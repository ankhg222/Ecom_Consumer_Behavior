# 📦 Phase 1: Data Engineering

**Tác giả:** Nguyễn Phước Khang — MSSV: 23110236  
**Mục tiêu:** Xây dựng pipeline ETL tự động để đọc, làm sạch và lưu trữ dữ liệu hành vi mua sắm E-commerce vào cơ sở dữ liệu có cấu trúc, sẵn sàng cho các bước phân tích tiếp theo.

---

## 📁 Cấu Trúc Thư Mục

```
1_data_engineering/
├── etl_pipeline.py        ← Script ETL chính
├── schema.sql             ← Schema bảng + SQL Views
├── etl.log                ← Log file tự động ghi khi chạy
└── dags/
    └── dag_ecommerce_etl.py  ← Airflow DAG (orchestration)
```

---

## 📄 Mô Tả Từng File

### `etl_pipeline.py` — ETL Pipeline chính
Script Python thực hiện toàn bộ quy trình Extract → Transform → Load.

| Hàm | Mô tả |
|-----|-------|
| `extract(path)` | Đọc file CSV gốc vào Pandas DataFrame |
| `transform(df)` | Làm sạch và chuẩn hoá dữ liệu (xem chi tiết bên dưới) |
| `load_csv(df, path)` | Lưu DataFrame đã clean ra file `.csv` |
| `load_db(df, db_path)` | Đẩy dữ liệu vào SQLite database |
| `create_views(db_path)` | Tạo các SQL Views KPI trong database |
| `run_pipeline()` | Hàm tổng, gọi toàn bộ các bước theo thứ tự |

**Các bước Transform chi tiết:**
1. Chuẩn hoá tên cột (bỏ khoảng trắng, ký tự đặc biệt)
2. `Purchase_Amount`: xoá ký tự `$` và khoảng trắng → chuyển sang `float`
3. `Time_of_Purchase`: parse sang kiểu `datetime`, trích xuất thêm `Purchase_Month`, `Purchase_Quarter`, `Purchase_DayOfWeek`
4. `Discount_Used`, `Customer_Loyalty_Program_Member`: chuyển `TRUE/FALSE` → `1/0`
5. Xử lý missing values: drop nếu thiếu ở cột key, fill median/`'Unknown'` cho các cột còn lại
6. Tạo feature phái sinh: `High_Satisfaction` (satisfaction ≥ 7), `Is_Loyal` (brand_loyalty ≥ 4)

**Input/Output:**
```
Input  → Data/Ecommerce_Consumer_Behavior_Analysis_Data.csv  (1000 rows, 28 cột)
Output → Data/processed/ecommerce_clean.csv                  (1000 rows, 33 cột)
       → Data/processed/ecommerce.db                         (SQLite database)
       → etl.log                                             (log file)
```

---

### `schema.sql` — Database Schema + SQL Views

Định nghĩa cấu trúc bảng `orders` và 3 Views KPI sẵn dùng:

| Đối tượng | Mô tả |
|-----------|-------|
| `orders` | Bảng chính chứa toàn bộ 33 cột sau ETL |
| `vw_kpi_overview` | KPIs tổng quan: tổng doanh thu, AOV, return rate, satisfaction, discount usage % |
| `vw_revenue_by_channel` | Doanh thu, AOV, số đơn, satisfaction theo kênh mua (Online/In-Store/Mixed) |
| `vw_demographics` | AOV, tần suất, brand loyalty theo Income Level × Gender × Education |

**Cách dùng Views:**
```sql
-- Mở DB Browser for SQLite hoặc DBeaver, kết nối file ecommerce.db
SELECT * FROM vw_kpi_overview;
SELECT * FROM vw_revenue_by_channel;
SELECT * FROM vw_demographics;
```

---

### `dags/dag_ecommerce_etl.py` — Airflow DAG

Định nghĩa workflow tự động chạy ETL hàng ngày lúc **01:00 SA**.

**Sơ đồ pipeline:**
```
extract_csv → transform_clean → load_to_db → validate_output → notify_done
```

