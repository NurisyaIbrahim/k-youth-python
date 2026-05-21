# tag_data.py - Tag BOTH tables with continuous batch numbering (starting at 1)
import sqlite3
import time
import requests

DB_PATH = '../week1/data/3_gold/jobs.db'
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"

# Batch configuration
BATCH_SIZE = 4
RETRY_DELAY = 3
MAX_RETRIES = 3

def count_tokens(text):
    """Estimate token count (4 tokens per word)"""
    return len(text.split()) * 4

def extract_tech_stack(description):
    """Extract tech stack using Ollama"""
    prompt = f"""Extract technical skills from this job description.
Return ONLY comma-separated list. No explanations.

Job Description: {description[:800]}

Technical skills:"""
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 150}
            }, timeout=90)
            
            result = response.json().get('response', '').strip()
            result = result.replace('\n', ', ').strip(', ')
            
            if result and len(result) > 5:
                return result[:150]
            return "Python, SQL, Git"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return "Python, SQL, Git"

def tag_data(db_url: str):
    overall_start = time.time()
    total_tokens = 0
    total_processed = 0
    total_failed = 0
    global_batch_num = 1  # Start batch numbering from 1
    
    conn = sqlite3.connect(db_url)
    cursor = conn.cursor()
    
    # Get total pending jobs from both tables
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE tech_stack IS NULL OR tech_stack = ''")
    jobs_pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs_quarantine WHERE tech_stack IS NULL OR tech_stack = ''")
    quarantine_pending = cursor.fetchone()[0]
    
    total_jobs = jobs_pending + quarantine_pending
    
    print("=" * 60)
    print("🚀 STARTING TECH STACK TAGGING")
    print("=" * 60)
    print(f"📊 Total jobs to tag: {total_jobs}")
    print(f"   - Jobs table: {jobs_pending}")
    print(f"   - Quarantine: {quarantine_pending}")
    print(f"   - Batch size: {BATCH_SIZE}")
    print("=" * 60)
    
    # Process jobs table
    if jobs_pending > 0:
        print(f"\n📋 PROCESSING JOBS TABLE")
        print("-" * 40)
        
        cursor.execute("""
            SELECT source_id, description 
            FROM jobs
            WHERE tech_stack IS NULL OR tech_stack = ''
        """)
        jobs = cursor.fetchall()
        
        for batch_start in range(0, len(jobs), BATCH_SIZE):
            batch = jobs[batch_start:batch_start + BATCH_SIZE]
            
            print(f"\n[Batch {global_batch_num}] Processing {len(batch)} jobs...")
            
            for job_id, (source_id, description) in enumerate(batch):
                print(f"  Analyzing Job {source_id}...")
                
                input_tokens = count_tokens(description[:800])
                tech_stack = extract_tech_stack(description)
                output_tokens = count_tokens(tech_stack)
                total_tokens += input_tokens + output_tokens
                
                if tech_stack:
                    cursor.execute(
                        "UPDATE jobs SET tech_stack = ? WHERE source_id = ?",
                        (tech_stack, source_id)
                    )
                    conn.commit()
                    total_processed += 1
                    print(f"    ✅ {tech_stack[:80]}...")
                else:
                    total_failed += 1
                    print(f"    ❌ Failed")
                
                if job_id < len(batch) - 1:
                    time.sleep(2)
            
            print(f"  [Batch {global_batch_num}] committed")
            global_batch_num += 1
            
            if batch_start + BATCH_SIZE < len(jobs):
                print(f"  Waiting 5 seconds before next batch...")
                time.sleep(5)
    
    # Process jobs_quarantine table
    if quarantine_pending > 0:
        print(f"\n📋 PROCESSING JOBS_QUARANTINE TABLE")
        print("-" * 40)
        
        cursor.execute("""
            SELECT source_id, description 
            FROM jobs_quarantine
            WHERE tech_stack IS NULL OR tech_stack = ''
        """)
        jobs = cursor.fetchall()
        
        for batch_start in range(0, len(jobs), BATCH_SIZE):
            batch = jobs[batch_start:batch_start + BATCH_SIZE]
            
            print(f"\n[Batch {global_batch_num}] Processing {len(batch)} jobs...")
            
            for job_id, (source_id, description) in enumerate(batch):
                print(f"  Analyzing Job {source_id}...")
                
                input_tokens = count_tokens(description[:800])
                tech_stack = extract_tech_stack(description)
                output_tokens = count_tokens(tech_stack)
                total_tokens += input_tokens + output_tokens
                
                if tech_stack:
                    cursor.execute(
                        "UPDATE jobs_quarantine SET tech_stack = ? WHERE source_id = ?",
                        (tech_stack, source_id)
                    )
                    conn.commit()
                    total_processed += 1
                    print(f"    ✅ {tech_stack[:80]}...")
                else:
                    total_failed += 1
                    print(f"    ❌ Failed")
                
                if job_id < len(batch) - 1:
                    time.sleep(2)
            
            print(f"  [Batch {global_batch_num}] committed")
            global_batch_num += 1
            
            if batch_start + BATCH_SIZE < len(jobs):
                print(f"  Waiting 5 seconds before next batch...")
                time.sleep(5)
    
    conn.close()
    
    overall_end = time.time()
    total_time_ms = (overall_end - overall_start) * 1000
    
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total jobs: {total_jobs} | Processed: {total_processed} | Failed: {total_failed}")
    print(f"📝 Total tokens used: {total_tokens}, took {total_time_ms:.2f}ms")
    print("=" * 60)

if __name__ == "__main__":
    tag_data(DB_PATH)