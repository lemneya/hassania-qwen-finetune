#!/bin/bash
# =============================================================================
# Jais-Hassaniya Fine-Tuning Setup for Mac (Apple Silicon)
# Optimized for MacBook Pro M4 Max with 36GB Memory
# =============================================================================

echo "🍎 Setting up Jais-Hassaniya Fine-Tuning for Mac"
echo "================================================"

# Check if running on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "❌ This script requires Apple Silicon (M1/M2/M3/M4)"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python first."
    exit 1
fi

echo "✅ Apple Silicon detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv ~/hassaniya-env
source ~/hassaniya-env/bin/activate

# Install dependencies
echo "📦 Installing MLX and dependencies..."
pip install --upgrade pip
pip install mlx mlx-lm transformers datasets huggingface_hub tqdm

# Clone repository if not exists
if [ ! -d "hassania-qwen-finetune" ]; then
    echo "📥 Cloning training data repository..."
    git clone https://github.com/lemneya/hassania-qwen-finetune.git
fi

cd hassania-qwen-finetune

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: source ~/hassaniya-env/bin/activate"
echo "2. Run: python3 hdrp/pipeline/finetune/mac_mlx_finetune.py"
echo ""
