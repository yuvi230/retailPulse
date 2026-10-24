
import io
import time
import zipfile
import urllib.request

import pandas as pd
from sqlalchemy import create_engine, text

from src import config as C
from src.logger import get_logger

log = get_logger("extract")

RENAME = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}
def download() -> None:
    if C.RAW_XLSX.exists():
        log.info("Raw file already present: %s", C.RAW_XLSX)
        return
    log.info("Downloading dataset from UCI ...")
    try:
        with urllib.request.urlopen(C.DATASET_URL, timeout=120) as r:
            data = r.read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            member = next(n for n in z.namelist() if n.lower().endswith(".xlsx"))
            C.RAW_DIR.mkdir(parents=True, exist_ok=True)
            with z.open(member) as src, open(C.RAW_XLSX, "wb") as dst:
                dst.write(src.read())
        log.info("Saved %s", C.RAW_XLSX)
    except Exception as e:
        raise SystemExit(
            f"Automatic download failed ({e}).\n"
            "Download manually from https://archive.ics.uci.edu/dataset/502/online+retail+ii\n"
            f"and place the Excel file at: {C.RAW_XLSX}"
        )
def read_sheets() -> pd.DataFrame:
    log.info("Reading Excel (takes 1-3 minutes) ...")
    sheets = pd.read_excel(C.RAW_XLSX, sheet_name=None,
                           dtype={"Invoice": str, "StockCode": str})
    frames = []
    for name, df in sheets.items():
        df = df.rename(columns=RENAME)
        df["source_sheet"] = name
        log.info("Sheet %-12s rows=%s", name, f"{len(df):,}")
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df["customer_id"] = df["customer_id"].astype("Int64")  # nullable int keeps NaN
    df["description"] = df["description"].astype("string")
    return df

def sanity_checks(df: pd.DataFrame) -> None:
    assert set(df.columns) == C.EXPECTED_COLUMNS, \
        f"Unexpected columns: {set(df.columns) ^ C.EXPECTED_COLUMNS}"
    if len(df) != C.EXPECTED_ROWS:
        log.warning("Row count %s differs from expected %s",
                    f"{len(df):,}", f"{C.EXPECTED_ROWS:,}")
    log.info("Date range: %s -> %s", df.invoice_date.min(), df.invoice_date.max())
    log.info("Missing customer_id: %.1f%%", df.customer_id.isna().mean() * 100)
    log.info("Cancelled invoices (start with C): %s",
             f"{df.invoice.str.startswith('C').sum():,}")
    log.info("Exact duplicate rows: %s", f"{df.duplicated().sum():,}")

def load_staging(df: pd.DataFrame) -> int:
    engine = create_engine(C.DB_URL)
    df.to_sql(C.STAGING_TABLE, engine, if_exists="replace",
              index=False, chunksize=50_000)
    with engine.connect() as conn:
        n = conn.execute(text(f"SELECT COUNT(*) FROM {C.STAGING_TABLE}")).scalar()
    log.info("Loaded %s rows into %s", f"{n:,}", C.STAGING_TABLE)
    return n


def main() -> None:
    t0 = time.time()
    download()
    df = read_sheets()
    sanity_checks(df)
    C.PROC_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(C.RAW_PARQUET, index=False)
    log.info("Saved %s", C.RAW_PARQUET)
    n = load_staging(df)
    assert n == len(df), "Row count mismatch between DataFrame and staging table"
    log.info("Day 1 extraction finished in %.1fs", time.time() - t0)


if __name__ == "__main__":
    main()