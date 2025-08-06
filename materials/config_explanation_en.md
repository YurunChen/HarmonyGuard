# HarmonyGuard Configuration File Guide

This document explains in detail the purpose and configuration options of each section in the `config.yaml` file.

## Configuration File Structure

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
  api_key: "${OPENAI_API_KEY}"      # OpenAI API key
  base_url: "${OPENAI_API_BASE}"    # API base URL
  timeout: 30.0                     # Request timeout (seconds)
  model: "gpt-4o"                   # Model name used
  max_tokens: 2048                  # Maximum number of generated tokens
  temperature: 0                    # Generation temperature (0=deterministic, 1=random)
```

**Purpose**: Configures the OpenAI API parameters used by the utility agent for safety alignment checks and risk assessments.

### 1.3 WASP Benchmark Configuration (`wasp`)

```yaml
wasp:
  api_key: "${OPENAI_API_KEY}"      # OpenAI API key
  base_url: "${OPENAI_API_BASE}"    # API base URL
  timeout: 30.0                     # Request timeout (seconds)
  model: "gpt-4o"                   # Model name used
  max_tokens: 2048                  # Maximum number of generated tokens
  temperature: 0                    # Generation temperature (0=deterministic, 1=random)
```

**Purpose**: Configures the API parameters used for the WASP (Web Agent Safety Protocol) benchmark tests.

### 1.4 ST-WebAgentBench Configuration (`st_webagentbench`)

```yaml
st_webagentbench:
  api_key: "${OPENAI_API_KEY}"      # OpenAI API key
  base_url: "${OPENAI_API_BASE}"    # API base URL
  timeout: 30.0                     # Request timeout (seconds)
  model: "gpt-4o"                   # Model name used
  max_tokens: 2048                  # Maximum number of generated tokens
  temperature: 0                    # Generation temperature (0=deterministic, 1=random)
```

**Purpose**: Configures the API parameters used for the ST-WebAgentBench benchmark tests.

## 2. MCP Server Configuration (`mcp_server`)

```yaml
mcp_server:
  openai:
    api_key: "${OPENAI_API_KEY}"    # OpenAI API key
    base_url: "${OPENAI_API_BASE}"  # API base URL
    model: "gpt-4o"                 # Model name used
    max_tokens: 8000                # Maximum number of generated tokens
    temperature: 0                  # Generation temperature
  http_timeout: 15.0               # HTTP request timeout (seconds)
  client_session_timeout: 60.0     # Client session timeout (seconds)
```

**Purpose**: Configures the MCP (Model Context Protocol) server parameters for communication with the OpenAI model.

## 3. Policy Database Configuration (`policy`)

```yaml
policy:
  risk_cat_path: "put your processed policy file path here"
```

**Purpose**: Specifies the path to the policy database file, which contains safety policies and risk assessment rules. Replace the placeholder with the actual path to your processed policy file (e.g., `policy_processing_output/xxx_policies.json`).

## 4. Logging System Configuration (`logging`)

### 4.1 Global Logging Configuration

```yaml
logging:
  level: "INFO"                    # Global log level
  format: "%(asctime)s - %(levelname)s - %(message)s"  # Log message format
  date_format: "%Y-%m-%d %H:%M:%S" # Date format for timestamps
```

### 4.2 Console Logging Configuration

```yaml
console:
  enabled: true                    # Enable console logging
  level: "INFO"                    # Console log level
  format: "%(asctime)s - %(levelname)s - %(message)s"  # Console message format
```

### 4.3 File Logging Configuration

```yaml
file:
  enabled: false                   # Disable file logging by default
  level: "DEBUG"                   # File log level
  format: "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"  # File message format
  path: "logs"                     # Log file directory
  max_size: "10MB"                 # Maximum log file size
  backup_count: 5                  # Number of backup log files to keep
```

### 4.4 Module-Specific Logging Configuration

```yaml
logger_configs:
  harmony_agents:                  # Logging configuration for harmony_agents module
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  benchmark:                       # Logging configuration for benchmark module
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  utility:                         # Logging configuration for utility module
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Environment Variables

The following environment variables are used:

- `${OPENAI_API_KEY}`: OpenAI API key  
- `${OPENAI_API_BASE}`: OpenAI API base URL  

These variables should be defined in your system environment or in a `.env` file.

## Log Level Definitions

- `DEBUG`: Debug information; most detailed level
- `INFO`: General info; runtime state
- `WARNING`: Warnings; not fatal, but notable
- `ERROR`: Errors; execution problems
- `CRITICAL`: Critical errors; may halt the program

## Config File Loading

The system uses `utility/config_loader.py` to load configuration, supporting:

- Environment variable substitution  
- Auto-discovery of configuration file path  
- Configuration validation and error handling

## Related Documentation

- **Main README**: [README.md](../readme.md) - Project overview and setup instructions
- **Evaluation Guide**: [evaluate/README.md](../evaluate/README.md) - Detailed instructions for using evaluation tools
- **Configuration Examples**: See the `config.yaml` file in the root directory for complete configuration examples 