from bs4 import BeautifulSoup
from pathlib import Path

# Test on one file
html_files = list(Path("data/1_bronze").glob("*.html"))
print(f"Found {len(html_files)} files")

for html_path in html_files[:3]:  # Test first 3 files
    print(f"\nProcessing: {html_path.name}")
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Try to find title
    title = soup.find('h1')
    if title:
        print(f"  Title: {title.get_text(strip=True)[:100]}")
    else:
        print("  No h1 tag found")
