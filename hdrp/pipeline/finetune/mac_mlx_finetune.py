#!/usr/bin/env python3
"""
Jais-Hassaniya Fine-Tuning Script for Mac (Apple Silicon)
Optimized for MacBook Pro M4 Max with 36GB Memory

Uses MLX for efficient Apple Silicon training.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime

def check_system():
    """Check system requirements."""
    import platform
    import subprocess
    
    print("🍎 Checking system requirements...")
    
    # Check Apple Silicon
    if platform.machine() != "arm64":
        print("❌ This script requires Apple Silicon (M1/M2/M3/M4)")
        return False
    
    # Check memory
    result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
    memory_gb = int(result.stdout.strip()) / (1024**3)
    print(f"   Memory: {memory_gb:.0f} GB")
    
    if memory_gb < 16:
        print("⚠️ Warning: Less than 16GB memory. Training may be slow.")
    
    # Check MLX
    try:
        import mlx
        print(f"   MLX version: {mlx.__version__}")
    except ImportError:
        print("❌ MLX not installed. Run: pip install mlx mlx-lm")
        return False
    
    print("✅ System check passed!")
    return True


def prepare_data(data_path: str, output_dir: str):
    """Convert HDRP data to MLX format."""
    print(f"\n📊 Preparing training data...")
    
    # Load HDRP data
    data = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            data.append(item)
    
    print(f"   Loaded {len(data)} examples")
    
    # Convert to MLX chat format
    mlx_data = []
    for item in data:
        messages = item.get('messages', [])
        if len(messages) >= 2:
            # Find user and assistant messages
            user_msg = None
            assistant_msg = None
            system_msg = "You are a helpful assistant that speaks Hassaniya Arabic dialect."
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_msg = msg['content']
                elif msg['role'] == 'user':
                    user_msg = msg['content']
                elif msg['role'] == 'assistant':
                    assistant_msg = msg['content']
            
            if user_msg and assistant_msg:
                mlx_data.append({
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": assistant_msg}
                    ]
                })
    
    # Split train/valid
    split_idx = int(len(mlx_data) * 0.95)
    train_data = mlx_data[:split_idx]
    valid_data = mlx_data[split_idx:]
    
    # Save
    os.makedirs(output_dir, exist_ok=True)
    
    train_path = os.path.join(output_dir, "train.jsonl")
    valid_path = os.path.join(output_dir, "valid.jsonl")
    
    with open(train_path, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    with open(valid_path, 'w', encoding='utf-8') as f:
        for item in valid_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"   Train: {len(train_data)} examples -> {train_path}")
    print(f"   Valid: {len(valid_data)} examples -> {valid_path}")
    
    return train_path, valid_path


def run_finetuning(
    model_name: str = "mlx-community/Qwen2.5-7B-Instruct-4bit",
    train_path: str = None,
    valid_path: str = None,
    output_dir: str = "./models/hassaniya-mlx",
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 1e-5,
    lora_rank: int = 16,
):
    """Run fine-tuning using MLX-LM."""
    from mlx_lm import load, generate
    import subprocess
    
    print(f"\n🚀 Starting fine-tuning...")
    print(f"   Model: {model_name}")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Learning rate: {learning_rate}")
    print(f"   LoRA rank: {lora_rank}")
    
    # Use mlx_lm.lora for fine-tuning
    cmd = [
        "python", "-m", "mlx_lm.lora",
        "--model", model_name,
        "--train",
        "--data", os.path.dirname(train_path),
        "--iters", str(epochs * 1000),  # Approximate iterations
        "--batch-size", str(batch_size),
        "--learning-rate", str(learning_rate),
        "--lora-rank", str(lora_rank),
        "--adapter-path", output_dir,
    ]
    
    print(f"\n   Running: {' '.join(cmd)}")
    print("\n" + "="*60)
    print("Training started. This will take 3-4 hours on M4 Max.")
    print("You can monitor progress below:")
    print("="*60 + "\n")
    
    # Run training
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    
    if process.returncode == 0:
        print("\n✅ Fine-tuning complete!")
        print(f"   Model saved to: {output_dir}")
    else:
        print(f"\n❌ Training failed with return code: {process.returncode}")
    
    return output_dir


def test_model(adapter_path: str, model_name: str):
    """Test the fine-tuned model."""
    from mlx_lm import load, generate
    
    print(f"\n🧪 Testing fine-tuned model...")
    
    # Load model with adapter
    model, tokenizer = load(model_name, adapter_path=adapter_path)
    
    test_prompts = [
        "Translate to Hassaniya: How are you?",
        "Translate to Hassaniya: I want to buy a car",
        "What does 'اشحالك' mean in English?",
    ]
    
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    
    for prompt in test_prompts:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that speaks Hassaniya Arabic dialect."},
            {"role": "user", "content": prompt}
        ]
        
        # Format prompt
        formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        response = generate(
            model, 
            tokenizer, 
            prompt=formatted,
            max_tokens=100,
            temp=0.7
        )
        
        print(f"\n📝 Prompt: {prompt}")
        print(f"🤖 Response: {response}")
        print("-"*60)


def main():
    parser = argparse.ArgumentParser(description="Jais-Hassaniya Fine-Tuning for Mac")
    parser.add_argument("--model", default="mlx-community/Qwen2.5-7B-Instruct-4bit",
                        help="Base model (MLX format)")
    parser.add_argument("--data", default="hdrp/data/processed/exports/sft/sft_hassaniya_v2.jsonl",
                        help="Training data path")
    parser.add_argument("--output", default="./models/hassaniya-mlx",
                        help="Output directory for fine-tuned model")
    parser.add_argument("--epochs", type=int, default=3,
                        help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4,
                        help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-5,
                        help="Learning rate")
    parser.add_argument("--lora-rank", type=int, default=16,
                        help="LoRA rank")
    parser.add_argument("--test-only", action="store_true",
                        help="Only test existing model")
    
    args = parser.parse_args()
    
    print("="*60)
    print("🇲🇷 Jais-Hassaniya Fine-Tuning for Mac (Apple Silicon)")
    print("="*60)
    
    # Check system
    if not check_system():
        return
    
    if args.test_only:
        test_model(args.output, args.model)
        return
    
    # Prepare data
    mlx_data_dir = "./data/mlx_format"
    train_path, valid_path = prepare_data(args.data, mlx_data_dir)
    
    # Run fine-tuning
    output_dir = run_finetuning(
        model_name=args.model,
        train_path=train_path,
        valid_path=valid_path,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        lora_rank=args.lora_rank,
    )
    
    # Test model
    test_model(output_dir, args.model)
    
    print("\n" + "="*60)
    print("🎉 All done!")
    print("="*60)
    print(f"\nYour fine-tuned Hassaniya model is saved at: {output_dir}")
    print("\nTo use the model later:")
    print(f"  python3 mac_mlx_finetune.py --test-only --output {output_dir}")


if __name__ == "__main__":
    main()
