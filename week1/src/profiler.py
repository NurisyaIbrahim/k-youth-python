# src/profiler.py
import sqlite3
import logging
import re
from pathlib import Path
from src.sql_helper import load_sql

logger = logging.getLogger(__name__)

def determine_quality(description, job_title, company):
    """
    Determine if record is HIGH or LOW quality
    LOW quality if:
    - description length < 100
    - missing job_title
    - missing company
    - too many special characters
    """
    if not job_title or not company or company == "Unknown":
        return "LOW"
    
    if not description or len(description) < 100:
        return "LOW"
    
    special_chars = len(re.findall(r'[!@#$%^&*()_+{}|:;"\'<>,.?/~`]', description))
    if special_chars > 50:
        return "LOW"
    
    return "HIGH"

def run_data_profile(db_path):
    db_file = Path(db_path)
    
    if not db_file.exists():
        logger.error(f"Database not found at {db_path}")
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create quarantine table if not exists
    cursor.execute(load_sql("create_quarantine_table"))
    
    # Get all records to evaluate quality
    cursor.execute("SELECT source_id, job_title, company, description FROM jobs")
    records = cursor.fetchall()
    
    # Update quality for each record
    low_count = 0
    high_count = 0
    
    for record in records:
        source_id, job_title, company, description = record
        quality = determine_quality(description, job_title, company)
        
        if quality == "LOW":
            low_count += 1
        else:
            high_count += 1
        
        cursor.execute("UPDATE jobs SET quality = ? WHERE source_id = ?", (quality, source_id))
    
    conn.commit()
    
    # Move LOW quality records to quarantine (separate statements)
    cursor.execute(load_sql("insert_quarantine"))
    cursor.execute(load_sql("delete_low_quality"))
    
    conn.commit()
    
    # Get counts for report
    cursor.execute(load_sql("count_jobs"))
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs_quarantine")
    quarantine_count = cursor.fetchone()[0]
    
    # Null values
    cursor.execute(load_sql("count_null_values"))
    null_result = cursor.fetchone()
    null_job_title, null_company, null_description = null_result
    
    # Average description length
    cursor.execute(load_sql("avg_description_length"))
    avg_desc_length = cursor.fetchone()[0]
    avg_desc_length = int(avg_desc_length) if avg_desc_length else 0
    
    # Shortest description
    cursor.execute(load_sql("shortest_description"))
    shortest = cursor.fetchone()
    
    # Longest description
    cursor.execute(load_sql("longest_description"))
    longest = cursor.fetchone()
    
    conn.close()
    
    logger.info(f"Data profiling complete - HIGH: {high_count} | LOW: {low_count} | Quarantined: {quarantine_count}")
    
    print("\n--- DATA QUALITY REPORT ---")
    print(f"Total Records (original): {total_records + quarantine_count}")
    print(f"Quality: HIGH={high_count} | LOW={low_count}")
    print(f"Quarantined: {quarantine_count} records moved to jobs_quarantine")
    print(f"Missing Values -> job_title: {null_job_title}, company: {null_company}, description: {null_description}")
    print(f"Avg Description Length: {avg_desc_length} chars")
    
    if shortest:
        print(f"Shortest Description: {shortest[2]} chars")
        print(f"   -> source_id: {shortest[0]} | job_title: {shortest[1]}")
    
    if longest:
        print(f"Longest Description: {longest[2]} chars")
        print(f"   -> source_id: {longest[0]} | job_title: {longest[1]}")
    
    print("-" * 40)

if __name__ == "__main__":
    run_data_profile("data/3_gold/jobs.db")