# 🛒 Đồ Án Phân Tích Hành Vi Người Tiêu Dùng Thương Mại Điện Tử (Ecommerce Consumer Behavior Analysis)

> **Thực hiện bởi:** Nguyễn Phước Khang — MSSV: 23110236 — Nhóm 8  
> **Bộ dữ liệu (Dataset):** Dữ liệu hành vi mua sắm thương mại điện tử (~1000 bản ghi, 28 trường dữ liệu)  
> **Ngôn ngữ & Công nghệ cốt lõi:** Python, SQL, SQLite, Apache Airflow, PowerBI, Scikit-learn, UMAP, XGBoost/Random Forest, SHAP, Causal Inference, Streamlit.

---

## 🌟 1. Giới Thiệu & Bài Toán Kinh Doanh (Business Problem)
Trong bối cảnh Thương mại điện tử (E-commerce) cạnh tranh khốc liệt, việc chỉ nhìn vào báo cáo doanh thu tổng (Revenue) là không đủ. Bài toán đặt ra cho đồ án này là ứng dụng toàn diện quy trình **Khoa học dữ liệu (Data Science Lifecycle)** để giải quyết các vấn đề sâu hơn:
1. **Phân cụm khách hàng (Customer Segmentation):** Khách hàng nào là "gà đẻ trứng vàng"? Ai sắp rời bỏ?
2. **Dự đoán hài lòng (Satisfaction Prediction):** Yếu tố nào quyết định một khách hàng sẽ đánh giá 5 sao hay hoàn trả hàng?
3. **Đánh giá hiệu quả chiến dịch (Causal Inference):** Việc doanh nghiệp tung "Mã giảm giá" có thực sự giúp giảm tỷ lệ hoàn trả hàng (Return Rate) hay chỉ đang lãng phí tiền?
4. **Tối đa hóa Giá trị vòng đời (Customer Lifetime Value - CLV).**

Đồ án được thiết kế chuẩn chỉnh từ khâu làm sạch dữ liệu (Data Engineering) cho đến xây dựng Mô hình AI và Triển khai trực quan hóa (Web Deployment).

---

## 🗂️ 2. Chi Tiết 5 Giai Đoạn Của Dự Án (The 5 Phases)

### 🛠️ Giai đoạn 1: Data Engineering (Kỹ Thuật Dữ Liệu)
- **Mục tiêu:** Xử lý dữ liệu thô (Raw CSV) chứa nhiều giá trị rỗng (NULL), nhiễu và định dạng sai.
- **Kỹ thuật:** Imputation (Median cho biến số, Mode cho biến phân loại), chuẩn hóa chuỗi văn bản.
- **Lưu trữ:** Tạo Data Warehouse thu nhỏ bằng **SQLite**. Dữ liệu sạch được load vào Database.

### 📈 Giai đoạn 2: Data Analysis & Business Intelligence (Phân Tích Dữ Liệu)
- **EDA (Exploratory Data Analysis):** Sử dụng `matplotlib` và `seaborn` sinh ra hơn 20 biểu đồ tĩnh từ cơ bản (Phân phối, Heatmap) đến phức tạp (Đa biến, Boxplot) để tìm ra tương quan bề mặt.
- **PowerBI & SQL:** Cung cấp sẵn các `SQL Queries` (tính AOV, tổng doanh thu theo kênh) phục vụ trực tiếp cho việc load lên Dashboard của PowerBI.

### 🤖 Giai đoạn 3: Machine Learning (Học Máy & Phân Cụm)
- **Phân cụm theo mô hình RFM (K-Means + UMAP):** 
  - Thay vì phân cụm dựa trên các biến thô ngẫu nhiên, mô hình tự động chuyển đổi sang 3 chỉ số kinh điển trong Marketing: **Recency (Gần đây), Frequency (Tần suất), Monetary (Giá trị)**.
  - Kết hợp điểm `Silhouette Score` và `Elbow` để chọn ra số cụm tối ưu ($K=4$).
  - **Giảm chiều dữ liệu bằng UMAP:** Thay thế thuật toán PCA cũ kỹ bằng `UMAP`, giúp bảo toàn cấu trúc phi tuyến tính, tạo ra ranh giới cực kỳ sắc nét giữa 4 nhóm khách hàng (Tiềm năng, Ngủ đông, Trung thành, Rời bỏ).
