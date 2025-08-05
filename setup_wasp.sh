#!/bin/bash

# HarmonyGuard WASP Test Environment Setup Script
# This script sets up a testing environment specifically for WASP (WebArena Prompt Injections)

set -e  # Exit on any error

echo "🚀 Setting up HarmonyGuard WASP Test Environment..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda is not installed. Please install Anaconda or Miniconda first."
    echo "📥 Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ conda is installed: $(conda --version)"

# Create conda environment if it doesn't exist
ENV_NAME="harmonyguard-wasp"
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "📦 Creating conda environment: $ENV_NAME"
    conda create -n $ENV_NAME python=3.10 -y
else
    echo "✅ Conda environment '$ENV_NAME' already exists"
fi

# Activate conda environment
echo "🔧 Activating conda environment: $ENV_NAME"
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME



# Install requirements
echo "📚 Installing Python dependencies..."

echo "🔧 Installing WASP specific dependencies..."
pip install -r requirements_wasp.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p output/wasp
mkdir -p logs

# ============================================================================
# WebArena Prompt Injections Setup
# ============================================================================
echo ""
echo "🔧 Setting up WebArena Prompt Injections components..."

# VisualWebarena setup
echo "📦 Installing required packages for visualwebarena..."
cd benchmark/wasp/visualwebarena
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
playwright install
pip install -e .
deactivate
cd ../../..

# WebArena Prompt Injections setup
echo "📦 Installing required packages for prompt injection tests..."
cd benchmark/wasp/webarena_prompt_injections
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
playwright install
deactivate
cd ../../..

# Claude-v3.5-sonnet computer use demo setup
echo "📦 Installing required packages for Claude computer use agent..."
cd benchmark/wasp/claude-35-computer-use-demo
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r dev-requirements.txt
deactivate
cd ../../..

echo "✅ WebArena Prompt Injections setup completed!"
echo ""
echo "🎉 WASP test environment setup completed!"

echo "🔧 Automatically activating conda environment: $ENV_NAME"
conda activate $ENV_NAME
echo "✅ Environment activated successfully!"
echo ""
echo "📋 Next steps:"
echo "Configure API keys in config.yaml file"
echo "   - Open config.yaml and add your API keys"
echo "   - Required keys: OPENAI_API_KEY, ANTHROPIC_API_KEY (if using Claude)"
