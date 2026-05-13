from pathlib import Path
from bs4 import BeautifulSoup
import json

bronze_dir = Path("data/1_bronze")
silver_dir = Path("data/2_silver")

html_files = list(bronze_dir.glob("*.html"))
json_files = list(silver_dir.glob("*.json"))

print("=" * 70)
print("HTML → JSON RELATIONSHIP ANALYSIS")
print("=" * 70)

# Find which HTML files have corresponding JSON
matched = []
html_no_json = []
json_no_html = []

for html in html_files:
    json_file = silver_dir / f"{html.stem}.json"
    if json_file.exists():
        matched.append(html.name)
    else:
        html_no_json.append(html.name)

print(f"\n📁 Files found:")
print(f"  HTML files: {len(html_files)}")
print(f"  JSON files: {len(json_files)}")
print(f"  Matched pairs: {len(matched)}")
print(f"  HTML without JSON (skipped): {len(html_no_json)}")

# Analyze WHY some HTML have no JSON
print("\n🔍 ANALYZING SKIPPED FILES (HTML without JSON):")
print("-" * 50)

for html_name in html_no_json[:10]:  # Show first 10
    html_path = bronze_dir / html_name
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Check what's missing
    title = soup.find('h1')
    has_title = title and title.get_text(strip=True)
    
    desc = soup.find(class_='job-description') or soup.find(class_='description')
    has_desc = desc and len(desc.get_text(strip=True)) > 50
    
    missing = []
    if not has_title:
        missing.append("NO_TITLE")
    if not has_desc:
        missing.append("NO_DESCRIPTION")
    
    print(f"  {html_name[:60]}...")
    print(f"    → Missing: {', '.join(missing)}")
    print()

# Analyze a SAMPLE of processed files (HTML with JSON)
print("\n✅ ANALYZING PROCESSED FILES (Sample of 5):")
print("-" * 50)

for html_name in matched[:5]:
    html_path = bronze_dir / html_name
    json_path = silver_dir / f"{Path(html_name).stem}.json"
    
    # Check HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Check JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    title = soup.find('h1')
    html_title = title.get_text(strip=True) if title else "N/A"
    
    print(f"\n  📄 HTML: {html_name[:50]}...")
    print(f"     HTML Title: {html_title[:50]}")
    print(f"     JSON Title: {json_data.get('job_title', 'N/A')[:50]}")
    print(f"     ✅ Match: {html_title == json_data.get('job_title', '')}")

print("\n" + "=" * 70)
print(f"CONCLUSION:")
print(f"  ✅ Processed: {len(matched)} files (have both HTML and JSON)")
print(f"  ❌ Skipped: {len(html_no_json)} files (missing title or description)")
print("=" * 70)
