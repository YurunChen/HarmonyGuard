# HarmonyGuard Configuration File Guide

This document explains in detail the purpose and configuration options of each section in the `config.yaml` file.

## File Structure Overview

```yaml
config.yaml
├── openai/                    # OpenAI API Configuration
│   ├── policy_agent/         # Policy Agent Configuration
│   ├── utility_agent/        # Utility Agent Configuration
│   ├── wasp/                 # WASP Benchmark Configuration
│   └── st_webagentbench/     # ST-WebAgentBench Configuration
├── mcp_server/               # MCP Server Configuration
├── policy/                   # Policy Database Configuration
└── logging/                  # Logging System Configuration
```

## 1. OpenAI Configuration (`openai`)

### 1.1 Policy Agent Configuration (`policy_agent`)

```yaml
policy_agent:
  api_key: "${OPENAI_API_KEY}"      # OpenAI API key
  base_url: "${OPENAI_API_BASE}"    # API base URL
  timeout: 30.0                     # Request timeout (seconds)
  model: "gpt-4o"                   # Model name used
  max_tokens: 2048                  # Maximum number of generated tokens
  temperature: 0                    # Generation temperature (0=deterministic, 1=random)
```

**Purpose**: Configures the OpenAI API parameters used by the policy agent to parse and generate policy documents.

### 1.2 Utility Agent Configuration (`utility_agent`)

```yaml
utility_agent:
  api_key: "${DASHSCOPE_API_KEY}"   # Alibaba Cloud DashScope API key
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  timeout: 30.0
  model: "qwen-max-2025-01-25"
  max_tokens: 2048
  temperature: 0
```

**Purpose**: Configures the DashScope API parameters used by the utility agent for safety alignment checks and risk assessments.

### 1.3 WASP Benchmark Configuration (`wasp`)

```yaml
wasp:
  api_key: "${OPENAI_API_KEY}"
  base_url: "${OPENAI_API_BASE}"
  timeout: 30.0
  model: "gpt-4o-mini"
  max_tokens: 2048
  temperature: 0
```

**Purpose**: Configures the API parameters used for the WASP (Web Agent Safety Protocol) benchmark tests.

### 1.4 ST-WebAgentBench Configuration (`st_webagentbench`)

```yaml
st_webagentbench:
  api_key: "${OPENAI_API_KEY}"
  base_url: "${OPENAI_API_BASE}"
  timeout: 30.0
  model: "gpt-4o-mini"
  max_tokens: 2048
  temperature: 0
```

**Purpose**: Configures the API parameters used for the ST-WebAgentBench benchmark tests.

## 2. MCP Server Configuration (`mcp_server`)

```yaml
mcp_server:
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    base_url: "https://api.openai-proxy.org/anthropic"
    model: "claude-3-7-sonnet-20250219"
    max_tokens: 20000
    temperature: 0.2
  http_timeout: 15.0
  client_session_timeout: 60.0
```

**Purpose**: Configures the MCP (Model Context Protocol) server parameters for communication with the Claude model.

## 3. Policy Database Configuration (`policy`)

```yaml
policy:
  risk_cat_path: "/Users/yurunchen/project/python/HarmonyGuard_v2/policy_processing_output/process_20250804_041851/wasp_policies.json"
```

**Purpose**: Specifies the path to the policy database file, which contains safety policies and risk assessment rules.

## 4. Logging System Configuration (`logging`)

### 4.1 Global Logging Configuration

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

### 4.2 Console Logging Configuration

```yaml
console:
  enabled: true
  level: "INFO"
  format: "%(asctime)s - %(levelname)s - %(message)s"
```

### 4.3 File Logging Configuration

```yaml
file:
  enabled: false
  level: "DEBUG"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
  path: "logs"
  max_size: "10MB"
  backup_count: 5
```

### 4.4 Module-Specific Logging Configuration

```yaml
logger_configs:
  harmony_agents:
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  benchmark:
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  utility:
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Environment Variables

The following environment variables are used:

- `${OPENAI_API_KEY}`: OpenAI API key  
- `${OPENAI_API_BASE}`: OpenAI API base URL  
- `${DASHSCOPE_API_KEY}`: Alibaba Cloud DashScope API key  
- `${ANTHROPIC_API_KEY}`: Anthropic API key  

These variables should be defined in your system environment or in a `.env` file.

## Log Level Definitions

- `DEBUG`: Debug information; most detailed level
- `INFO`: General info; runtime state
- `WARNING`: Warnings; not fatal, but notable
- `ERROR`: Errors; execution problems
- `CRITICAL`: Critical errors; may halt the program

## Configuration Best Practices

1. **API Key Security**: Use environment variables for API keys. Never hard-code them.
2. **Log Levels**: Use `INFO` in production, `DEBUG` in development.
3. **Timeout Settings**: Adjust based on network conditions.
4. **Model Choice**: Choose the right model to balance performance and cost.
5. **File Paths**: Use absolute or project-root-relative paths.

## Config File Loading

The system uses `utility/config_loader.py` to load configuration, supporting:

- Environment variable substitution  
- Auto-discovery of configuration file path  
- Configuration validation and error handling  