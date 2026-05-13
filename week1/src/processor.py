import json
from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str
    tech_stack: str = ""

def process_all_html(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        print(f"Warning: Input directory '{input_dir}' does not exist.")
        return
    
    html_files = list(input_path.glob("*.html"))
    if not html_files:
        print(f"Warning: No .html files found in '{input_dir}'.")
        return
    
    print("🥈 Silver:...")
    
    processed = 0
    skipped = 0
    
    for html_file in html_files:
        try:
            # Read and parse HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Extract job title from h1
            title_elem = soup.find('h1')
            job_title = title_elem.get_text(strip=True) if title_elem else None
            
            # Extract company
            company = None
            for selector in ['.company', '.employer', '.company-name']:
                elem = soup.select_one(selector)
                if elem:
                    company = elem.get_text(strip=True)
                    break
            
            # Extract description
            description = None
            for selector in ['.job-description', '.description', '.job-details']:
                elem = soup.select_one(selector)
                if elem:
                    description = elem.get_text(separator=" ", strip=True)
                    break
            
            # If no description found, try meta tag
            if not description:
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    description = meta_desc['content']
            
            # Source ID from filename
            source_id = html_file.stem.replace(" - Jobstreet", "")
            
            # Extract tech stack from description
            tech_stack = []
            tech_keywords = ['Python', 'Java', 'JavaScript', 'React', 'SQL', 'AWS', 'Docker', 'AI', 'Machine Learning', 'TensorFlow', 'PyTorch']
            if description:
                desc_lower = description.lower()
                for tech in tech_keywords:
                    if tech.lower() in desc_lower:
                        tech_stack.append(tech)
            
            # Check for missing required fields
            missing = []
            if not job_title:
                missing.append("job_title")
            if not description:
                missing.append("description")
            
            if missing:
                print(f"⚠️ Missing {', '.join(missing)} in: {html_file.name}")
                skipped += 1
                continue
            
            # Create JobListing object
            job = JobListing(
                source_id=source_id[:200],
                job_title=job_title[:500],
                company=(company or "Unknown")[:200],
                description=description[:5000],
                tech_stack=", ".join(tech_stack)[:500]
            )
            
            # Save to JSON
            output_file = output_path / f"{html_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(job.model_dump(), f, indent=2, ensure_ascii=False)
            
            print(f"✅ Processed: {html_file.name}")
            processed += 1
            
        except Exception as e:
            print(f"⚠️ Error processing {html_file.name}: {str(e)}")
            skipped += 1
    
    print(f"\n📊 Silver Summary:")
    print(f"Total: {len(html_files)} | Processed: {processed} | Skipped: {skipped}")

if __name__ == "__main__":
    process_all_html("data/1_bronze", "data/2_silver")