| Task | Mô tả |
|------|-------|
| `extract_csv` | Gọi `extract()`, push số rows vào XCom |
| `transform_clean` | Gọi `transform()`, kiểm tra dữ liệu đầu ra |
| `load_to_db` | Gọi `load_csv()` + `load_db()` + `create_views()` |
| `validate_output` | Kết nối SQLite, assert DB có > 0 rows |
| `notify_done` | In thông báo hoàn thành ra log |

**Cấu hình DAG:**
```python
schedule_interval = '0 1 * * *'   # 01:00 mỗi ngày
retries           = 2              # tự retry 2 lần nếu lỗi
retry_delay       = 5 phút
```

> **Lưu ý:** Airflow yêu cầu Linux/Mac hoặc Docker trên Windows.  
> Trên Windows: chạy `python etl_pipeline.py` trực tiếp là đủ.

---

## ▶️ Cách Chạy

### Chạy thủ công (Windows)
```bash
cd "e:\PhanTichDuLieu\PhanTichDuLieu\23110236_NguyenPhuocKhang_Nhom_8\Data\1_data_engineering"
python etl_pipeline.py
```

### Kết quả chạy thực tế

```text
2026-07-16 17:03:04,554 [INFO] ==================================================
2026-07-16 17:03:04,554 [INFO] ETL Pipeline START
2026-07-16 17:03:04,554 [INFO] Extracting from: E:\PhanTichDuLieu\PhanTichDuLieu\23110236_NguyenPhuocKhang_Nhom_8\Data\Ecommerce_Consumer_Behavior_Analysis_Data.csv
2026-07-16 17:03:04,565 [INFO] Extracted 1000 rows, 28 columns
2026-07-16 17:03:04,565 [INFO] Starting transform...
2026-07-16 17:03:04,590 [INFO] Missing values: 503 -> 0
2026-07-16 17:03:04,591 [INFO] Purchase_Amount outliers (1%-99%): 20 rows (kept)
2026-07-16 17:03:04,592 [INFO] Transform done: 1000 -> 1000 rows
2026-07-16 17:03:04,602 [INFO] Saved processed CSV: E:\PhanTichDuLieu\PhanTichDuLieu\23110236_NguyenPhuocKhang_Nhom_8\Data\processed\ecommerce_clean.csv
2026-07-16 17:03:04,622 [INFO] Loaded 1000 rows to SQLite: E:\PhanTichDuLieu\PhanTichDuLieu\23110236_NguyenPhuocKhang_Nhom_8\Data\processed\ecommerce.db [table: orders]
2026-07-16 17:03:04,633 [INFO] Created 3 SQL views in DB
2026-07-16 17:03:04,633 [INFO] ETL Pipeline DONE in 0.1s
2026-07-16 17:03:04,633 [INFO] ==================================================
```

**Thành quả đạt được:**
- Đã đọc và làm sạch toàn bộ 1000 dòng dữ liệu thô (xử lý thành công 503 missing values).
- Tạo file xuất `ecommerce_clean.csv` chuẩn bị cho bước Machine Learning & Data Science.
- Lưu dữ liệu vào CSDL SQLite `ecommerce.db` (bảng `orders`) và tạo sẵn 3 SQL Views. Sẵn sàng cho phân tích và Power BI.

---

## 🔧 Dependencies

```bash
pip install pandas sqlalchemy
```

SQLite được tích hợp sẵn trong Python, không cần cài thêm.

---

## 📊 Cột Dữ Liệu Sau ETL (33 cột)

| Nhóm | Cột |
|------|-----|
| **Gốc (28 cột)** | Customer_ID, Age, Gender, Income_Level, Marital_Status, Education_Level, Occupation, Location, Purchase_Category, Purchase_Amount, Frequency_of_Purchase, Purchase_Channel, Brand_Loyalty, Product_Rating, Research_Hours, Social_Media_Influence, Discount_Sensitivity, Return_Rate, Customer_Satisfaction, Engagement_with_Ads, Device_Used_for_Shopping, Payment_Method, Time_of_Purchase, Discount_Used, Customer_Loyalty_Program_Member, Purchase_Intent, Shipping_Preference, Time_to_Decision |
| **Phái sinh (5 cột)** | Purchase_Month, Purchase_Quarter, Purchase_DayOfWeek, High_Satisfaction, Is_Loyal |
