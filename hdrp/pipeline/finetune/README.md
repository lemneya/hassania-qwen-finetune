# Hassaniya Fine-Tuning Scripts

This directory contains scripts for fine-tuning language models on the Hassaniya dialect.

## Recommended Model for Arabic Dialects

**Jais** is the recommended model for Hassaniya fine-tuning because:
- Built specifically for Arabic with 126B Arabic tokens
- Native Arabic tokenization (more efficient than GPT)
- Better dialect understanding out of the box
- Open source with full fine-tuning control

## Available Options

### 0. Jais Fine-Tuning (RECOMMENDED for Arabic)

**Models:** Jais-13b-chat, Jais-30b-chat-v3  
**Time:** 2-8 hours depending on model size  
**Cost:** GPU compute only (open source)

```bash
# Install dependencies
pip install -r requirements_jais.txt

# Fine-tune Jais-13b (requires ~10GB VRAM with QLoRA)
python3 jais_finetune.py --model jais-13b --epochs 3

# Fine-tune Jais-30b (requires ~24GB VRAM with QLoRA)
python3 jais_finetune.py --model jais-30b --epochs 3 --batch-size 1

# Test the fine-tuned model
python3 test_jais_hassaniya.py --model models/jais-hassaniya/final
```

#### Jais Hardware Requirements

| Model | VRAM (QLoRA) | Training Time |
|-------|--------------|---------------|
| Jais-13b | ~10GB | ~2-4 hours |
| Jais-30b | ~24GB | ~4-8 hours |

### 1. OpenAI Fine-Tuning (Recommended for Quick Results)

**Model:** gpt-4o-mini  
**Time:** ~2-4 hours  
**Cost:** ~$10-30

```bash
# Start fine-tuning
python3 openai_finetune.py

# Monitor progress
python3 monitor_openai.py

# List all jobs
python3 monitor_openai.py --list
```

### 2. Local Qwen Fine-Tuning (Recommended for Full Control)

**Models:** Qwen2.5-0.5B to Qwen2.5-14B  
**Time:** 1-8 hours depending on model size  
**Cost:** GPU compute only

#### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# For CUDA support (recommended)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

#### Run Fine-Tuning

```bash
# Default (Qwen2.5-1.5B, 3 epochs)
python3 qwen_finetune.py

# Custom configuration
python3 qwen_finetune.py \
    --model Qwen/Qwen2.5-7B-Instruct \
    --epochs 3 \
    --batch-size 2 \
    --lr 2e-5 \
    --lora-r 16 \
    --lora-alpha 32
```

#### Hardware Requirements

| Model | VRAM | Recommended GPU |
|-------|------|-----------------|
| Qwen2.5-0.5B | 4GB | RTX 3060 |
| Qwen2.5-1.5B | 8GB | RTX 3070/4060 |
| Qwen2.5-7B | 16GB | RTX 4080/A100 |
| Qwen2.5-14B | 24GB+ | A100/H100 |

## Data Files

The scripts use HDRP-compliant data from:
- Training: `hdrp/data/processed/exports/sft/sft_hassaniya_v2.jsonl` (10,668 records)
- Evaluation: `hdrp/data/processed/exports/eval/eval_hassaniya_v2.jsonl` (593 records)

## Output

### OpenAI
- Fine-tuned model available via API
- Model name format: `ft:gpt-4o-mini-2024-07-18:org::hassaniya-v1`

### Qwen
- Model saved to: `models/qwen-hassaniya/final/`
- Can be loaded with Hugging Face Transformers

## Testing the Fine-Tuned Model

### OpenAI
```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="ft:gpt-4o-mini-2024-07-18:org::hassaniya-v1",  # Your model name
    messages=[
        {"role": "system", "content": "You are a helpful Hassaniya assistant."},
        {"role": "user", "content": "How do you say 'hello' in Hassaniya?"}
    ]
)
print(response.choices[0].message.content)
```

### Qwen
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("models/qwen-hassaniya/final")
tokenizer = AutoTokenizer.from_pretrained("models/qwen-hassaniya/final")

messages = [
    {"role": "system", "content": "You are a helpful Hassaniya assistant."},
    {"role": "user", "content": "How do you say 'hello' in Hassaniya?"}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```
