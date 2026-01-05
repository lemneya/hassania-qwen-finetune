#!/usr/bin/env python3
"""
Test the fine-tuned Hassania model with various prompts.
"""

from openai import OpenAI
import json

# Fine-tuned model name
MODEL = "ft:gpt-4o-mini-2024-07-18:personal:hassania:CuTBNU9n"

def test_model(prompt, system_message=None):
    """Test the model with a prompt."""
    client = OpenAI()
    
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def main():
    print("="*60)
    print("TESTING HASSANIA FINE-TUNED MODEL")
    print(f"Model: {MODEL}")
    print("="*60)
    
    system_msg = "You are a helpful assistant specialized in the Hassania (Hassaniya) Arabic dialect spoken in Mauritania and Western Sahara. You can translate between English and Hassania, generate Hassania text, explain grammar, and help with vocabulary."
    
    test_cases = [
        {
            "name": "English to Hassania Translation",
            "prompt": "Translate to Hassania: Hello, how are you?"
        },
        {
            "name": "English to Hassania Translation 2",
            "prompt": "Translate to Hassania: Thank you very much for your help."
        },
        {
            "name": "Hassania to English Translation",
            "prompt": "Translate to English: السلام عليكم، شخبارك؟"
        },
        {
            "name": "Hassania Greeting",
            "prompt": "How do you say 'good morning' in Hassania dialect?"
        },
        {
            "name": "Hassania Poetry",
            "prompt": "Write a short poem (لغن) in Hassania about the desert."
        },
        {
            "name": "Hassania Proverb",
            "prompt": "Give me a traditional Hassania proverb with its meaning."
        },
        {
            "name": "Hassania Vocabulary",
            "prompt": "What are some common Hassania words for family members?"
        },
        {
            "name": "Hassania Grammar",
            "prompt": "Explain how to form questions in Hassania dialect."
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test['name']}")
        print(f"Prompt: {test['prompt']}")
        print("-" * 40)
        
        try:
            response = test_model(test['prompt'], system_msg)
            print(f"Response: {response}")
            results.append({
                "test": test['name'],
                "prompt": test['prompt'],
                "response": response,
                "status": "success"
            })
        except Exception as e:
            print(f"Error: {e}")
            results.append({
                "test": test['name'],
                "prompt": test['prompt'],
                "error": str(e),
                "status": "error"
            })
    
    # Save results
    with open("/home/ubuntu/hassania-qwen-finetune/test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("TEST RESULTS SAVED TO: test_results.json")
    print("="*60)

if __name__ == "__main__":
    main()
