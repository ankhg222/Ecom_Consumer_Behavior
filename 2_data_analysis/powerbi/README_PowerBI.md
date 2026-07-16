# Hướng Dẫn Kết Nối PowerBI với SQLite

## 1. Cài ODBC Driver cho SQLite

1. Tải **SQLite ODBC Driver** tại: https://www.ch-werner.de/sqliteodbc/
2. Cài file `sqliteodbc_w64.exe` (Windows 64-bit)

## 2. Kết nối PowerBI Desktop

1. Mở **PowerBI Desktop**
2. **Home → Get Data → ODBC**
3. Data source name: chọn `SQLite3 Datasource`
4. Advanced: Connection string:
   ```
   Database=E:\PhanTichDuLieu\PhanTichDuLieu\23110236_NguyenPhuocKhang_Nhom_8\data\processed\ecommerce.db
   ```
5. Import các tables/views sau:
   - `orders` — bảng chính
   - `vw_kpi_overview` — KPIs tổng quan
   - `vw_revenue_by_channel` — doanh thu theo kênh
   - `vw_demographics` — phân tích nhân khẩu học

## 3. Cấu Trúc Dashboard (3 trang)

### Trang 1 — Executive Overview
| Visual | Fields |
|--------|--------|
| KPI Card | Total Orders (COUNT Customer_ID) |
| KPI Card | Total Revenue (SUM Purchase_Amount) |
| KPI Card | AOV (AVG Purchase_Amount) |
| KPI Card | Avg Satisfaction (AVG Customer_Satisfaction) |
| KPI Card | Return Rate (AVG Return_Rate) |
| Bar Chart | Purchase_Category vs SUM(Purchase_Amount) |
| Donut Chart | Purchase_Channel phân bổ |
| Table | vw_kpi_overview |

### Trang 2 — Customer Demographics
| Visual | Fields |
|--------|--------|
| Slicer | Gender |
| Slicer | Income_Level |
| Slicer | Education_Level |
| Treemap | Location → COUNT(Customer_ID) |
| Scatter | Age (X) vs Purchase_Amount (Y), màu Income_Level |
| Stacked Bar | Age_Group vs AVG(Frequency_of_Purchase) theo Gender |
| Bar | Payment_Method vs COUNT(orders) |

### Trang 3 — Behavioral Analysis
| Visual | Fields |
|--------|--------|
| Matrix | Discount_Sensitivity (row) × Purchase_Intent (col) → AVG(Customer_Satisfaction) |
| Line Chart | Purchase_Month vs SUM(Purchase_Amount) |
| Bar Chart | Social_Media_Influence vs AVG(Brand_Loyalty) |
| Bar Chart | Shipping_Preference vs AVG(Customer_Satisfaction) |
| KPI | Discount Usage % |
| Donut | Loyalty Member vs Non-Member |

## 4. DAX Measures Quan Trọng

```dax
Total Revenue = SUM(orders[Purchase_Amount])

AOV = AVERAGE(orders[Purchase_Amount])

Return Rate % = 
    DIVIDE(SUM(orders[Return_Rate]), COUNT(orders[Customer_ID]))

High Satisfaction % = 
    DIVIDE(
        CALCULATE(COUNT(orders[Customer_ID]), orders[High_Satisfaction] = 1),
        COUNT(orders[Customer_ID])
    )

Discount Usage % = 
    DIVIDE(
        CALCULATE(COUNT(orders[Customer_ID]), orders[Discount_Used] = 1),
        COUNT(orders[Customer_ID])
    ) * 100

Loyalty Member % =
    DIVIDE(
        CALCULATE(COUNT(orders[Customer_ID]), orders[Customer_Loyalty_Program_Member] = 1),
        COUNT(orders[Customer_ID])
    ) * 100
```

## 5. Tips

- Dùng **Conditional Formatting** trên matrix để highlight cell có satisfaction cao/thấp
- Dùng **Sync Slicers** cho Gender/Income để filter đồng bộ giữa các trang
- **Cross-filter** giữa Purchase_Channel và danh mục sản phẩm để drill-down
