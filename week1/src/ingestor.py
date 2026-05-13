import re
from pathlib import Path
from email import policy
from email.parser import BytesParser
import quopri
import base64

def ingest_all_mhtml(input_dir, output_dir):
    """
    Extract MHTML files from 0_source and save as HTML in 1_bronze
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists
    if not input_path.exists():
        print(f"Warning: Input directory '{input_dir}' does not exist.")
        return
    
    # Find all mhtml files
    mhtml_files = list(input_path.glob("*.mhtml")) + list(input_path.glob("*.mht"))
    
    if not mhtml_files:
        print(f"Warning: No .mhtml or .mht files found in '{input_dir}'.")
        return
    
    print("🥉 Bronze:...")
    
    success_count = 0
    error_count = 0
    
    for mhtml_path in mhtml_files:
        try:
            # Read the MHTML file
            with open(mhtml_path, 'rb') as f:
                mhtml_data = f.read()
            
            # Parse as email message
            msg = BytesParser(policy=policy.default).parsebytes(mhtml_data)
            
            html_content = None
            
            # Walk through all parts to find HTML
            for part in msg.walk():
                content_type = part.get_content_type()
                
                if content_type == 'text/html':
                    payload = part.get_payload()
                    encoding = part.get('Content-Transfer-Encoding', '').lower()
                    
                    # Decode based on encoding
                    if encoding == 'quoted-printable':
                        if isinstance(payload, str):
                            payload = payload.encode('utf-8')
                        html_content = quopri.decodestring(payload).decode('utf-8', errors='replace')
                    elif encoding == 'base64':
                        if isinstance(payload, str):
                            payload = payload.encode('utf-8')
                        html_content = base64.b64decode(payload).decode('utf-8', errors='replace')
                    else:
                        if isinstance(payload, bytes):
                            html_content = payload.decode('utf-8', errors='replace')
                        else:
                            html_content = payload
                    
                    break
            
            # If no HTML found
            if html_content is None:
                print(f"⚠️ No HTML content found in: {mhtml_path.name}")
                error_count += 1
                continue
            
            # Save HTML file
            output_file = output_path / f"{mhtml_path.stem}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Extracted: {mhtml_path.name}")
            success_count += 1
            
        except Exception as e:
            print(f"⚠️ No HTML content found in: {mhtml_path.name}")
            error_count += 1
    
    print(f"\n📊 Bronze Summary:")
    print(f"Total: {len(mhtml_files)} | Extracted: {success_count} | Failed: {error_count}")