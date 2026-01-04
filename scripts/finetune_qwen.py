#!/usr/bin/env python3
"""
Fine-tune Qwen 2.5 on Hassania dialect using QLoRA.
"""

import os
import json
import argparse
from pathlib import Path
import torch
from datasets import load_dataset, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune Qwen 2.5 on Hassania dialect")
    parser.add_argument(
        "--model_name",
        type=str,
        default="Qwen/Qwen2.5-1.5B-Instruct",
        help="Base model to fine-tune"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="./data/processed/hassania_combined.jsonl",
        help="Path to training data"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./models/qwen2.5-hassania",
        help="Output directory for fine-tuned model"
    )
    parser.add_argument(
        "--num_epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Training batch size"
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=16,
        help="Gradient accumulation steps"
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=2e-5,
        help="Learning rate"
    )
    parser.add_argument(
        "--lora_r",
        type=int,
        default=16,
        help="LoRA rank"
    )
    parser.add_argument(
        "--lora_alpha",
        type=int,
        default=32,
        help="LoRA alpha"
    )
    parser.add_argument(
        "--max_seq_length",
        type=int,
        default=512,
        help="Maximum sequence length"
    )
    return parser.parse_args()


def load_training_data(data_path):
    """Load and format training data."""
    print(f"Loading data from {data_path}...")
    
    samples = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            samples.append(json.loads(line))
    
    print(f"Loaded {len(samples)} samples")
    return Dataset.from_list(samples)


def format_instruction(sample):
    """Format sample into instruction format for Qwen."""
    instruction = sample.get('instruction', '')
    input_text = sample.get('input', '')
    output = sample.get('output', '')
    
    if input_text:
        prompt = f"<|im_start|>user\n{instruction}\n\nInput: {input_text}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
    else:
        prompt = f"<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
    
    return {"text": prompt}


def main():
    args = parse_args()
    
    print("\n" + "="*60)
    print("QWEN 2.5 HASSANIA FINE-TUNING")
    print("="*60)
    print(f"Model: {args.model_name}")
    print(f"Data: {args.data_path}")
    print(f"Output: {args.output_dir}")
    print("="*60 + "\n")
    
    # Check for GPU
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("WARNING: No GPU detected. Training will be slow.")
    
    # Load dataset
    dataset = load_training_data(args.data_path)
    dataset = dataset.map(format_instruction)
    
    # Split into train/eval
    dataset = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = dataset['train']
    eval_dataset = dataset['test']
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Eval samples: {len(eval_dataset)}")
    
    # QLoRA configuration (4-bit quantization)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    
    # Load model
    print(f"\nLoading model: {args.model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # LoRA configuration
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        fp16=True,
        optim="paged_adamw_8bit",
        report_to="none",
        save_total_limit=2,
    )
    
    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
    )
    
    # Train
    print("\nStarting training...")
    trainer.train()
    
    # Save model
    print(f"\nSaving model to {args.output_dir}")
    trainer.save_model()
    tokenizer.save_pretrained(args.output_dir)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print(f"Model saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