- **Dự đoán độ hài lòng (Satisfaction Prediction):**
  - Giải quyết bài toán mất cân bằng dữ liệu (Imbalanced Data) bằng thuật toán **SMOTE** (Sinh mẫu thiểu số).
  - So sánh `Logistic Regression`, `XGBoost` và `Random Forest`. **Random Forest** đạt hiệu suất cực cao (F1-Score > 0.91, ROC-AUC > 0.97).

### 🧬 Giai đoạn 4: Advanced Data Science (Khoa Học Dữ Liệu Chuyên Sâu)
- **Explainable AI (SHAP):** Biến mô hình AI từ "Hộp đen" thành "Hộp trắng". Dùng `SHAP Beeswarm` và `SHAP Waterfall` để giải thích cụ thể lý do (VD: Khách Hài lòng vì Product Rating cao hay vì Shipping nhanh).
- **Suy luận Nhân quả (Causal Inference - Propensity Score Matching):** Dùng PSM để loại bỏ nhiễu (Confounders) và đánh giá Tác động điều trị trung bình (ATE). Phá vỡ lầm tưởng: *Mã giảm giá (Discount) KHÔNG thực sự làm giảm tỷ lệ trả hàng.*
- **Phân lớp Customer Lifetime Value (CLV):** Áp dụng công thức Tần suất x Giá trị / Churn Rate để phân nhóm giá trị vòng đời dài hạn.

### 🌐 Giai đoạn 5: Deployment (Triển Khai Dashboard)
Đóng gói toàn bộ mô hình và số liệu thành ứng dụng Web đa năng sử dụng **Streamlit**.
- Giao diện gồm 5 trang tương tác.
- Tự động Cache (bộ nhớ đệm) để tăng tốc độ load dữ liệu khổng lồ.

---

## ⚙️ 3. Kiến Trúc Thư Mục (Project Structure)

```text
📦 Ecommerce_Data_Project
├── 1_data_engineering/          ← Script ETL_Pipeline làm sạch & Load Database
├── 2_data_analysis/             ← Script EDA sinh 20+ Biểu đồ & SQL Code cho PowerBI
├── 3_machine_learning/          ← Pipeline Huấn luyện AI (RFM, UMAP, SMOTE, RandomForest)
├── 4_data_science/              ← Script Phân tích SHAP, PSM (Nhân quả) & CLV
├── app/                         ← Web App Streamlit (Hiển thị toàn bộ đồ án)
├── models/                      ← Chứa Models AI đã lưu (.pkl)
├── processed/                   ← Chứa DB SQLite (ecommerce.db) và toàn bộ biểu đồ xuất ra
└── requirements.txt             ← Thư viện môi trường
```

---

## 🚀 4. Hướng Dẫn Cài Đặt Và Vận Hành Toàn Bộ Dự Án

*Lưu ý: Mở Terminal/Command Prompt và dùng lệnh `cd` chuyển vào thư mục dự án trước khi chạy.*

### Bước 1. Chuẩn bị môi trường Python
```bash
pip install -r requirements.txt
```
*(Nếu quá trình chạy gặp lỗi thiếu thư viện SHAP hoặc mất cân bằng, chạy lệnh bổ sung: `pip install shap imbalanced-learn umap-learn`)*

### Bước 2. Xây dựng Data Warehouse
```bash
cd 1_data_engineering
python etl_pipeline.py
cd ..
```
*Kết quả:* Dữ liệu thô được làm sạch triệt để và nạp vào CSDL `processed/ecommerce.db`.

