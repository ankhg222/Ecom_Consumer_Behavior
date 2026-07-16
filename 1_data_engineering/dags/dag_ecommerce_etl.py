"""
Airflow DAG - Ecommerce ETL Pipeline
Phase 1: Data Engineering
Author: 23110236_NguyenPhuocKhang

Schedule: Chạy hàng ngày lúc 01:00 SA
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Thêm thư mục gốc vào sys.path để import etl_pipeline
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

default_args = {
    'owner': 'khang_23110236',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# ─── Task functions ────────────────────────────────────────────────────────────
def task_extract(**context):
    from etl_pipeline import extract, RAW_PATH
    df = extract(RAW_PATH)
    context['ti'].xcom_push(key='row_count', value=len(df))
    print(f"[EXTRACT] {len(df)} rows loaded")


def task_transform(**context):
    from etl_pipeline import extract, transform, RAW_PATH
    df_raw = extract(RAW_PATH)
    df_clean = transform(df_raw)
    context['ti'].xcom_push(key='clean_row_count', value=len(df_clean))
    print(f"[TRANSFORM] {len(df_clean)} rows after cleaning")


def task_load(**context):
    from etl_pipeline import extract, transform, load_csv, load_db
    from etl_pipeline import RAW_PATH, PROCESSED_PATH, DB_PATH
    df_raw   = extract(RAW_PATH)
    df_clean = transform(df_raw)
    load_csv(df_clean, PROCESSED_PATH)
    load_db(df_clean, DB_PATH)
    print(f"[LOAD] Saved to {PROCESSED_PATH} and {DB_PATH}")


def task_validate(**context):
    import sqlite3
    from etl_pipeline import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    assert count > 0, "Validation FAILED: 0 rows in DB"
    print(f"[VALIDATE] DB có {count} rows — OK")


# ─── DAG definition ───────────────────────────────────────────────────────────
with DAG(
    dag_id='ecommerce_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for Ecommerce Consumer Behavior dataset',
    schedule_interval='0 1 * * *',     # mỗi ngày 01:00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ecommerce', 'etl', 'data-engineering'],
) as dag:

    t_extract = PythonOperator(
        task_id='extract_csv',
        python_callable=task_extract,
    )

    t_transform = PythonOperator(
        task_id='transform_clean',
        python_callable=task_transform,
    )

    t_load = PythonOperator(
        task_id='load_to_db',
        python_callable=task_load,
    )

    t_validate = PythonOperator(
        task_id='validate_output',
        python_callable=task_validate,
    )

    t_notify = BashOperator(
        task_id='notify_done',
        bash_command='echo "ETL completed at $(date). DB updated successfully."',
    )

    # Pipeline order
    t_extract >> t_transform >> t_load >> t_validate >> t_notify
