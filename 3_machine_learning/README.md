# Giai đoạn 3: Học máy (Machine Learning)

Thư mục này chứa các kịch bản xây dựng, huấn luyện và đánh giá các mô hình Học máy để phân tích và dự đoán hành vi, mức độ hài lòng của khách hàng.

## Cấu trúc và Quy trình

Tệp chính: `01_ML_Pipeline.py`

### Phần 3A: Phân cụm khách hàng (Customer Segmentation)
- **Thuật toán**: K-Means Clustering kết hợp PCA (Phân tích thành phần chính).
- **Mục tiêu**: Gom nhóm khách hàng dựa trên các đặc trưng hành vi (Số tiền chi tiêu, Tần suất mua, Độ trung thành...).
- **Kết quả**: Xác định được 4 cụm khách hàng chính (K=4) thông qua phương pháp Elbow.

### Phần 3B: Dự đoán sự hài lòng (Satisfaction Prediction)
- **Mục tiêu**: Phân loại mức độ hài lòng của khách hàng (High Satisfaction).
- **Feature Engineering**: Tạo thêm biến `Engagement_Score` và biến có kiểm soát `Service_Quality_Index` để mô phỏng tính phân loại thực tế.
- **Xử lý mất cân bằng dữ liệu**: Áp dụng **SMOTE** để cân bằng lớp dữ liệu huấn luyện.
- **Mô hình huấn luyện**: So sánh giữa Logistic Regression, Random Forest và XGBoost.
- **Kết quả (Best Model)**:
  - Thuật toán tốt nhất: **Random Forest**
  - Accuracy: **94%**
  - F1-Score: **0.91**
  - ROC-AUC: **0.97**

## Cấu trúc thư mục đầu ra

- `models/`: Chứa các tệp `.pkl` của mô hình đã huấn luyện (`segmentation_model.pkl`, `satisfaction_best_model.pkl`).
- `../processed/ml_charts/`: Chứa các biểu đồ đánh giá và trực quan hóa:
  - `01_elbow_method.png`: **Khuỷu tay (Elbow Method)** - Giúp xác định số lượng cụm khách hàng (K) tối ưu nhất cho thuật toán K-Means (ở đây K=4).
  - `02_pca_clusters.png`: **Biểu đồ phân tán PCA (PCA 2D)** - Trực quan hóa 4 cụm khách hàng trên không gian 2 chiều sau khi ép giảm số lượng biến số, giúp quan sát độ tách biệt giữa các cụm.
  - `04_confusion_matrix.png`: **Ma trận nhầm lẫn (Confusion Matrix)** - Hiện thị số lượng dự đoán đúng/sai thực tế của mô hình tốt nhất (Biết được bao nhiêu người thực sự Hài lòng bị dự đoán nhầm).
  - `05_roc_curve.png`: **Đường cong ROC (ROC Curve)** - Đánh giá tổng quan năng lực phân biệt 2 nhóm (Hài lòng vs Không hài lòng) của mô hình. Đường cong càng cong lên góc trái trên (AUC gần 1) thì mô hình càng hoàn hảo.
  - `06_feature_importance.png`: **Độ quan trọng của đặc trưng (Feature Importance)** - Xếp hạng các biến số (như Thu nhập, Khuyến mãi, Lòng trung thành...) có sức ảnh hưởng lớn nhất đến sự hài lòng của khách hàng theo thuật toán học máy.

## Hướng dẫn sử dụng

Cài đặt thư viện cần thiết trước khi chạy:
```bash
pip install scikit-learn xgboost imbalanced-learn matplotlib numpy pandas
```

Chạy toàn bộ pipeline:
```bash
python 01_ML_Pipeline.py
```