### Bước 3. Khám Phá Dữ Liệu Bề Mặt (EDA)
```bash
cd 2_data_analysis
python 01_EDA.py
cd ..
```
*Kết quả:* Các biểu đồ cơ bản được sinh ra trong `processed/charts/`.

### Bước 4. Chạy Khối Học Máy (Machine Learning)
```bash
cd 3_machine_learning
python 01_ML_Pipeline.py
cd ..
```
*Kết quả:* Huấn luyện thành công các mô hình AI. Mô hình `segmentation_model.pkl` và `satisfaction_best_model.pkl` được xuất ra thư mục `models/`. Các biểu đồ đánh giá (Confusion Matrix, ROC, UMAP 2D) lưu tại `processed/ml_charts/`.

### Bước 5. Chạy Phân Tích Khoa Học Dữ Liệu (SHAP & Nhân Quả)
*Đặc biệt: Bật cờ `-X utf8` trên Windows để tránh lỗi in Tiếng Việt có dấu.*
```bash
cd 4_data_science
python -X utf8 01_DataScience_Analysis.py
cd ..
```
*Kết quả:* Biểu đồ tính toán ATE, CLV và giải thích SHAP lưu tại `processed/ds_charts/`.

### Bước 6. Triển Khai Lên Web Dashboard
```bash
streamlit run app/app.py
```
*Kết quả:* Trình duyệt tự động mở trang `http://localhost:8501`. Tất cả tinh hoa của dự án đều nằm trên Web này!

---

## 💡 5. Điểm Nhấn Phân Tích Kinh Doanh (Key Actionable Insights)

Sau khi hệ thống phân tích vận hành hoàn chỉnh, đây là **5 Insight cốt lõi** mang về cho Doanh nghiệp:

1. **Khách hàng High CLV cực kỳ giá trị:** Tệp khách hàng được phân cụm vào nhóm "Trung Thành" (RFM) đem lại dòng tiền khổng lồ dài hạn. Doanh nghiệp phải ưu tiên ngân sách cấp thẻ VIP và có chế độ chăm sóc Priority 1:1 cho nhóm này.
2. **Ảo tưởng về Mã Giảm Giá:** Thuật toán suy luận nhân quả **Propensity Score Matching (PSM)** đã ghép cặp so sánh và chứng minh: Việc cho khách hàng dùng Discount hoàn toàn KHÔNG làm giảm tỷ lệ trả hàng (Return Rate). Doanh nghiệp đang lãng phí tiền Marketing. Giải pháp là cắt giảm voucher và đầu tư vào Khâu Kiểm Định Chất Lượng (QA) sản phẩm.
3. **Mạng xã hội thúc đẩy Giỏ hàng (AOV):** Những cá nhân có mức độ tương tác Mạng xã hội cao (High Social Media Influence) tạo ra Giá trị trung bình đơn (AOV) lên tới gần $285. Influencer Marketing đang đi đúng hướng.
4. **Sản phẩm cốt lõi:** Bất chấp khách hàng mua qua In-Store hay Online, ngành hàng **Jewelry & Accessories (Trang sức)** luôn là trụ cột sinh lời lớn nhất.
5. **Chăm sóc đúng "Huyệt":** Nhờ `SHAP Waterfall`, mô hình chỉ ra rằng **Engagement_Score** và **Product_Rating** đóng vai trò sinh tử quyết định sự hài lòng. Nếu đánh giá sản phẩm thấp, dù có bù đắp bằng bất kỳ dịch vụ hậu mãi nào thì xác suất giữ chân khách hàng vẫn tiệm cận 0.

---
**© 2026 Nguyễn Phước Khang** — *Sản phẩm mã nguồn mở phục vụ quá trình học tập, nghiên cứu môn học Phân Tích Dữ Liệu.*
📧 **Email liên hệ:** khangnguyen2x0@gmail.com
