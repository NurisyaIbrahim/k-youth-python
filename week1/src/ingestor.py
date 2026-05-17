# src/ingestor.py
import re
import quopri
import base64
import logging
from pathlib import Path
from email import policy
from email.parser import BytesParser

logger = logging.getLogger(__name__)

def ingest_all_mhtml(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        logger.warning(f"⚠️ Input directory '{input_dir}' does not exist.")
        return
    
    mhtml_files = list(input_path.glob("*.mhtml")) + list(input_path.glob("*.mht"))
    
    if not mhtml_files:
        logger.warning(f"⚠️ No .mhtml files found in '{input_dir}'.")
        return
    
    # KEEP print() for header
    print("🥉 Bronze:...")
    
    extracted = 0
    failed = 0
    total = len(mhtml_files)
    
    for mhtml_path in mhtml_files:
        try:
            with open(mhtml_path, 'rb') as f:
                mhtml_data = f.read()
            
            msg = BytesParser(policy=policy.default).parsebytes(mhtml_data)
            html_content = None
            
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    payload = part.get_payload()
                    encoding = part.get('Content-Transfer-Encoding', '').lower()
                    
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
            
            #logging 
            if html_content is None:
                logger.warning(f"⚠️ Missing description in: {mhtml_path.name}")
                failed += 1
                continue
            
            output_file = output_path / f"{mhtml_path.stem}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            

            logger.info(f"✅ Processed file: {mhtml_path.name}")
            extracted += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to process: {mhtml_path.name} | Reason: {e}")
            failed += 1
    
    # KEEP print() for summary
    print(f"\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")