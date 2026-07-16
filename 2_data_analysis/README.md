# Giai đoạn 2: Phân tích Dữ liệu (Data Analysis)

Thư mục này chứa các kịch bản phân tích dữ liệu và truy vấn SQL phục vụ cho việc nghiên cứu hành vi tiêu dùng thương mại điện tử (Ecommerce Consumer Behavior).

## Danh sách tệp tin

1. **`01_EDA.py`** (và bản notebook `01_EDA.ipynb`)
   - **Mục đích**: Khai phá dữ liệu (Exploratory Data Analysis - EDA) và phân tích tương quan giữa các biến số.
   - **Hoạt động**: Đọc dữ liệu từ CSDL SQLite (`Data/processed/ecommerce.db`), tính toán các chỉ số thống kê, vẽ biểu đồ, sau đó lưu kết quả trực quan vào thư mục `Data/processed/charts`.
   - **Cách chạy**: `python 01_EDA.py`

2. **`02_SQL_Queries.sql`**
   - **Mục đích**: Truy vấn dữ liệu để trích xuất các chỉ số KPI quan trọng.
   - **Hoạt động**: Chứa tập hợp các câu lệnh `SELECT`, `JOIN`, `GROUP BY` chuyên sâu để phân tích dữ liệu.
   - **Cách chạy**: Khởi chạy bằng SQLite:
     ```bash
     sqlite3 ../processed/ecommerce.db ".read 02_SQL_Queries.sql"
     ```

3. **`powerbi/`**
   - Thư mục lưu trữ các tệp Dashboard và báo cáo trực quan hóa từ Power BI (nếu có).

## Yêu cầu môi trường
Đảm bảo đã cài đặt các thư viện cần thiết trước khi chạy:
```bash
pip install pandas matplotlib seaborn scipy
```

## Kết quả đạt được

- **Chỉ số kinh doanh (KPIs)**:
  - Tổng số đơn hàng: 1.000 đơn.
  - Tổng doanh thu: 275.063,88 USD (Giá trị trung bình mỗi đơn: 275,06 USD).
  - Tỷ lệ khách hàng sử dụng mã giảm giá: 52,1%.
  - Tỷ lệ khách hàng thành viên thân thiết (Loyalty Members): 49,1%.
  - Điểm hài lòng trung bình: 5,40 / 10.
- **Kiểm định A/B (A/B Testing)**: Không có sự khác biệt có ý nghĩa thống kê về tỷ lệ hoàn trả hàng giữa nhóm có dùng giảm giá và nhóm không dùng giảm giá.
- **Trực quan hoá dữ liệu**: Trích xuất thành công 23 biểu đồ phân tích (lưu tại `Data/processed/charts`). Chi tiết và ý nghĩa các nhóm biểu đồ chính:
  - *Doanh thu & Phân phối sản phẩm* (`01_purchase_amount_distribution`, `02_revenue_by_channel`, `03_top_categories`): **Ý nghĩa**: Xác định kênh bán hàng và danh mục sản phẩm mang lại doanh thu chủ lực, hiểu rõ phân khúc giá trị đơn hàng.
  - *Chân dung khách hàng* (`04_frequency_by_age`, `11_marital_status_analysis`, `12_education_level_analysis`, `14_top_locations`): **Ý nghĩa**: Phác họa rõ nhân khẩu học (độ tuổi, học vấn, khu vực) để hỗ trợ nhắm mục tiêu (targeting) chính xác hơn.
  - *Đánh giá & Trải nghiệm* (`06_discount_vs_satisfaction`, `15_product_rating_analysis`, `21_education_channel_satisfaction`): **Ý nghĩa**: Đo lường sự tác động của chính sách giảm giá đến độ hài lòng và chất lượng sản phẩm qua lăng kính khách hàng.
  - *Xu hướng & Thời vụ* (`10_monthly_trend`, `16_time_to_decision_analysis`, `17_time_trends_dayofweek_quarter`): **Ý nghĩa**: Phân tích thời gian ra quyết định mua và tính mùa vụ để tối ưu hóa thời điểm tung chiến dịch Marketing.
  - *Marketing & Độ trung thành* (`08_correlation_matrix`, `09_social_media_vs_loyalty`, `19_engagement_with_ads_analysis`, `22_brand_loyalty_multidim`): **Ý nghĩa**: Khám phá mối tương quan tổng thể, đánh giá hiệu suất của quảng cáo và sức ảnh hưởng của mạng xã hội tới lòng trung thành của khách hàng.
- **Truy vấn SQL**: Hoàn thành kết xuất báo cáo KPI và truy vấn sâu từ CSDL SQLite (đã lưu vào tệp `02_SQL_Queries_Output.txt`).
