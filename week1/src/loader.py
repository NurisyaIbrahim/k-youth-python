import json
import sqlite3
import logging
import hashlib
from pathlib import Path
from src.sql_helper import load_sql

logger = logging.getLogger(__name__)

def compute_content_hash(job_title, company, description):
    """BONUS #2: Compute SHA256 hash of job content"""
    hash_input = f"{job_title}|{company}|{description}"
    hash_input = hash_input.lower().strip()
    hash_input = ' '.join(hash_input.split())
    return hashlib.sha256(hash_input.encode()).hexdigest()

def load_all_jsons(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    db_path = output_path / "jobs.db"
    
    if not input_path.exists():
        logger.warning(f"Input directory '{input_dir}' does not exist.")
        return
    
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        logger.warning(f"No .json files found in '{input_dir}'.")
        return
    
    print("🥇 Gold:...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # BONUS #3: Create table using SQL file
    cursor.execute(load_sql("create_jobs_table"))
    
    inserted = 0
    skipped = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            source_id = data.get('source_id', '')
            job_title = data.get('job_title', '')
            company = data.get('company', 'Unknown')
            description = data.get('description', '')
            tech_stack = data.get('tech_stack', '')
            
            # BONUS #2: Compute content hash
            content_hash = compute_content_hash(job_title, company, description)
            
            # BONUS #3: Insert using SQL file
            cursor.execute(load_sql("insert_job"), 
                          (source_id, job_title, company, description, tech_stack, content_hash, 'PENDING'))
            
            if cursor.rowcount > 0:
                logger.info(f"✅ Inserted: {json_file.name} | Hash: {content_hash[:16]}...")
                inserted += 1
            else:
                logger.warning(f"⏭️ Skipped (duplicate): {json_file.name}")
                skipped += 1
                
        except Exception as e:
            logger.error(f"❌ Error: {json_file.name} | Reason: {str(e)}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Gold Summary:")
    print(f"Total: {len(json_files)} | Inserted: {inserted} | Skipped: {skipped}")
    print(f"\n✅ Database created at: {db_path}")
    print(f"✅ BONUS #2: content_hash column added with SHA256 hashing")
    print(f"✅ BONUS #3: SQL queries loaded from queries/ folder")

if __name__ == "__main__":
    load_all_jsons("data/2_silver", "data/3_gold")
