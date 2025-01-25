import logging
import os
from datetime import datetime
import json
from logging.handlers import RotatingFileHandler
import httpx
import sys
from .context import get_request_id
from .middleware.request_logging import request_id_var

# Environment variable to control color output
FORCE_COLOR = os.getenv('FORCE_COLOR', '1').lower() in ('1', 'true', 'yes', 'on')

# ANSI color codes
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[31;1m', # Bright Red
    'RESET': '\033[0m'       # Reset
}

class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output"""
    
    def __init__(self, fmt=None, datefmt=None, force_color=FORCE_COLOR):
        super().__init__(fmt, datefmt)
        self.default_formatter = logging.Formatter(fmt, datefmt)
        self.force_color = force_color
    
    def format(self, record):
        # Save original values
        orig_levelname = record.levelname
        orig_msg = record.msg
        
        # Add color if forced or going to a terminal
        if self.force_color or sys.stdout.isatty():
            color = COLORS.get(record.levelname, '')
            if color:
                # Color the level name
                record.levelname = f"{color}{record.levelname}{COLORS['RESET']}"
                # Color the message
                if isinstance(record.msg, str):
                    record.msg = f"{color}{record.msg}{COLORS['RESET']}"
        
        # Format the record
        result = self.default_formatter.format(record)
        
        # Restore original values
        record.levelname = orig_levelname
        record.msg = orig_msg
        
        return result

class JsonFormatter(logging.Formatter):
    """JSON formatter that puts trace_id at the beginning"""
    def format(self, record):
        # Create the log entry with trace_id first
        log_entry = {
            "trace_id": getattr(record, "trace_id", "-"),
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }

        # Add extra fields if they exist
        if hasattr(record, "request"):
            log_entry["request"] = record.request
        if hasattr(record, "response"):
            log_entry["response"] = record.response
        if record.exc_info:
            log_entry["exc_info"] = self.formatException(record.exc_info)
        
        # Add any extra attributes from record
        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        return json.dumps(log_entry)

class TraceIDFilter(logging.Filter):
    """Filter that adds trace_id to log records"""
    def filter(self, record):
        # Always try to get trace_id from context first
        trace_id = request_id_var.get(None)  # Use None as default
        if trace_id:
            record.trace_id = trace_id
            return True
            
        # Try to get from record attributes
        if hasattr(record, 'trace_id'):
            return True
            
        # Try to get from args if it's a httpx log
        if record.name == 'httpx':
            if hasattr(record, 'args') and isinstance(record.args, tuple):
                # Try to extract trace_id from request/response headers
                for arg in record.args:
                    if isinstance(arg, (httpx.Request, httpx.Response)):
                        trace_id = arg.headers.get('x-request-id')
                        if trace_id:
                            record.trace_id = trace_id
                            return True
        
        # Use request ID from our context as last resort
        record.trace_id = get_request_id() or "-"
        return True

def create_colored_formatter() -> logging.Formatter:
    """Create a colored formatter for console output"""
    return ColoredFormatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def setup_logging(
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_level: int = logging.INFO
) -> None:
    """Setup application logging
    
    Args:
        log_dir: Directory to store log files
        max_bytes: Maximum size of each log file
        backup_count: Number of backup files to keep
        log_level: Logging level
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Remove all existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure root logger
    root_logger.setLevel(log_level)

    # Configure httpx logger
    httpx_logger = logging.getLogger('httpx')
    httpx_logger.setLevel(log_level)
    httpx_logger.propagate = False  # Don't propagate to root logger

    # Add trace ID filter to root logger and httpx logger
    trace_filter = TraceIDFilter()
    root_logger.addFilter(trace_filter)
    httpx_logger.addFilter(trace_filter)

    # Configure handlers
    handlers = []

    # File handler with rotation (using JSON formatter)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(JsonFormatter())
    handlers.append(file_handler)

    # Console handler (using colored formatter)
    console_handler = logging.StreamHandler(sys.stdout)  # Use stdout instead of stderr
    console_handler.setFormatter(create_colored_formatter())
    handlers.append(console_handler)

    # Add handlers to root logger and httpx logger
    for handler in handlers:
        root_logger.addHandler(handler)
        httpx_logger.addHandler(handler)

    # Log startup message
    root_logger.info("Logging system initialized", extra={
        "log_dir": log_dir,
        "max_bytes": max_bytes,
        "backup_count": backup_count,
        "log_level": logging.getLevelName(log_level)
    }) 