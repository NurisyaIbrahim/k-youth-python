# k-youth-python - Data Engineering ETL Pipeline

## Project Description

This project implements a complete ETL (Extract, Transform, Load) pipeline for job listings data using Medallion Architecture. The pipeline extracts job data from MHTML files, cleans and processes HTML content, transforms it into structured JSON, loads it into a SQLite database and performs data quality profiling.

### Pipeline Flow
0_source/*.mhtml → 1_bronze/*.html → 2_silver/*.json → 3_gold/jobs.db
(Extract) --> (Transform) -- > (Load) --> (Profile)


### Results Summary
| Layer | Input | Output | Success Rate |
|-------|-------|--------|--------------|
| Bronze | 100 MHTML | 100 HTML | 100% |
| Silver | 100 HTML | 84 JSON | 84% |
| Gold | 84 JSON | 84 records in DB | 100% |
| Quality | 84 records | 29 HIGH, 55 LOW | - |

---

## Setup Instructions

### Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|----------------|
| Python | 3.14 or higher | `python --version` |
| uv | 0.8.* or higher | `uv --version` |
| Git | Any version | `git --version` |

### Step-by-Step Setup

1. Clone the repository
-powershell-
git clone git@github.com:NurisyaIbrahim/k-youth-python.git
cd k-youth-python/week1

2. Install uv package manager
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
- restart terminal after install it

3. Create and activate virtual environment
uv venv
.venv\Scripts\activate

4. Install dependencies
uv sync

5. Download and extract source data
New-Item -ItemType Directory -Force -Path data/0_source
Expand-Archive -Path ~/Downloads/0_source.zip -DestinationPath data/0_source/


Usage
Available Commands
Command	               Description	            Module
python main.py ingest	Extract MHTML → HTML	   Bronze Layer
python main.py process	Process HTML → JSON	   Silver Layer
python main.py load	   Load JSON → SQLite	   Gold Layer
python main.py profile	Run data quality report	Profiler
python main.py all	   Run full pipeline	All Modules

Run Full Pipeline
python main.py all

Run Individual Modules
python main.py ingest   # Extract 100 MHTML to HTML
python main.py process  # Process 100 HTML to 84 JSON
python main.py load     # Load 84 JSON to SQLite
python main.py profile  # Generate quality report

Expected Outputs
Module 1 - Bronze Layer (ingest)
🥉 Bronze:...
✅ Extracted: 000.mhtml
✅ Extracted: 001.mhtml
...
📊 Bronze Summary:
Total: 100 | Extracted: 100 | Failed: 0

Module 2 - Silver Layer (process)
🥈 Silver:...
⚠️ Missing job_title, description in: file1.html
⚠️ Missing job_title in: file2.html
✅ Processed: file3.html
...
📊 Silver Summary:
Total: 100 | Processed: 84 | Skipped: 16

Module 3 - Gold Layer (load)
🥇 Gold:...
✅ Inserted: file1.json
✅ Inserted: file2.json
...
📊 Gold Summary:
Total: 84 | Inserted: 84 | Skipped: 0

✅ Database created at: data/3_gold/jobs.db

Module 4 - Profiler (profile)
--- DATA QUALITY REPORT ---
Total Records (original): 84
Quality: HIGH=29 | LOW=55
Quarantined: 55 records moved to jobs_quarantine
Missing Values -> job_title: 0, company: 0, description: 0
Avg Description Length: 2694 chars
Shortest Description: 140 chars
   -> source_id: 88882387 | job_title: Senior Back-End Developer
Longest Description: 3004 chars
   -> source_id: 91240902 | job_title: Junior Backend Engineer
----------------------------------------

Project Structure
k-youth-python/
├── week1/
│   ├── data/
│   │   ├── 0_source/      # Raw MHTML files (100 files)
│   │   ├── 1_bronze/      # Extracted HTML files (100 files)
│   │   ├── 2_silver/      # Processed JSON files (84 files)
│   │   └── 3_gold/        # SQLite database (jobs.db)
│   ├── src/
│   │   ├── ingestor.py    # Module 1: MHTML → HTML
│   │   ├── processor.py   # Module 2: HTML → JSON
│   │   ├── loader.py      # Module 3: JSON → SQLite
│   │   ├── profiler.py    # Module 4: Data quality
│   │   └── sql_helper.py  # SQL file loader
│   ├── queries/           # SQL statement files
│   ├── main.py            # CLI orchestrator
│   └── pyproject.toml     # Dependencies
├── week2/                 # Future modules
├── week3/                 # Future modules
├── week4/                 # Future modules
└── README.md              # This file

## Viewing the Database

To view tables in VS Code:
1. Install **SQLite3 Editor** extension
2. Press `Ctrl+Shift+P` → `SQLite: Open Database`
3. Select `week1/data/3_gold/jobs.db`
4. Expand the database in the sidebar

To query using Python:
```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/3_gold/jobs.db'); print(conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]); conn.close()"

                                                                     
                                                                     TECHNICAL REFLECTIONS
### Module 1: The Extractor (Medallion & Lakehouses)
 Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?

Keeping raw HTML files provides flexibility, as the data can be reprocessed anytime if the parsing logic changes, without needing to scrape the website again. It also acts as an audit trail, preserving the original source for verification and ensuring data integrity.

Raw HTML makes debugging easier because developers can inspect the original structure to identify parsing errors or missing fields caused by website changes. It also supports recovery, since corrupted or incomplete processed data can be regenerated by reprocessing the saved raw files.

 ### Module 2: Treatment Plant (ETL vs ELT & Scale)
Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?

Cloud systems prefer ELT because loading raw data first provides cheap storage, greater flexibility, and infinite scalability. This creates an idempotent pipeline, allowing teams to safely re-run transformations on unchanged raw data without risking duplication or corruption. By leveraging powerful distributed cloud engines for post-load transformations, systems become faster and more adaptable to shifting analytics needs.

Sequential processing creates severe bottlenecks by handling files one at a time, which limits scalability and increases network I/O overhead as single machines constantly pull massive datasets. Distributed processing solves this by splitting the workload across multiple machines to run tasks in parallel. Processing data chunks closer to where they are physically stored drastically reduces network I/O, accelerating performance.

### Module 3: The Blueprint & The Vault (Storage & Contracts)
What should happen if an important field like job_title disappears? Why fail early instead of silently inserting nulls into DB? How does INSERT OR IGNORE help prevent duplicate records?

If a critical field like job_title is missing, the system must fail early and raise an error instead of silently inserting NULL values. This prevents inconsistent, low-quality data from corrupting downstream reports and analysis. Failing early isolates the issue immediately, making debugging much easier by alerting developers to parser errors or website structural changes before malformed data spreads through the system.

INSERT OR IGNORE maintains database consistency by automatically skipping records that violate unique constraints or primary keys. This ensures that repeated scraping or data processing runs do not create duplicate entries. By preventing redundant data, it keeps the database clean, reliable and ensures pipeline idempotency.

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)
What happens if processor.py crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?

If processor.py crashes midway, it leaves the dataset incomplete and inconsistent, with some output files generated while others are missing. Recovery becomes entirely manual and inefficient, requiring developers to audit logs to find the exact failure point and restart the process, which increases the risk of human error and data duplication.

Automated orchestration tools eliminate this manual overhead by continuously tracking the success or failure state of every individual task in the pipeline. They automatically manage task dependencies, trigger smart retries on failure and send instant alerts to the team. If a crash occurs, the orchestrator can safely resume the workflow exactly from the last successful step, ensuring a dependable and hands-off pipeline.