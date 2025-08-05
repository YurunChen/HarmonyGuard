# HarmonyGuard_v2 配置文件说明

本文档详细解释了 `config.yaml` 配置文件中各个部分的作用和配置选项。

## 文件结构概览

```yaml
config.yaml
├── openai/                    # OpenAI API 配置
│   ├── policy_agent/         # 策略代理配置
│   ├── utility_agent/        # 工具代理配置
│   ├── wasp/                 # WASP基准测试配置
│   └── st_webagentbench/     # ST-WebAgentBench配置
├── mcp_server/               # MCP服务器配置
├── policy/                   # 策略数据库配置
└── logging/                  # 日志系统配置
```

## 1. OpenAI 配置 (openai)

### 1.1 策略代理配置 (policy_agent)
```yaml
policy_agent:
  api_key: "${OPENAI_API_KEY}"      # OpenAI API密钥
  base_url: "${OPENAI_API_BASE}"    # API基础URL
  timeout: 30.0                     # 请求超时时间（秒）
  model: "gpt-4o"                   # 使用的模型名称
  max_tokens: 2048                  # 最大生成token数
  temperature: 0                    # 生成温度（0=确定性，1=随机性）
```

**作用**: 配置策略代理使用的OpenAI API参数，用于处理策略文档的解析和生成。

### 1.2 工具代理配置 (utility_agent)
```yaml
utility_agent:
  api_key: "${DASHSCOPE_API_KEY}"   # 阿里云DashScope API密钥
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"  # DashScope API地址
  timeout: 30.0                     # 请求超时时间（秒）
  model: "qwen-max-2025-01-25"      # 通义千问模型
  max_tokens: 2048                  # 最大生成token数
  temperature: 0                    # 生成温度
```

**作用**: 配置工具代理使用的阿里云DashScope API参数，用于安全对齐检查和风险评估。

### 1.3 WASP基准测试配置 (wasp)
```yaml
wasp:
  api_key: "${OPENAI_API_KEY}"      # OpenAI API密钥
  base_url: "${OPENAI_API_BASE}"    # API基础URL
  timeout: 30.0                     # 请求超时时间（秒）
  model: "gpt-4o-mini"              # 使用的模型名称
  max_tokens: 2048                  # 最大生成token数
  temperature: 0                    # 生成温度
```

**作用**: 配置WASP (Web Agent Safety Protocol) 基准测试使用的API参数。

### 1.4 ST-WebAgentBench配置 (st_webagentbench)
```yaml
st_webagentbench:
  api_key: "${OPENAI_API_KEY}"      # OpenAI API密钥
  base_url: "${OPENAI_API_BASE}"    # API基础URL
  timeout: 30.0                     # 请求超时时间（秒）
  model: "gpt-4o-mini"              # 使用的模型名称
  max_tokens: 2048                  # 最大生成token数
  temperature: 0                    # 生成温度
```

**作用**: 配置ST-WebAgentBench基准测试使用的API参数。

## 2. MCP服务器配置 (mcp_server)

```yaml
mcp_server:
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"                    # Anthropic API密钥
    base_url: "https://api.openai-proxy.org/anthropic" # Anthropic API代理地址
    model: "claude-3-7-sonnet-20250219"                # Claude模型版本
    max_tokens: 20000                                  # 最大生成token数
    temperature: 0.2                                   # 生成温度
  http_timeout: 15.0                                   # HTTP请求超时时间
  client_session_timeout: 60.0                         # 客户端会话超时时间
```

**作用**: 配置MCP (Model Context Protocol) 服务器参数，用于与Claude模型进行通信。

## 3. 策略数据库配置 (policy)

```yaml
policy:
  risk_cat_path: "/Users/yurunchen/project/python/HarmonyGuard_v2/policy_processing_output/process_20250804_041851/wasp_policies.json"
```

**作用**: 指定策略数据库文件的路径，包含安全策略和风险评估规则。

## 4. 日志系统配置 (logging)

### 4.1 全局日志配置
```yaml
logging:
  level: "INFO"                     # 全局日志级别
  format: "%(asctime)s - %(levelname)s - %(message)s"  # 全局日志格式
  date_format: "%Y-%m-%d %H:%M:%S"  # 日期时间格式
```

### 4.2 控制台日志配置
```yaml
console:
  enabled: true                     # 是否启用控制台输出
  level: "INFO"                     # 控制台日志级别
  format: "%(asctime)s - %(levelname)s - %(message)s"  # 控制台日志格式
```

### 4.3 文件日志配置
```yaml
file:
  enabled: false                    # 是否启用文件输出,日志保存在logs目录下
  level: "DEBUG"                    # 文件日志级别
  format: "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"  # 文件日志格式
  path: "logs"                      # 日志文件目录
  max_size: "10MB"                  # 单个日志文件最大大小
  backup_count: 5                   # 保留的日志文件数量
```

### 4.4 模块特定日志配置
```yaml
logger_configs:
  harmony_agents:                   # harmony_agents模块日志配置
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  benchmark:                        # benchmark模块日志配置
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  utility:                          # utility模块日志配置
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 环境变量说明

配置文件中使用了以下环境变量：

- `${OPENAI_API_KEY}`: OpenAI API密钥
- `${OPENAI_API_BASE}`: OpenAI API基础URL
- `${DASHSCOPE_API_KEY}`: 阿里云DashScope API密钥
- `${ANTHROPIC_API_KEY}`: Anthropic API密钥

这些环境变量需要在系统环境或 `.env` 文件中设置。

## 日志级别说明

- `DEBUG`: 调试信息，最详细的日志级别
- `INFO`: 一般信息，记录程序运行状态
- `WARNING`: 警告信息，不影响程序运行但需要注意
- `ERROR`: 错误信息，程序运行出现问题
- `CRITICAL`: 严重错误，程序可能无法继续运行


## 配置文件加载

系统使用 `utility/config_loader.py` 模块加载配置文件，支持：
- 环境变量替换
- 配置文件路径自动发现
- 配置验证和错误处理 