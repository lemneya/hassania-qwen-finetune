#!/usr/bin/env python3
"""
Monitor OpenAI fine-tuning job progress.
"""

import os
import sys
import time
import json
from openai import OpenAI

def monitor_job(job_id):
    client = OpenAI()
    
    print(f"Monitoring fine-tuning job: {job_id}")
    print("="*60)
    
    last_status = None
    
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        
        if job.status != last_status:
            print(f"\n[{time.strftime('%H:%M:%S')}] Status: {job.status}")
            last_status = job.status
            
            if job.status == "running":
                # Get training metrics
                events = client.fine_tuning.jobs.list_events(job_id, limit=5)
                for event in reversed(events.data):
                    print(f"  - {event.message}")
        
        if job.status == "succeeded":
            print(f"\n{'='*60}")
            print("FINE-TUNING COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            print(f"\nFine-tuned model: {job.fine_tuned_model}")
            print(f"Trained tokens: {job.trained_tokens}")
            
            # Save the model name
            result = {
                "job_id": job_id,
                "status": job.status,
                "fine_tuned_model": job.fine_tuned_model,
                "trained_tokens": job.trained_tokens,
                "finished_at": job.finished_at
            }
            
            with open("/home/ubuntu/hassania-qwen-finetune/finetune_result.json", "w") as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"\nResult saved to: finetune_result.json")
            print(f"\nTo use the model:")
            print(f'  client.chat.completions.create(model="{job.fine_tuned_model}", ...)')
            return job.fine_tuned_model
            
        elif job.status == "failed":
            print(f"\n{'='*60}")
            print("FINE-TUNING FAILED!")
            print(f"{'='*60}")
            print(f"Error: {job.error}")
            return None
            
        elif job.status == "cancelled":
            print("\nFine-tuning job was cancelled.")
            return None
        
        # Check progress every 30 seconds
        time.sleep(30)

def main():
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
    else:
        # Try to load from saved file
        try:
            with open("/home/ubuntu/hassania-qwen-finetune/finetune_job_info.json") as f:
                info = json.load(f)
                job_id = info["job_id"]
        except:
            print("Usage: python monitor_finetune.py <job_id>")
            sys.exit(1)
    
    monitor_job(job_id)

if __name__ == "__main__":
    main()
