import sys
from pathlib import Path
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import run_data_profile

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR = Path("data/3_gold")
DB_NAME = "jobs.db"

def run_profiler():
    db_path = GOLD_DIR / DB_NAME
    run_data_profile(db_path)

def run_gold():
    input_dir = SILVER_DIR
    output_dir = GOLD_DIR
    load_all_jsons(input_dir, output_dir)

def run_silver():
    input_dir = BRONZE_DIR
    output_dir = SILVER_DIR
    process_all_html(input_dir, output_dir)

def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    ingest_all_mhtml(input_dir, output_dir)

def show_help():
    print("""
Available commands:
  python main.py ingest   - Extract MHTML to HTML (Bronze layer)
  python main.py process  - Process HTML to JSON (Silver layer)
  python main.py load     - Load JSON to SQLite (Gold layer)
  python main.py profile  - Run quality checks
  python main.py all      - Run entire pipeline
  python main.py help     - Show this help message
    """)

def main():
    # Create necessary directories
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    
    if len(sys.argv) < 2:
        print("Error: No command provided.")
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    match command:
        case "ingest":
            print("\n=== Starting Bronze Layer: Ingestion ===")
            run_bronze()
        case "process":
            print("\n=== Starting Silver Layer: Processing ===")
            run_silver()
        case "load":
            print("\n=== Starting Gold Layer: Loading ===")
            run_gold()
        case "profile":
            print("\n=== Running Data Profiler ===")
            run_profiler()
        case "all":
            print("\n=== Running Complete ETL Pipeline ===")
            run_bronze()
            run_silver()
            run_gold()
            run_profiler()
        case "help":
            show_help()
        case _:
            print(f"Error: Unknown command '{command}'")
            show_help()

if __name__ == "__main__":
    main()