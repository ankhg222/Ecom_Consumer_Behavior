"""
ETL Pipeline - Ecommerce Consumer Behavior
Phase 1: Data Engineering
Author: 23110236_NguyenPhuocKhang
"""

import pandas as pd
import sqlite3
import os
import logging
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────────
_BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Data/
RAW_PATH       = os.path.join(_BASE, 'Ecommerce_Consumer_Behavior_Analysis_Data.csv')
PROCESSED_PATH = os.path.join(_BASE, 'processed', 'ecommerce_clean.csv')
DB_PATH        = os.path.join(_BASE, 'processed', 'ecommerce.db')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('etl.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ─── Extract ──────────────────────────────────────────────────────────────────
def extract(path: str) -> pd.DataFrame:
    log.info(f"Extracting from: {path}")
    df = pd.read_csv(path)
    log.info(f"Extracted {len(df)} rows, {df.shape[1]} columns")
    return df


# ─── Transform ────────────────────────────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Starting transform...")
    original_len = len(df)

    # 1. Rename columns: chuẩn hoá tên
    df.columns = df.columns.str.strip().str.replace(r'[\s\(\)]', '_', regex=True)
    df.rename(columns={
        'Time_Spent_on_Product_Research_hours_': 'Research_Hours'
    }, inplace=True)

    # 2. Purchase_Amount: "$333.80 " → 333.80
    df['Purchase_Amount'] = (
        df['Purchase_Amount']
        .astype(str)
        .str.replace(r'[$,\s]', '', regex=True)
        .astype(float)
    )

    # 3. Time_of_Purchase → datetime
    df['Time_of_Purchase'] = pd.to_datetime(df['Time_of_Purchase'], errors='coerce')
    df['Purchase_Month'] = df['Time_of_Purchase'].dt.month
    df['Purchase_Quarter'] = df['Time_of_Purchase'].dt.quarter
    df['Purchase_DayOfWeek'] = df['Time_of_Purchase'].dt.dayofweek  # 0=Mon

    # 4. Boolean columns
    bool_cols = ['Discount_Used', 'Customer_Loyalty_Program_Member']
    for col in bool_cols:
        df[col] = df[col].astype(str).str.upper().map({'TRUE': 1, 'FALSE': 0})

    # 5. Strip whitespace từ các cột string
    str_cols = df.select_dtypes(include='str').columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

    # 6. Xử lý missing values
    missing_before = df.isnull().sum().sum()
    df.dropna(subset=['Customer_ID', 'Purchase_Amount', 'Customer_Satisfaction'], inplace=True)
    for col in ['Age', 'Research_Hours', 'Time_to_Decision']:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include='str').columns:
        df[col] = df[col].fillna('Unknown')
    missing_after = df.isnull().sum().sum()
    log.info(f"Missing values: {missing_before} -> {missing_after}")

    # 7. Tạo thêm feature phái sinh
    df['High_Satisfaction'] = (df['Customer_Satisfaction'] >= 7).astype(int)
    df['Is_Loyal'] = (df['Brand_Loyalty'] >= 4).astype(int)

    # 8. Outlier check cho Purchase_Amount (IQR)
    q1, q3 = df['Purchase_Amount'].quantile([0.01, 0.99])
    outliers = ((df['Purchase_Amount'] < q1) | (df['Purchase_Amount'] > q3)).sum()
    log.info(f"Purchase_Amount outliers (1%-99%): {outliers} rows (kept)")

    log.info(f"Transform done: {original_len} -> {len(df)} rows")
    return df


# ─── Load ─────────────────────────────────────────────────────────────────────
def load_csv(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    log.info(f"Saved processed CSV: {path}")


def load_db(df: pd.DataFrame, db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql('orders', conn, if_exists='replace', index=False)
    conn.close()
    log.info(f"Loaded {len(df)} rows to SQLite: {db_path} [table: orders]")


def create_views(db_path: str):
    """Tạo SQL Views (KPIs) trong DB."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        log.warning(f"schema.sql not found at {schema_path}, skipping views.")
        return
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    view_stmts = [s.strip() for s in sql.split(';') if 'CREATE VIEW' in s]
    for stmt in view_stmts:
        if stmt:
            conn.execute(stmt)
    conn.commit()
    conn.close()
    log.info(f"Created {len(view_stmts)} SQL views in DB")


# ─── Main ─────────────────────────────────────────────────────────────────────
def run_pipeline():
    start = datetime.now()
    log.info("=" * 50)
    log.info("ETL Pipeline START")

    df_raw  = extract(RAW_PATH)
    df_clean = transform(df_raw)
    load_csv(df_clean, PROCESSED_PATH)
    load_db(df_clean, DB_PATH)
    create_views(DB_PATH)

    elapsed = (datetime.now() - start).total_seconds()
    log.info(f"ETL Pipeline DONE in {elapsed:.1f}s")
    log.info("=" * 50)
    return df_clean


if __name__ == '__main__':
    run_pipeline()
