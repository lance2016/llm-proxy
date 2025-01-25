# LLM API Gateway

A FastAPI-based API gateway for multiple LLM providers (OpenAI, Anthropic, DeepSeek).

## Features

- 🚀 Multiple LLM Provider Support
  - OpenAI
  - Anthropic
  - DeepSeek
  - Easily extensible for more providers

- 🔄 Unified API Interface
  - Compatible with OpenAI's chat completion API
  - Streaming support
  - Automatic provider selection based on model name

- 🔍 Advanced Logging System
  - JSON structured logging
  - Request tracing with trace_id
  - Colored console output
  - Log rotation
  - Docker-friendly logging

- 🛡️ Built-in Security
  - Rate limiting
  - API key validation
  - CORS protection
  - Production-ready security checks

- 🎯 Production Ready
  - Health checks
  - Docker support
  - Environment-based configuration
  - Comprehensive error handling

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-api-gateway
```

2. Create and configure your `.env` file:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

3. Start the service:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`.

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

3. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `DEBUG`: Enable debug mode (default: false)
- `ENV`: Environment (development/production)
- `FORCE_COLOR`: Enable colored logging output (default: true)

### Rate Limiting

- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: true)
- `RATE_LIMIT_REQUESTS`: Number of requests allowed (default: 100)
- `RATE_LIMIT_PERIOD`: Time window in seconds (default: 60)

### Logging

- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_DIR`: Log directory (default: logs)
- `LOG_MAX_BYTES`: Maximum log file size (default: 10MB)
- `LOG_BACKUP_COUNT`: Number of backup files (default: 5)

## API Documentation

Once running, visit:
- OpenAPI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/v1/chat/completions`: Chat completion endpoint
  - Compatible with OpenAI's chat completion API
  - Supports streaming responses
  - Automatic provider selection based on model prefix

## Development

### Project Structure

```
app/
├── api/
│   └── v1/
│       └── endpoints.py
├── core/
│   ├── config/
│   │   └── settings.py
│   ├── middleware/
│   │   ├── rate_limit.py
│   │   └── request_logging.py
│   ├── providers/
│   │   └── http_client.py
│   ├── context.py
│   ├── exceptions.py
│   ├── handlers.py
│   └── logging_config.py
├── services/
│   └── chat/
│       └── service.py
└── main.py
```

### Adding a New Provider

1. Create a new provider class in `app/core/providers/`
2. Implement the required interface methods
3. Add provider configuration in `settings.py`
4. Register the provider in `PROVIDER_CONFIGS`

## Docker Support

### Build Image
```bash
docker build -t llm-api-gateway .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -v ./logs:/app/logs \
  --env-file .env \
  llm-api-gateway
```

### Docker Compose
```bash
docker-compose up -d
```

## Logging

The application uses a sophisticated logging system with:

- JSON structured logging for file output
- Colored console output (configurable via `FORCE_COLOR`)
- Request tracing with `trace_id`
- Automatic log rotation
- Docker-friendly logging configuration

### Log Formats

- Console: Colored, human-readable format
- File: JSON format with additional metadata

Example console output:
```
2024-01-25 10:30:45 [INFO] app.main: Server started
2024-01-25 10:30:46 [INFO] app.api: Request received [trace_id: abc-123]
```

Example JSON log:
```json
{
  "trace_id": "abc-123",
  "timestamp": "2024-01-25T10:30:45",
  "level": "INFO",
  "logger": "app.main",
  "message": "Server started"
}
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)
