# src/processor.py
import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

def process_all_html(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        logger.warning(f"⚠️ Input directory '{input_dir}' does not exist.")
        return
    
    html_files = list(input_path.glob("*.html"))
    
    if not html_files:
        logger.warning(f"⚠️ No .html files found in '{input_dir}'.")
        return
    
    print("🥈 Silver:...")
    
    processed = 0
    skipped = 0
    total = len(html_files)
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Extract source_id from og:url
        og_url = soup.find('meta', property='og:url')
        if og_url and og_url.get('content'):
            url = og_url['content']
            source_id = url.rstrip('/').split('/')[-1]
        else:
            source_id = ""
        
        # Extract job_title from h1
        h1 = soup.find('h1')
        if h1:
            job_title = h1.get_text(separator=" ", strip=True)
        else:
            job_title = ""
        
        # Extract company
        company_elem = soup.find(attrs={'data-automation': 'advertiser-name'})
        if company_elem:
            company = company_elem.get_text(separator=" ", strip=True)
            company = company.replace('<!-- -->', '').strip()
        else:
            company = ""
        
        # Extract description
        desc_div = soup.find('div', {'data-automation': 'jobAdDetails'})
        if desc_div:
            description = desc_div.get_text(separator=" ", strip=True)
        else:
            description = ""
        
        # Track missing fields
        missing = []
        if not source_id:
            missing.append("source_id")
        if not job_title:
            missing.append("job_title")
        if not description:
            missing.append("description")
        if not company:
            missing.append("company")
        
        if missing:
            logger.warning(f"⚠️ Missing {', '.join(missing)} in: {html_file.name}")
        
        # SKIP if missing job_title OR description OR company
        if not job_title or not description or not company:
            skipped += 1
            continue
        
        # Create validated job listing
        job = JobListing(
            source_id=source_id,
            job_title=job_title,
            company=company,
            description=description
        )
        
        output_file = output_path / f"{html_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job.model_dump(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Processed file: {html_file.name}")
        processed += 1
    
    print(f"\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")