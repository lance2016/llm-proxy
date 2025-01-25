# LLM API 网关

一个强大的大语言模型 API 网关，支持多个提供商的统一接口。

## 功能特点

- 🤖 支持多个 LLM 提供商
- 🔄 自动故障转移
- ⚡ 流式响应
- 🔒 速率限制
- 📊 使用统计

## 项目结构

```
.
├── app/                    # 应用源代码
│   ├── api/               # API 端点
│   ├── core/              # 核心功能
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic 模式
│   ├── services/          # 业务逻辑
│   │   └── providers/     # LLM 提供商
│   └── utils/             # 工具函数
├── docs/                  # 文档
├── scripts/               # 工具脚本
├── tests/                 # 测试用例
├── .env                   # 环境变量
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker 配置
├── docker-compose.yml    # Docker compose 配置
├── requirements.txt      # Python 依赖
└── README.md            # 项目文档
```

## 依赖要求

- Python 3.11+
- FastAPI 0.104.0+
- Pydantic 2.4.2+
- Pydantic-settings 2.0.3+
- HTTPX 0.25.0+
- 其他依赖请查看 `requirements.txt`

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/lance2016/llm-api-gateway.git
   cd llm-api-gateway
   ```

2. 复制环境文件并配置：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件设置你的配置
   ```

3. 使用 Docker 运行：
   ```bash
   docker-compose up -d --build
   ```

## 开发

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行开发服务器：
   ```bash
   uvicorn app.main:app --reload
   ```

## API 文档

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc
- OpenAPI JSON：http://localhost:8000/api/v1/openapi.json

## 添加新的提供商

1. 在 `app/services/providers/` 中创建新的提供商类
2. 继承 `OpenAIProvider` 以兼容 OpenAI 格式的 API
3. 重写必要的方法（如 `prepare_payload`）
4. 使用 `@LLMProviderFactory.register` 装饰器注册提供商

示例：
```python
@LLMProviderFactory.register("new_provider")
class NewProvider(OpenAIProvider):
    def prepare_payload(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        payload = super().prepare_payload(request)
        # 添加提供商特定的修改
        return payload
```

## 贡献

1. Fork 本仓库
2. 创建你的特性分支
3. 提交你的改动
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情

## 作者

- Lance (https://github.com/lance2016)
