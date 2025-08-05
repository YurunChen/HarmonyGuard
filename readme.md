<div align="center">
<img src="materials/icon.png" alt="HarmonyGuard Icon" width="150" height="150" style="vertical-align: middle;">

#  HarmonyGuard


### Toward Safety and Utility in Web Agents via Adaptive Policy Enhancement and Dual-Objective Optimization

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/your-username/HarmonyGuard)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&logo=opensourceinitiative&logoColor=black)](LICENSE)

*A multi-agent collaborative framework for balancing safety and utility in web environments*

📄 [Paper](#) 


</div>

---

## 📋 Table of Contents

- [HarmonyGuard](#harmonyguard)
    - [Toward Safety and Utility in Web Agents via Adaptive Policy Enhancement and Dual-Objective Optimization](#toward-safety-and-utility-in-web-agents-via-adaptive-policy-enhancement-and-dual-objective-optimization)
  - [📋 Table of Contents](#-table-of-contents)
  - [🎯 Overview](#-overview)
    - [🔧 Key Components](#-key-components)
    - [🎯 Core Capabilities](#-core-capabilities)
  - [🚀 Features](#-features)
  - [🏗️ Architecture](#️-architecture)
  - [⚙️ Installation](#️-installation)
    - [📋 Prerequisites](#-prerequisites)
    - [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
    - [2️⃣ Set Up Environment Variables](#2️⃣-set-up-environment-variables)
    - [3️⃣ Install Dependencies](#3️⃣-install-dependencies)
      - [🏆 For ST-WebAgentBench:](#-for-st-webagentbench)
      - [🐝 For WASP:](#-for-wasp)
    - [4️⃣ Website Deployment](#4️⃣-website-deployment)
  - [🔧 Configuration](#-configuration)
    - [🤖 Agent Configuration](#-agent-configuration)
    - [🔌 MCP Server Configuration](#-mcp-server-configuration)
    - [📝 Logging Configuration](#-logging-configuration)
  - [📊 Policy Processing](#-policy-processing)
  - [🧪 Evaluation](#-evaluation)
    - [ST-WebAgentBench](#st-webagentbench)
    - [WASP](#wasp)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [📞 Communication and Cooperation](#-communication-and-cooperation)
  - [📄 License](#-license)

---

## 🎯 Overview

Large language models enable agents to autonomously perform tasks in open web environments. However, as hidden threats within the web evolve, web agents face the challenge of balancing task performance with emerging risks during long-sequence operations. Although this challenge is critical, current research remains limited to single-objective optimization or single-turn scenarios, lacking the capability for collaborative optimization of both safety and utility in web environments.

To address this gap, we propose **HarmonyGuard**, a multi-agent collaborative framework that leverages policy enhancement and objective optimization to jointly improve both utility and safety. **HarmonyGuard** features a multi-agent architecture characterized by two fundamental capabilities:

### 🔧 Key Components

| Component | Description |
|-----------|-------------|
| **🛡️ Policy Agent** | LLM-based agent for processing and updating security policies |
| **⚡ Utility Agent** | Agent for implementing web agent reasoning evaluation and reasoning correction |
| **🔌 MCP Server** | Model Context Protocol Server, used for the agent tool calls |

### 🎯 Core Capabilities

1. **🔄 Adaptive Policy Enhancement**: We introduce the Policy Agent within **HarmonyGuard**, which automatically extracts and maintains structured security policies from unstructured external documents, while continuously updating policies in response to evolving threats.

2. **⚖️ Dual-Objective Optimization**: Based on the dual objectives of safety and utility, the Utility Agent integrated within **HarmonyGuard** performs the Markovian real-time reasoning to evaluate the objectives and utilizes metacognitive capabilities for their optimization.

> **📊 Performance**: Extensive evaluations on multiple benchmarks show that **HarmonyGuard** improves policy compliance by up to **38%** and task completion by up to **20%** over existing baselines, while achieving over **90%** policy compliance across all tasks.

---

## 🚀 Features

<div align="center">

| Feature | Description |
|---------|-------------|
| 🏆 **Multi-Benchmark Support** | Integrated evaluation with ST-WebAgentBench and WASP |
| 🛡️ **Policy-Aware Evaluation** | Six-dimensional safety assessment (User-Consent, Boundary, Strict Execution, Hierarchy, Robustness, Error Handling) |
| 🤖 **Multi-Model Support** | Compatible with OpenAI GPT models, Anthropic Claude, and Alibaba Qwen |
| 📄 **Automated Policy Processing** | PDF and webpage policy extraction capabilities |
| 📝 **Comprehensive Logging** | Detailed logging and thought process tracking |


</div>

---

## 🏗️ Architecture

```
HarmonyGuard/
├── 🛡️ harmony_agents/          # Core agent implementations
│   ├── policy_agent.py     # Policy processing agent
│   ├── utility_agent.py    # Utility functions agent
│   └── mcp_server.py       # MCP server implementation
├── 🏆 benchmark/              # Benchmark suites
│   ├── ST-WebAgentBench/   # ST-WebAgentBench benchmark
│   └── wasp/              # WASP benchmark
├── 🔧 utility/               # Utility modules
│   ├── config_loader.py   # Configuration management
│   ├── logger.py          # Logging utilities
│   └── tools.py           # Common tools
├── 📚 policy_docs/           # External Policy documentation
├── 📊 policy_processing_output/ # Structured policy outputs
└── 📈 output/               # Evaluation results
```

---

## ⚙️ Installation

### 📋 Prerequisites

- ✅ Python 3.10 or higher
- 🐳 Docker (for ST-WebAgentBench)
- ☁️ AWS EC2

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/HarmonyGuard.git
cd HarmonyGuard
```

### 2️⃣ Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic Configuration (for MCP Server)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Alibaba DashScope Configuration (for Utility Agent)
DASHSCOPE_API_KEY=your_dashscope_api_key
```

### 3️⃣ Install Dependencies

We tested the performance of **HarmonyGuard** on two benchmarks, and the environment configuration of the benchmarks is as follows.

#### 🏆 For ST-WebAgentBench:
```bash
chmod +x setup_stweb.sh
./setup_stweb.sh
```
This will create an environment named `harmonyguard-stweb` using conda.

#### 🐝 For WASP:
```bash
chmod +x setup_wasp.sh
./setup_stweb.sh
```
This will create an environment named `harmonyguard-wasp` using conda.

### 4️⃣ Website Deployment

Based on the following tutorial for deployment on AWS EC2:

- **ST-WebAgentBench**: 
  - [GitLab & ShoppingAdmin](https://github.com/web-arena-x/webarena/tree/main/environment_docker#pre-installed-amazon-machine-image-recommended)
  - [SuiteCRM](https://github.com/segev-shlomov/ST-WebAgentBench/blob/main/suitecrm_setup/README.md)

- **WASP**: [visualwebarena](https://github.com/facebookresearch/wasp/blob/main/visualwebarena/environment_docker/README.md)

> **⚠️ Notice**: If the ST-WebAgentBench website runs successfully, several website URLs need to be configured in `\benchmark\ST-WebAgentBench\.env`.

---

## 🔧 Configuration

The project uses `config.yaml` for configuration management. we present detailed explanation in [this](materials/config_explanation_en.md). Key configuration sections:

### 🤖 Agent Configuration
```yaml
openai:
  policy_agent:
    api_key: "${OPENAI_API_KEY}" # read from .env
    base_url: "${OPENAI_API_BASE}" # read from .env
    model: "gpt-4o"
    max_tokens: 2048
    temperature: 0
    ...
```

### 🔌 MCP Server Configuration
```yaml
mcp_server:
  anthropic:
    api_key: "${OPENAI_API_KEY}" # read from .env
     base_url: "${OPENAI_API_BASE}" # read from .env
    model: "gpt-4o"
    max_tokens: 20000
    temperature: 0
```

### 📝 Logging Configuration
```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(levelname)s - %(message)s"
  console:
    enabled: true
  file:
    enabled: false
    path: "logs"
```

---

## 📊 Policy Processing

To process the policy files located in the root directory, execute the following command:

```bash
cd harmony_agents
python policy_agent.py \
  -i /Users/yurunchen/project/python/HarmonyGuard_v2/policy_docs/wasp_risk.pdf \
  -org "organization" \
  -desc "Description of the policy files" \
  -subject "Agent"
```
✅ The processed results will be saved in the policy_processing_output directory.

Among the output files, the `xxx_policies.json` file is considered the parsed result. Use the path of this file to replace the placeholder in your configuration:
```
policy:
  risk_cat_path: "xxx_policies.json"
```
---

## 🧪 Evaluation

### ST-WebAgentBench

Run the following command in the root directory:

```bash
# Remember to set .env in ST-WebAgentBench
cd benchmark/ST-WebAgentBench
conda activate harmonyguard-stweb
python st_bench_loop.py # You can set the evaluation range in this file.
```

### WASP

Run WASP prompt injection tests:

```bash
cd benchmark/wasp/webarena_prompt_injections
conda activate harmonyguard-wasp
export DATASET=webarena_prompt_injections
export REDDIT="Put your Reddit website URL here."
export GITLAB="Put your Gitlab website URL here."
python run.py \
    --config configs/experiment_config.raw.json \
    --model gpt-4o \
    --system-prompt configs/system_prompts/wa_p_som_cot_id_actree_3s.json \
    --output-dir ../../../output/wasp/ \
    --output-format webarena
```

---

## 🙏 Acknowledgments

<div align="center">

| Project | Description |
|---------|-------------|
| **ST-WebAgentBench** | For the safety and trustworthiness evaluation framework |
| **WASP** | For the web agent security benchmark |
| **BrowserGym** | For the web automation infrastructure |
| **OpenAI** | For GPT model APIs |
| **Anthropic** | For Claude model APIs |
| **Alibaba** | For Qwen model APIs |

</div>

---

## 📞 Communication and Cooperation

For questions, issues, or contributions:

- 📧 **Email**: yurunchen.research@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/HarmonyGuard/issues)

---

## 📄 License

This project is licensed under the MIT License.

