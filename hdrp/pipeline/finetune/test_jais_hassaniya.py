#!/usr/bin/env python3
"""
Test Script for Fine-Tuned Jais Hassaniya Model
================================================
Test the fine-tuned Jais model on various Hassaniya prompts.

Usage:
    python3 test_jais_hassaniya.py --model models/jais-hassaniya/final
    python3 test_jais_hassaniya.py --model inceptionai/jais-13b-chat  # Test base model
"""

import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

def parse_args():
    parser = argparse.ArgumentParser(description="Test Jais Hassaniya model")
    parser.add_argument("--model", type=str, required=True,
                        help="Path to fine-tuned model or base model ID")
    parser.add_argument("--base-model", type=str, default=None,
                        help="Base model ID (if loading LoRA adapter)")
    parser.add_argument("--max-tokens", type=int, default=200,
                        help="Maximum tokens to generate")
    return parser.parse_args()


# Hassaniya system prompt
SYSTEM_PROMPT = """اسمك مساعد حسانية، متخصص في اللهجة الحسانية الموريتانية. أنت تتحدث الحسانية بطلاقة وتفهم الثقافة الموريتانية. ساعد المستخدمين في تعلم وفهم اللهجة الحسانية."""


def format_prompt(user_message: str) -> str:
    """Format a user message in Jais prompt format."""
    prompt = f"### Instruction: {SYSTEM_PROMPT}\n\n"
    prompt += f"أكمل المحادثة أدناه بين [|Human|] و [|AI|]:\n"
    prompt += f"### Input: [|Human|] {user_message}\n"
    prompt += f"### Response: [|AI|]"
    return prompt


def load_model(model_path: str, base_model: str = None):
    """Load the model (either fine-tuned or base)."""
    print(f"Loading model from: {model_path}")
    
    # Check if it's a local path with LoRA adapter
    is_local = not model_path.startswith(("inceptionai/", "core42/"))
    
    # Quantization config for inference
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    
    if is_local and base_model:
        # Load base model + LoRA adapter
        print(f"Loading base model: {base_model}")
        tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        print(f"Loading LoRA adapter from: {model_path}")
        model = PeftModel.from_pretrained(model, model_path)
    else:
        # Load full model (either base or merged fine-tuned)
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    return model, tokenizer


def generate_response(model, tokenizer, prompt: str, max_tokens: int = 200) -> str:
    """Generate a response from the model."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract just the AI response
    if "### Response: [|AI|]" in response:
        response = response.split("### Response: [|AI|]")[-1].strip()
    
    return response


def main():
    args = parse_args()
    
    print("="*60)
    print("JAIS HASSANIYA MODEL TESTING")
    print("="*60)
    
    # Load model
    model, tokenizer = load_model(args.model, args.base_model)
    
    # Test prompts
    test_prompts = [
        # Basic greetings
        {
            "name": "Greeting",
            "prompt": "كيف نقول 'مرحبا، كيف حالك؟' بالحسانية؟",
        },
        # Marketplace
        {
            "name": "Marketplace",
            "prompt": "كيف أسأل عن سعر شيء في السوق بالحسانية؟",
        },
        # Translation
        {
            "name": "Translation EN->Hassaniya",
            "prompt": "Translate 'I want to buy a car' to Hassaniya dialect.",
        },
        # Cultural
        {
            "name": "Cultural - Tea",
            "prompt": "اشرح لي تقاليد الشاي الموريتاني بالحسانية",
        },
        # Direct Hassaniya input
        {
            "name": "Hassaniya Input",
            "prompt": "اشحالك؟",
        },
        # Proverb
        {
            "name": "Proverb",
            "prompt": "أعطني مثل حساني عن الصبر",
        },
        # Family vocabulary
        {
            "name": "Family",
            "prompt": "كيف نقول 'أب' و'أم' و'أخ' بالحسانية؟",
        },
    ]
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    for test in test_prompts:
        print(f"\n### {test['name']}")
        print(f"User: {test['prompt']}")
        
        formatted_prompt = format_prompt(test['prompt'])
        response = generate_response(model, tokenizer, formatted_prompt, args.max_tokens)
        
        print(f"Assistant: {response}")
        print("-"*60)
    
    # Interactive mode
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("Type 'quit' to exit")
    print("="*60)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        formatted_prompt = format_prompt(user_input)
        response = generate_response(model, tokenizer, formatted_prompt, args.max_tokens)
        print(f"Jais: {response}")


if __name__ == "__main__":
    main()
