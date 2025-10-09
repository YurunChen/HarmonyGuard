<div align="center">
<img src="materials/icon.png" alt="HarmonyGuard Icon" width="150" height="150" style="vertical-align: middle;">

#  HarmonyGuard


### Toward Safety and Utility in Web Agents via Adaptive Policy Enhancement and Dual-Objective Optimization

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/YurunChen/HarmonyGuard)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&logo=opensourceinitiative&logoColor=black)](LICENSE)

*A multi-agent collaborative framework for balancing safety and utility in web environments*

📄 [Paper](https://arxiv.org/abs/2508.04010) | 🤗 [HuggingFace](https://huggingface.co/papers/2508.04010) | 🐦 [X (Twitter)](https://x.com/YRChen_AIsafety/status/1953745222258897305)


</div>

---

## 📋 Table of Contents

- [HarmonyGuard](#harmonyguard)
    - [Toward Safety and Utility in Web Agents via Adaptive Policy Enhancement and Dual-Objective Optimization](#toward-safety-and-utility-in-web-agents-via-adaptive-policy-enhancement-and-dual-objective-optimization)
  - [📋 Table of Contents](#-table-of-contents)
  - [🎯 Overview](#-overview)
    - [🔧 Key Components](#-key-components)
    - [🎯 Core Capabilities](#-core-capabilities)
    - [🌟 Citiation](#-citiation)
  - [🚀 Features](#-features)
  - [🏗️ Architecture](#️-architecture)
  - [⚙️ Installation](#️-installation)
    - [📋 Prerequisites](#-prerequisites)
    - [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
    - [2️⃣ Set Up Environment Variables](#2️⃣-set-up-environment-variables)
    - [3️⃣ Install Dependencies](#3️⃣-install-dependencies)
      - [🏆 For ST-WebAgentBench](#-for-st-webagentbench)
      - [🐝 For WASP](#-for-wasp)
    - [4️⃣ Website Deployment](#4️⃣-website-deployment)
  - [🔧 Configuration](#-configuration)
    - [🤖 Agent Configuration](#-agent-configuration)
    - [🔌 MCP Server Configuration](#-mcp-server-configuration)
    - [📝 Logging Configuration](#-logging-configuration)
  - [📊 Policy Processing](#-policy-processing)
  - [🐝 Running](#-running)
    - [ST-WebAgentBench](#st-webagentbench)
    - [WASP](#wasp)
    - [Result Saved](#result-saved)
    - [Notice](#notice)
  - [🧪 Evaluation](#-evaluation)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [📞 Contact](#-contact)
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

### 🌟 Citiation
If you find our work valuable for your research or applications, we would greatly appreciate a star ⭐ and a citation using the BibTeX entry provided below.
```
@misc{chen2025harmonyguardsafetyutilityweb,
      title={HarmonyGuard: Toward Safety and Utility in Web Agents via Adaptive Policy Enhancement and Dual-Objective Optimization}, 
      author={Yurun Chen and Xavier Hu and Yuhan Liu and Keting Yin and Juncheng Li and Zhuosheng Zhang and Shengyu Zhang},
      year={2025},
      eprint={2508.04010},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2508.04010}, 
}
```

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
├── 📈 output/               # Evaluation results
│   ├── stweb/             # ST-WebAgentBench results
│   └── wasp/              # WASP results
├── 📊 evaluate/              # Evaluation tools
│   ├── evaluate_wasp.py   # WASP evaluation tool
│   ├── evaluate_stweb.py  # ST-Web evaluation tool
│   ├── Results/           # Evaluation results directory
│   │   ├── WASP/         # WASP results to be evluated
│   │   └── stweb/        # ST-Web results to be evluated
│   └── README.md         # Evaluation documentation
└── 📝 materials/            # Project materials
    ├── icon.png          # Project icon
    └── config_explanation_en.md # Configuration documentation
```

---

## ⚙️ Installation

### 📋 Prerequisites

- ✅ Python 3.10 or higher
- 🐳 Docker (for ST-WebAgentBench)
- ☁️ AWS EC2

### 1️⃣ Clone the Repository

```bash
git clone git@github.com:YurunChen/HarmonyGuard.git
cd HarmonyGuard
```

### 2️⃣ Set Up Environment Variables

Then edit the `env.example` file with your actual API keys:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=your_openai_base_url_here

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_API_BASE=your_anthropic_base_url_here

# Alibaba DashScope Configuration
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DASHSCOPE_API_BASE=your_dashscope_base_url_here
```
Copy the example environment file and configure it:

```bash
cp env.example .env
```

### 3️⃣ Install Dependencies

We evaluated the performance of HarmonyGuard on two benchmarks. The benchmark environments were set up using two scripts, with each environment created via conda.

#### 🏆 For ST-WebAgentBench
```bash
chmod +x setup_stweb.sh
./setup_stweb.sh
```
This will create an environment named `harmonyguard-stweb` using conda.

#### 🐝 For WASP
```bash
chmod +x setup_wasp.sh
./setup_wasp.sh
```
This will create an environment named `harmonyguard-wasp` using conda.

### 4️⃣ Website Deployment

Based on the following tutorial for deployment on AWS EC2:

- **ST-WebAgentBench**: 
  - [GitLab & ShoppingAdmin](https://github.com/web-arena-x/webarena/tree/main/environment_docker#pre-installed-amazon-machine-image-recommended)
  - [SuiteCRM](https://github.com/segev-shlomov/ST-WebAgentBench/blob/main/suitecrm_setup/README.md)

- **WASP**: [visualwebarena](https://github.com/facebookresearch/wasp/blob/main/visualwebarena/environment_docker/README.md)

> **⚠️ Notice**: If the ST-WebAgentBench website runs successfully, several website URLs need to be configured in `HarmonyGuard/benchmark/ST-WebAgentBench/.env`.

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
  openai:
    api_key: "${OPENAI_API_KEY}" # read from .env
    base_url: "${OPENAI_API_BASE}" # read from .env
    model: "gpt-4o"
    max_tokens: 8000
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
  -i your_policy_file_path \
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

## 🐝 Running

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
### Result Saved

We recommend saving all output files in the `HarmonyGuard/output` directory.
The results of WASP should be stored in `HarmonyGuard/output/wasp`, and the results of ST-WebAgentBench should be stored in `HarmonyGuard/output/stweb`.

### Notice
The results of WASP is printed to the console. Please make sure to save the complete execution log.



---

## 🧪 Evaluation
We provide the evaluation code in the `evaluate` folder. Detailed instructions can be found [here](evaluate/README.md).

## 🙏 Acknowledgments

<div align="center">

| Project | Description |
|---------|-------------|
| **ST-WebAgentBench** | For the safety and trustworthiness evaluation framework |
| **WASP** | For the web agent security benchmark |
| **BrowserGym** | For the web automation infrastructure |

</div>

---

## 📞 Contact

For questions, issues, or contributions:

- 📧 **Email**: [yurunchen.research@gmail.com](mailto:yurunchen.research@gmail.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/YurunChen/HarmonyGuard/issues)

---

## 📄 License

This project is licensed under the MIT License.

