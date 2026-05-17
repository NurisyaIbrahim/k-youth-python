# src/sql_helper.py
from pathlib import Path

def load_sql(query_name):
    """Load SQL query from file"""
    query_path = Path(__file__).parent.parent / "queries" / f"{query_name}.sql"
    
    if not query_path.exists():
        raise FileNotFoundError(f"SQL file not found: {query_path}")
    
    with open(query_path, 'r', encoding='utf-8') as f:
        return f.read()
