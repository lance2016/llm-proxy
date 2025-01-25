# LLM API Gateway

[中文文档](README_CN.md)

A unified async FastAPI gateway for various LLM providers with OpenAI-compatible interface. This project provides a standardized way to interact with different LLM providers through a single API interface.

## Features

- Async support for all endpoints
- OpenAI-compatible interface
- Streaming and non-streaming support
- Easy to extend for new LLM providers
- Clean and elegant design using Factory and Adapter patterns
- HTTP-based communication with LLM providers
- Standardized error handling
- Type safety with Pydantic models

## Project Structure

```
app/
├── api/            # API routes and endpoints
├── core/           # Core configurations
├── models/         # Database models (if needed)
├── schemas/        # Pydantic models for request/response
├── services/       # LLM provider implementations
│   ├── providers/  # Concrete provider implementations
│   └── base.py     # Abstract base classes and factory
└── utils/          # Utility functions
```

## Supported Providers

Currently supported LLM providers:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Deepseek

## Dependencies

- Python 3.11+
- FastAPI 0.104.0+
- Pydantic 2.4.2+
- Pydantic-settings 2.0.3+
- HTTPX 0.25.0+
- Other dependencies listed in `requirements.txt`

## Setup

### Option 1: Local Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_key_here
ANTHROPIC_API_BASE=https://api.anthropic.com

# Deepseek API Configuration
DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

### Option 2: Docker Setup

1. Create a `.env` file with your API keys (same as above)

2. Build and start the service using Docker Compose:
```bash
docker-compose up -d --build
```

3. Check the service status:
```bash
docker-compose ps
```

4. View logs:
```bash
docker-compose logs -f
```

5. Stop the service:
```bash
docker-compose down
```

6. Rebuild and restart (after code changes):
```bash
docker-compose up -d --build
```

## Running the Server

```bash
uvicorn app.main:app --reload
```

## API Usage

### Basic Chat Completion

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {"role": "user", "content": "Hello!"}
       ]
     }'
```

### Streaming Chat Completion

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -N \
     -d '{
       "model": "deepseek-chat",
       "messages": [
         {"role": "user", "content": "Hello!"}
       ],
       "stream": true
     }'
```

### Model Prefix Mapping

The provider is automatically selected based on the model prefix:
- `gpt-*`: OpenAI provider
- `anthropic-*`: Anthropic provider
- `deepseek-*`: Deepseek provider

## Adding New Providers

1. Create a new provider class in `app/services/providers/`:
```python
@LLMProviderFactory.register("your_provider")
class YourProvider(LLMProvider):
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        # Implement non-streaming chat completion
        pass
    
    async def chat_completion_stream(
        self, 
        request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        # Implement streaming chat completion
        pass
    
    def prepare_headers(self) -> Dict[str, str]:
        # Prepare request headers
        pass
    
    def prepare_payload(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        # Convert request to provider format
        pass
    
    def process_response(self, response: Dict[str, Any]) -> ChatCompletionResponse:
        # Convert provider response to standard format
        pass
    
    async def process_stream_response(
        self, 
        response: httpx.Response
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        # Process streaming response
        pass
```

2. Add provider configuration in `app/core/config.py`:
```python
# Your Provider Endpoints
YOUR_PROVIDER_API_KEY: str = ""
YOUR_PROVIDER_API_BASE: str = "https://api.your-provider.com/v1"

# Add to PROVIDER_CONFIGS
PROVIDER_CONFIGS: Dict[str, Dict[str, str]] = {
    "your-prefix": {
        "provider": "your_provider",
        "api_key": "YOUR_PROVIDER_API_KEY",
        "api_base": "YOUR_PROVIDER_API_BASE"
    }
}
```

3. Import your provider in `app/services/providers/__init__.py`

## Error Handling

The API provides standardized error responses:
- 400: Bad Request (invalid input)
- 401: Unauthorized (invalid API key)
- 404: Not Found (invalid endpoint)
- 500: Internal Server Error

## Development

- Use `black` for code formatting
- Use `isort` for import sorting
- Use `mypy` for type checking
- Follow PEP 8 style guidelines

## License

MIT
