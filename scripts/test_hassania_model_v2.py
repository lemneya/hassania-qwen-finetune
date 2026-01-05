#!/usr/bin/env python3
"""
Test the v2 fine-tuned Hassania model (cleaned data - no poetry).
"""

from openai import OpenAI
import json

# V2 Fine-tuned model name (cleaned data)
MODEL = "ft:gpt-4o-mini-2024-07-18:personal:hassania-v2:CuU8TMsr"

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
    print("TESTING HASSANIA V2 MODEL (CLEANED DATA)")
    print(f"Model: {MODEL}")
    print("="*60)
    
    system_msg = """You are a native Hassania (Hassaniya) Arabic speaker from Mauritania. You speak the authentic Hassania dialect, not Modern Standard Arabic or other dialects.

Key Hassania features you use:
- Unique vocabulary different from MSA
- Specific verb conjugations and grammar patterns  
- Common expressions and greetings used in Mauritania
- Both Arabic script and romanized transcription when helpful

You help with translations, vocabulary, grammar explanations, and natural conversation in Hassania."""
    
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
            "name": "Hassania Vocabulary - Family",
            "prompt": "What are some common Hassania words for family members?"
        },
        {
            "name": "Hassania Grammar - Questions",
            "prompt": "Explain how to form questions in Hassania dialect."
        },
        {
            "name": "Hassania Common Phrases",
            "prompt": "Give me 5 common everyday phrases in Hassania with their English translations."
        },
        {
            "name": "Hassania vs MSA",
            "prompt": "What are the main differences between Hassania and Modern Standard Arabic?"
        },
        {
            "name": "Hassania Numbers",
            "prompt": "How do you count from 1 to 10 in Hassania?"
        },
        {
            "name": "Hassania Conversation",
            "prompt": "Write a short conversation in Hassania between two people meeting for the first time."
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
    with open("/home/ubuntu/hassania-qwen-finetune/test_results_v2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("TEST RESULTS SAVED TO: test_results_v2.json")
    print("="*60)

if __name__ == "__main__":
    main()
