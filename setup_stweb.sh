#!/bin/bash

# HarmonyGuard ST-WebAgentBench Test Environment Setup Script
# This script sets up a testing environment specifically for ST-WebAgentBench

set -e  # Exit on any error

echo "🚀 Setting up HarmonyGuard ST-WebAgentBench Test Environment..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda is not installed. Please install Anaconda or Miniconda first."
    echo "📥 Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ conda is installed: $(conda --version)"

# Create conda environment if it doesn't exist
ENV_NAME="harmonyguard-stweb"
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
pip install -r requirements_stweb.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
pip install playwright==1.52.0
playwright install chromium

# Verify Playwright installation and reinstall browsers if needed
echo "🔍 Verifying Playwright browser installation..."
if ! playwright install --dry-run chromium | grep -q "already installed"; then
    echo "⚠️  Browser version mismatch detected, reinstalling..."
    playwright install chromium --force
fi

# Install NLTK data for ST-WebAgentBench
echo "📖 Installing NLTK data..."
python -c "
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
"

# Install browsergym package for ST-WebAgentBench
echo "🔧 Installing browsergym package..."
pip install -e benchmark/ST-WebAgentBench/browsergym/stwebagentbench

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p output/stweb
mkdir -p logs

echo "✅ ST-WebAgentBench test environment setup completed!"
echo ""
echo "🔧 Automatically activating conda environment: $ENV_NAME"
conda activate $ENV_NAME
echo "✅ Environment activated successfully!"
echo ""
echo "📋 Next steps:"
echo "Configure API keys in config.yaml file"
echo "   - Open config.yaml and add your API keys"
echo "   - Required keys: OPENAI_API_KEY, ANTHROPIC_API_KEY (if using Claude)"
