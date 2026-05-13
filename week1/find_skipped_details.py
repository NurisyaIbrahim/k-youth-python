from pathlib import Path
from bs4 import BeautifulSoup

bronze_dir = Path("data/1_bronze")
silver_dir = Path("data/2_silver")

html_files = list(bronze_dir.glob("*.html"))
skipped_files = []

for html in html_files:
    json_file = silver_dir / f"{html.stem}.json"
    if not json_file.exists():
        skipped_files.append(html)

print(f"Found {len(skipped_files)} skipped files:\n")

for i, html_file in enumerate(skipped_files, 1):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    title = soup.find('h1')
    has_title = title and title.get_text(strip=True)
    
    desc = soup.find(class_='job-description') or soup.find(class_='description')
    has_desc = desc and len(desc.get_text(strip=True)) > 50
    
    missing = []
    if not has_title:
        missing.append("JOB TITLE")
    if not has_desc:
        missing.append("DESCRIPTION")
    
    print(f"{i}. {html_file.name}")
    print(f"   Missing: {' & '.join(missing)}")
    print()
