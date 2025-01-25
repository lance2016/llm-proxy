# LLM API 网关

一个统一的异步 FastAPI 网关，用于对接各种大语言模型提供商，提供 OpenAI 兼容的接口。本项目提供了一个标准化的方式来通过单一的 API 接口与不同的 LLM 提供商进行交互。

## 特性

- 所有端点都支持异步
- OpenAI 兼容的接口
- 支持流式和非流式输出
- 易于扩展新的 LLM 提供商
- 使用工厂模式和适配器模式的清晰优雅设计
- 基于 HTTP 的通信方式
- 标准化的错误处理
- 使用 Pydantic 模型确保类型安全

## 项目结构

```
app/
├── api/            # API 路由和端点
├── core/           # 核心配置
├── models/         # 数据库模型（如需要）
├── schemas/        # Pydantic 请求/响应模型
├── services/       # LLM 提供商实现
│   ├── providers/  # 具体提供商实现
│   └── base.py     # 抽象基类和工厂
└── utils/          # 工具函数
```

## 支持的提供商

目前支持的 LLM 提供商：
- OpenAI（GPT 模型）
- Anthropic（Claude 模型）
- Deepseek

## 安装设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows 上使用：venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 创建 `.env` 文件并配置 API 密钥：
```env
# OpenAI API 配置
OPENAI_API_KEY=你的_openai_密钥
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic API 配置
ANTHROPIC_API_KEY=你的_anthropic_密钥
ANTHROPIC_API_BASE=https://api.anthropic.com

# Deepseek API 配置
DEEPSEEK_API_KEY=你的_deepseek_密钥
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

## 运行服务器

```bash
uvicorn app.main:app --reload
```

## API 使用

### 基础聊天补全

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {"role": "user", "content": "你好！"}
       ]
     }'
```

### 流式聊天补全

```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -N \
     -d '{
       "model": "deepseek-chat",
       "messages": [
         {"role": "user", "content": "用中文写一个故事"}
       ],
       "stream": true
     }'
```

### 模型前缀映射

系统会根据模型前缀自动选择对应的提供商：
- `gpt-*`：使用 OpenAI 提供商
- `anthropic-*`：使用 Anthropic 提供商
- `deepseek-*`：使用 Deepseek 提供商

## 添加新的提供商

1. 在 `app/services/providers/` 中创建新的提供商类：
```python
@LLMProviderFactory.register("your_provider")
class YourProvider(LLMProvider):
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        # 实现非流式聊天补全
        pass
    
    async def chat_completion_stream(
        self, 
        request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        # 实现流式聊天补全
        pass
    
    def prepare_headers(self) -> Dict[str, str]:
        # 准备请求头
        pass
    
    def prepare_payload(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        # 转换请求为提供商格式
        pass
    
    def process_response(self, response: Dict[str, Any]) -> ChatCompletionResponse:
        # 转换提供商响应为标准格式
        pass
    
    async def process_stream_response(
        self, 
        response: httpx.Response
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        # 处理流式响应
        pass
```

2. 在 `app/core/config.py` 中添加提供商配置：
```python
# 你的提供商端点
YOUR_PROVIDER_API_KEY: str = ""
YOUR_PROVIDER_API_BASE: str = "https://api.your-provider.com/v1"

# 添加到 PROVIDER_CONFIGS
PROVIDER_CONFIGS: Dict[str, Dict[str, str]] = {
    "your-prefix": {
        "provider": "your_provider",
        "api_key": "YOUR_PROVIDER_API_KEY",
        "api_base": "YOUR_PROVIDER_API_BASE"
    }
}
```

3. 在 `app/services/providers/__init__.py` 中导入你的提供商

## 错误处理

API 提供标准化的错误响应：
- 400：错误请求（无效输入）
- 401：未授权（无效的 API 密钥）
- 404：未找到（无效的端点）
- 500：内部服务器错误

## 开发指南

- 使用 `black` 进行代码格式化
- 使用 `isort` 进行导入排序
- 使用 `mypy` 进行类型检查
- 遵循 PEP 8 风格指南

## 许可证

MIT 