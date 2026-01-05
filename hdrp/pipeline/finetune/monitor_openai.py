#!/usr/bin/env python3
"""
Monitor OpenAI Fine-Tuning Job
"""

import json
import time
from pathlib import Path
from openai import OpenAI

BASE_DIR = Path(__file__).parent.parent.parent.parent
JOB_FILE = BASE_DIR / "hdrp/data/processed/exports/openai/finetune_job.json"

def get_job_id():
    """Get job ID from saved file."""
    if JOB_FILE.exists():
        with open(JOB_FILE, 'r') as f:
            data = json.load(f)
            return data.get("job_id")
    return None

def monitor_job(job_id: str = None, poll_interval: int = 30):
    """Monitor fine-tuning job status."""
    client = OpenAI()
    
    if not job_id:
        job_id = get_job_id()
    
    if not job_id:
        print("No job ID found. Please provide one.")
        return
    
    print(f"Monitoring job: {job_id}")
    print(f"Poll interval: {poll_interval}s")
    print("-" * 60)
    
    last_status = None
    
    while True:
        try:
            job = client.fine_tuning.jobs.retrieve(job_id)
            
            if job.status != last_status:
                print(f"\n[{time.strftime('%H:%M:%S')}] Status: {job.status}")
                last_status = job.status
                
                if job.status == "succeeded":
                    print(f"\n{'='*60}")
                    print("FINE-TUNING COMPLETE!")
                    print(f"{'='*60}")
                    print(f"Fine-tuned model: {job.fine_tuned_model}")
                    print(f"Trained tokens: {job.trained_tokens}")
                    
                    # Update job file
                    if JOB_FILE.exists():
                        with open(JOB_FILE, 'r') as f:
                            data = json.load(f)
                        data["status"] = "succeeded"
                        data["fine_tuned_model"] = job.fine_tuned_model
                        data["trained_tokens"] = job.trained_tokens
                        with open(JOB_FILE, 'w') as f:
                            json.dump(data, f, indent=2, default=str)
                    
                    return job
                
                elif job.status == "failed":
                    print(f"\n{'='*60}")
                    print("FINE-TUNING FAILED!")
                    print(f"{'='*60}")
                    print(f"Error: {job.error}")
                    return job
                
                elif job.status == "cancelled":
                    print("\nJob was cancelled.")
                    return job
            
            # Print progress dots
            print(".", end="", flush=True)
            time.sleep(poll_interval)
            
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped. Job continues in background.")
            print(f"Resume with: python3 monitor_openai.py --job-id {job_id}")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(poll_interval)

def list_jobs(limit: int = 10):
    """List recent fine-tuning jobs."""
    client = OpenAI()
    
    jobs = client.fine_tuning.jobs.list(limit=limit)
    
    print(f"{'='*60}")
    print("RECENT FINE-TUNING JOBS")
    print(f"{'='*60}")
    
    for job in jobs.data:
        print(f"\nJob ID: {job.id}")
        print(f"  Model: {job.model}")
        print(f"  Status: {job.status}")
        print(f"  Created: {job.created_at}")
        if job.fine_tuned_model:
            print(f"  Fine-tuned model: {job.fine_tuned_model}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor OpenAI fine-tuning")
    parser.add_argument("--job-id", help="Job ID to monitor")
    parser.add_argument("--list", action="store_true", help="List recent jobs")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds")
    
    args = parser.parse_args()
    
    if args.list:
        list_jobs()
    else:
        monitor_job(args.job_id, args.interval)

if __name__ == "__main__":
    main()
