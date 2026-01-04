#!/usr/bin/env python3
"""
Generate synthetic Hassania dialect data using OpenAI API.
Uses existing data as examples to generate more diverse training samples.
"""

import os
import json
import random
import time
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "enrichment" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load existing Hassania examples for few-shot prompting
def load_existing_examples():
    """Load existing Hassania text examples."""
    examples = []
    
    # Load from processed dataset
    jsonl_file = PROCESSED_DIR / "hassania_combined.jsonl"
    if jsonl_file.exists():
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    output = data.get('output', '')
                    # Only keep Arabic text outputs
                    if any('\u0600' <= c <= '\u06FF' for c in output) and len(output) > 10:
                        examples.append(output)
                except:
                    continue
    
    return examples[:100]  # Limit to 100 examples for prompting


# Synthetic data generation prompts
GENERATION_PROMPTS = [
    {
        "task": "conversation",
        "system": """You are an expert in Hassania Arabic dialect (اللهجة الحسانية), the Arabic dialect spoken in Mauritania, Western Sahara, and parts of Mali and Senegal. 
Generate authentic conversational exchanges in Hassania dialect. The conversations should reflect daily life, culture, and traditions of Hassania speakers.
Output ONLY the Hassania text, no translations or explanations.""",
        "user": "Generate a short conversation in Hassania Arabic dialect between two people greeting each other and asking about their family. Write only in Hassania Arabic script."
    },
    {
        "task": "proverbs",
        "system": """You are an expert in Hassania Arabic dialect and Mauritanian culture.
Generate traditional Hassania proverbs and sayings (أمثال حسانية). These should reflect the wisdom, values, and nomadic heritage of the Bidan people.
Output ONLY the Hassania proverbs, no translations.""",
        "user": "Generate 5 traditional Hassania Arabic proverbs about life, wisdom, or hospitality. Write only in Hassania Arabic script."
    },
    {
        "task": "poetry",
        "system": """You are an expert in Hassania Arabic poetry (الشعر الحساني).
Generate authentic Hassania poetry verses in the traditional style. Hassania poetry often discusses themes of love, nature, camels, desert life, and tribal honor.
Output ONLY the poetry in Hassania Arabic script.""",
        "user": "Generate a short Hassania Arabic poem (4-6 verses) about the desert or nomadic life. Write only in Hassania Arabic script."
    },
    {
        "task": "daily_expressions",
        "system": """You are an expert in Hassania Arabic dialect.
Generate common daily expressions and phrases used in Hassania dialect. Include greetings, farewells, expressions of gratitude, and common responses.
Output ONLY the Hassania expressions.""",
        "user": "Generate 10 common daily expressions in Hassania Arabic dialect with their contexts. Write only in Hassania Arabic script."
    },
    {
        "task": "stories",
        "system": """You are an expert in Hassania Arabic dialect and Mauritanian oral traditions.
Generate short traditional stories or folk tales in Hassania dialect. These stories often feature animals, moral lessons, or historical events.
Output ONLY the story in Hassania Arabic script.""",
        "user": "Generate a short folk tale in Hassania Arabic dialect (about 100-150 words). Write only in Hassania Arabic script."
    },
    {
        "task": "descriptions",
        "system": """You are an expert in Hassania Arabic dialect.
Generate descriptive texts in Hassania dialect about Mauritanian culture, traditions, food, clothing, or daily activities.
Output ONLY the description in Hassania Arabic script.""",
        "user": "Generate a description in Hassania Arabic dialect about traditional Mauritanian tea ceremony (الشاي الموريتاني). Write only in Hassania Arabic script."
    },
    {
        "task": "translation_pairs",
        "system": """You are an expert translator between English and Hassania Arabic dialect.
Generate English sentences with their Hassania Arabic translations. The sentences should cover various topics relevant to daily life in Mauritania.
Format: English: [sentence] | Hassania: [translation]""",
        "user": "Generate 10 English sentences with their Hassania Arabic translations covering greetings, family, food, and daily activities."
    },
    {
        "task": "questions_answers",
        "system": """You are an expert in Hassania Arabic dialect.
Generate question-answer pairs in Hassania dialect covering various topics like weather, directions, shopping, and social interactions.
Output in Hassania Arabic script only.""",
        "user": "Generate 8 question-answer pairs in Hassania Arabic dialect about daily life situations. Write only in Hassania Arabic script."
    }
]


