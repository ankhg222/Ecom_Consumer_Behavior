# Giai đoạn 4: Khoa học Dữ liệu (Data Science & Business Insights)

Thư mục này chứa mã nguồn phân tích chuyên sâu (Advanced Analytics) nhằm diễn giải mô hình học máy, thực hiện kiểm định giả thuyết và trích xuất thông tin chi tiết (insights) hữu ích cho doanh nghiệp.

## Tệp chính
- **`01_DataScience_Analysis.py`**: Kịch bản (script) chính thực hiện toàn bộ quy trình Khoa học dữ liệu.

## Các nội dung phân tích (Phases)

### 4A: Phân tích SHAP (SHAP Analysis)
- **Mục tiêu**: Mở "hộp đen" (black-box) của mô hình học máy để xem yếu tố nào ảnh hưởng lớn nhất đến sự hài lòng của khách hàng.
- **Biểu đồ tạo ra**:
  - `01_shap_summary.png`: Biểu đồ tổng quan (Beeswarm) cho thấy tầm quan trọng của tất cả các biến (VD: Thu nhập, Độ tuổi, Thời gian ra quyết định là 3 yếu tố hàng đầu).
  - `02_shap_waterfall.png`: Biểu đồ thác nước giải thích chi tiết cách mô hình đưa ra dự đoán cho một khách hàng cụ thể (tại sao họ hài lòng hoặc không).

### 4B: Kiểm định A/B (A/B Testing)
- **Mục tiêu**: Kiểm tra xem việc áp dụng mã giảm giá (Discount) có thực sự làm giảm tỷ lệ hoàn trả hàng (Return Rate) hay không bằng thống kê khoa học.
- **Phương pháp**: Sử dụng Shapiro-Wilk để kiểm tra phân phối chuẩn, sau đó dùng kiểm định phi tham số Mann-Whitney U Test. Tính toán kích thước ảnh hưởng bằng Cohen's d.
- **Biểu đồ tạo ra**:
  - `04_ab_test.png`: So sánh phân phối tỷ lệ hoàn trả hàng giữa 2 nhóm Có dùng và Không dùng giảm giá.

### 4C: Đúc kết kinh doanh (Business Insights)
Từ dữ liệu, kịch bản tự động xuất ra 5 khuyến nghị hành động (Actionable Insights) cho doanh nghiệp:
1. **Tối ưu Kênh**: Đầu tư marketing vào kênh mang lại Giá trị đơn hàng trung bình (AOV) cao nhất (Kênh Mixed).
2. **Khách hàng thân thiết**: Tiếp tục mở rộng Loyalty Program vì nó thực sự giúp tăng độ hài lòng.
3. **Mạng xã hội**: Tập trung vào Influencer Marketing cho nhóm khách bị ảnh hưởng mạnh bởi Social Media để thu AOV cao.
4. **Nghiên cứu sản phẩm**: Cung cấp mô tả chi tiết vì thời gian nghiên cứu (Research Hours) có tương quan thuận với sự hài lòng.
5. **Quản trị danh mục**: Ưu tiên ngân sách khuyến mãi và tồn kho cho ngành hàng bán chạy nhất (VD: Jewelry & Accessories).

## Hướng dẫn sử dụng
```bash
# Cài đặt thư viện (nếu thiếu)
pip install shap scipy pandas numpy matplotlib seaborn xgboost

# Khởi chạy phân tích
python 01_DataScience_Analysis.py
```
