#!/bin/bash
# =============================================================================
# Jais Fine-Tuning Script for RunPod / Cloud GPU
# =============================================================================
# This script sets up the environment and runs Jais fine-tuning on Hassaniya data
#
# Usage on RunPod:
#   1. Create a new Pod with PyTorch template
#   2. Select A100 40GB or 80GB GPU
#   3. Upload this script and run: bash runpod_jais_train.sh
#
# Estimated time: 2-4 hours for Jais-13b, 4-8 hours for Jais-30b
# Estimated cost: $2-10 depending on GPU and model size
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "JAIS HASSANIYA FINE-TUNING - CLOUD GPU SETUP"
echo "=============================================="

# Configuration
MODEL_SIZE="${MODEL_SIZE:-jais-13b}"  # Options: jais-13b, jais-30b
EPOCHS="${EPOCHS:-3}"
BATCH_SIZE="${BATCH_SIZE:-2}"
LEARNING_RATE="${LEARNING_RATE:-2e-5}"

echo "Configuration:"
echo "  Model: $MODEL_SIZE"
echo "  Epochs: $EPOCHS"
echo "  Batch Size: $BATCH_SIZE"
echo "  Learning Rate: $LEARNING_RATE"
echo ""

# Step 1: Install dependencies
echo "[1/6] Installing dependencies..."
pip install --upgrade pip
pip install torch>=2.0.0 transformers>=4.36.0 accelerate>=0.25.0 datasets>=2.14.0
pip install peft>=0.7.0 bitsandbytes>=0.41.0
pip install sentencepiece protobuf scipy einops
pip install huggingface_hub

# Step 2: Clone the repository
echo "[2/6] Cloning repository..."
if [ ! -d "hassania-qwen-finetune" ]; then
    git clone https://github.com/lemneya/hassania-qwen-finetune.git
fi
cd hassania-qwen-finetune

# Step 3: Verify GPU
echo "[3/6] Checking GPU..."
python3 -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
"

# Step 4: Login to Hugging Face (required for Jais)
echo "[4/6] Hugging Face authentication..."
echo "NOTE: You need to accept the Jais model license at:"
echo "  https://huggingface.co/inceptionai/jais-13b-chat"
echo "  or https://huggingface.co/core42/jais-30b-chat-v3"
echo ""
if [ -z "$HF_TOKEN" ]; then
    echo "Please set HF_TOKEN environment variable or login manually:"
    echo "  huggingface-cli login"
    read -p "Press Enter after logging in..."
else
    huggingface-cli login --token $HF_TOKEN
fi

# Step 5: Run fine-tuning
echo "[5/6] Starting fine-tuning..."
echo "This will take 2-8 hours depending on model size..."
echo ""

python3 hdrp/pipeline/finetune/jais_finetune.py \
    --model $MODEL_SIZE \
    --epochs $EPOCHS \
    --batch-size $BATCH_SIZE \
    --lr $LEARNING_RATE \
    --output-dir models/jais-hassaniya

# Step 6: Test the model
echo "[6/6] Testing fine-tuned model..."
python3 -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_path = 'models/jais-hassaniya/final'
print(f'Loading model from {model_path}...')

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map='auto',
    torch_dtype=torch.float16,
    trust_remote_code=True
)

# Test prompt
test_prompt = '''### Instruction: اسمك مساعد حسانية، متخصص في اللهجة الحسانية الموريتانية.
أكمل المحادثة أدناه بين [|Human|] و [|AI|]:
### Input: [|Human|] كيف نقول مرحبا بالحسانية؟
### Response: [|AI|]'''

inputs = tokenizer(test_prompt, return_tensors='pt').to(model.device)
outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print('Test Response:')
print(response.split('### Response: [|AI|]')[-1])
"

echo ""
echo "=============================================="
echo "FINE-TUNING COMPLETE!"
echo "=============================================="
echo ""
echo "Model saved to: models/jais-hassaniya/final"
echo ""
echo "To download the model:"
echo "  zip -r jais-hassaniya-model.zip models/jais-hassaniya/final"
echo ""
echo "To continue testing interactively:"
echo "  python3 hdrp/pipeline/finetune/test_jais_hassaniya.py --model models/jais-hassaniya/final"