def generate_with_openai(prompt_config, examples=None, temperature=0.8):
    """Generate synthetic data using OpenAI API."""
    system_prompt = prompt_config["system"]
    user_prompt = prompt_config["user"]
    
    # Add examples if available
    if examples:
        example_text = "\n".join(random.sample(examples, min(5, len(examples))))
        system_prompt += f"\n\nHere are some examples of authentic Hassania text for reference:\n{example_text}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  Error: {e}")
        return None


def parse_generated_content(content, task):
    """Parse generated content into training samples."""
    samples = []
    
    if not content:
        return samples
    
    if task == "translation_pairs":
        # Parse English | Hassania format
        lines = content.split('\n')
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    english = parts[0].replace('English:', '').strip()
                    hassania = parts[1].replace('Hassania:', '').strip()
                    if english and hassania:
                        samples.append({
                            "instruction": f"Translate to Hassania Arabic: {english}",
                            "input": "",
                            "output": hassania,
                            "source": "synthetic_openai",
                            "task": "translation"
                        })
                        samples.append({
                            "instruction": f"Translate to English: {hassania}",
                            "input": "",
                            "output": english,
                            "source": "synthetic_openai",
                            "task": "translation"
                        })
    elif task == "questions_answers":
        # Parse Q&A format
        lines = content.split('\n')
        current_q = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if '?' in line or 'س:' in line or line.startswith('Q'):
                current_q = line
            elif current_q and ('ج:' in line or 'A:' in line or any('\u0600' <= c <= '\u06FF' for c in line)):
                samples.append({
                    "instruction": current_q,
                    "input": "",
                    "output": line,
                    "source": "synthetic_openai",
                    "task": "qa_hassania"
                })
                current_q = None
    else:
        # For other tasks, treat the whole content as output
        # Split by paragraphs or numbered items
        segments = []
        
        # Try splitting by numbers
        numbered = content.split('\n')
        for line in numbered:
            line = line.strip()
            # Remove numbering
            line = line.lstrip('0123456789.-) ')
            if line and len(line) > 10:
                segments.append(line)
        
        if not segments:
            segments = [content]
        
        task_instructions = {
            "conversation": "This is a Hassania Arabic conversation:",
            "proverbs": "This is a Hassania Arabic proverb:",
            "poetry": "This is Hassania Arabic poetry:",
            "daily_expressions": "This is a common Hassania Arabic expression:",
            "stories": "This is a Hassania Arabic folk tale:",
            "descriptions": "This is a description in Hassania Arabic:"
        }
        
        instruction = task_instructions.get(task, "This is Hassania Arabic text:")
        
        for segment in segments:
            if any('\u0600' <= c <= '\u06FF' for c in segment):
                samples.append({
                    "instruction": instruction,
                    "input": "",
                    "output": segment,
                    "source": "synthetic_openai",
                    "task": f"synthetic_{task}"
                })
    
    return samples


def main():
    print("\n" + "#"*60)
    print("# SYNTHETIC HASSANIA DATA GENERATION")
    print("#"*60)
    
    # Load existing examples
    print("\nLoading existing Hassania examples...")
    examples = load_existing_examples()
    print(f"  Loaded {len(examples)} examples for few-shot prompting")
    
    all_samples = []
    
    # Generate data for each prompt type
    num_iterations = 5  # Generate multiple times per prompt type
    
    for prompt_config in GENERATION_PROMPTS:
        task = prompt_config["task"]
        print(f"\nGenerating {task} data...")
        
        for i in range(num_iterations):
            print(f"  Iteration {i+1}/{num_iterations}...")
            
            # Vary temperature for diversity
            temp = 0.7 + random.random() * 0.3
            
            content = generate_with_openai(prompt_config, examples, temperature=temp)
            
            if content:
                samples = parse_generated_content(content, task)
                all_samples.extend(samples)
                print(f"    Generated {len(samples)} samples")
            
            # Rate limiting
            time.sleep(1)
    
    # Save all samples
    if all_samples:
        output_file = OUTPUT_DIR / "synthetic_hassania.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in all_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"\n✓ Saved {len(all_samples)} synthetic samples to {output_file}")
        
        # Statistics
        by_task = {}
        for s in all_samples:
            task = s['task']
            by_task[task] = by_task.get(task, 0) + 1
        
        print("\nSamples by task:")
        for task, count in sorted(by_task.items()):
            print(f"  {task}: {count}")
    else:
        print("\n✗ No synthetic samples generated")


if __name__ == "__main__":
    main()
