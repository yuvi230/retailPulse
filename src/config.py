"""Central configuration. Every other module imports paths and settings from here."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
OUT_DIR = ROOT / "outputs"
LOG_DIR = ROOT / "logs"
SQL_DIR = ROOT / "sql"

DATASET_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
RAW_XLSX = RAW_DIR / "online_retail_II.xlsx"
RAW_PARQUET = PROC_DIR / "raw_combined.parquet"

# SQLite needs no setup. To use PostgreSQL later, change only this line:
# DB_URL = "postgresql+psycopg2://user:password@localhost:5432/retailpulse"
DB_URL = f"sqlite:///{ROOT / 'retailpulse.db'}"

STAGING_TABLE = "stg_online_retail"

# Expected values for sanity checks
EXPECTED_ROWS = 1_067_371
EXPECTED_COLUMNS = {
    "invoice", "stock_code", "description", "quantity",
    "invoice_date", "price", "customer_id", "country", "source_sheet",
}