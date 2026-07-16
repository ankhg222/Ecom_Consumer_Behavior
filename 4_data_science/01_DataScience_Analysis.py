"""
SHAP Analysis + A/B Testing + Business Report
Phase 4: Data Science
Author: 23110236_NguyenPhuocKhang
"""

# ─── 0. Thư viện ─────────────────────────────────────────────────────────────
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import shap
import pickle, os, warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, 'processed', 'ecommerce.db')
MODEL_PKL = os.path.join(BASE_DIR, 'models', 'satisfaction_xgb.pkl')
CHART_DIR = os.path.join(BASE_DIR, 'processed', 'ds_charts')
os.makedirs(CHART_DIR, exist_ok=True)

def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, f"{name}.png"), bbox_inches='tight')
    plt.close()

# ─── 1. Load data + model ────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM orders", conn)
conn.close()

model_data = pickle.load(open(MODEL_PKL, 'rb'))
xgb_model  = model_data['model']
le_map     = model_data['le_map']
FEATURES   = model_data['features']

# Chuẩn bị X
df_ml = df[FEATURES + ['High_Satisfaction']].dropna().copy()
for col in df_ml.select_dtypes(include='object').columns:
    if col in le_map:
        df_ml[col] = le_map[col].transform(df_ml[col].astype(str))
    else:
        from sklearn.preprocessing import LabelEncoder
        df_ml[col] = LabelEncoder().fit_transform(df_ml[col].astype(str))
X = df_ml[FEATURES]

# ─── 2. SHAP Analysis ───────────────────────────────────────────────────────
print("=== PHASE 4A: SHAP Analysis ===")
explainer   = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X)

# SHAP Beeswarm (global)
fig, ax = plt.subplots(figsize=(10, 8))
shap.summary_plot(shap_values, X, plot_type='dot', show=False)
plt.title('SHAP Summary — Factors Affecting Customer Satisfaction', fontsize=13, fontweight='bold')
save("01_shap_beeswarm")

# SHAP Bar (mean importance)
fig, ax = plt.subplots(figsize=(10, 6))
shap.summary_plot(shap_values, X, plot_type='bar', show=False)
plt.title('SHAP Feature Importance (Mean |SHAP|)', fontsize=13, fontweight='bold')
save("02_shap_bar")

# SHAP Waterfall — 1 sample
sample_idx = 0
expected_value = explainer.expected_value
shap.waterfall_plot(shap.Explanation(
    values=shap_values[sample_idx],
    base_values=expected_value,
    data=X.iloc[sample_idx].values,
    feature_names=FEATURES
), show=False)
plt.title('SHAP Waterfall — Sample Customer', fontsize=13, fontweight='bold')
save("03_shap_waterfall")

print("Top 5 features theo SHAP:")
mean_shap = pd.Series(np.abs(shap_values).mean(axis=0), index=FEATURES).sort_values(ascending=False)
print(mean_shap.head(5).to_string())

# ─── 3. CAUSAL INFERENCE (PSM) ─────────────────────────────────────────────────────────
print("\n=== PHASE 4B: Causal Inference — Propensity Score Matching ===")

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

# Treatment: Discount_Used (1=Treated, 0=Control)
# Outcome: Return_Rate
# Confounders: Age, Income_Level, Brand_Loyalty (these might affect both discount usage and return rate)
confounders = ['Age', 'Income_Level', 'Brand_Loyalty']
df_psm = df.copy().dropna(subset=confounders + ['Discount_Used', 'Return_Rate'])

# Encode categorical confounders
for col in confounders:
    if not pd.api.types.is_numeric_dtype(df_psm[col]):
        df_psm[col] = LabelEncoder().fit_transform(df_psm[col].astype(str))

X_psm = df_psm[confounders]
T_psm = df_psm['Discount_Used']

# Tính Propensity Score
lr = LogisticRegression(random_state=42)
lr.fit(X_psm, T_psm)
df_psm['Propensity_Score'] = lr.predict_proba(X_psm)[:, 1]

# Chia Treated và Control
treated = df_psm[df_psm['Discount_Used'] == 1]
control = df_psm[df_psm['Discount_Used'] == 0]

# Matching (1-to-1 Nearest Neighbor)
nn = NearestNeighbors(n_neighbors=1, metric='euclidean')
nn.fit(control[['Propensity_Score']])
distances, indices = nn.kneighbors(treated[['Propensity_Score']])

# Tạo tập dữ liệu đã match
matched_control = control.iloc[indices.flatten()]
matched_data = pd.concat([treated, matched_control])

# Tính Average Treatment Effect (ATE)
ate = treated['Return_Rate'].mean() - matched_control['Return_Rate'].mean()
print(f"Average Treatment Effect (ATE) cua Discount len Return Rate: {ate:.4f}")

# Kiểm định T-test trên tập đã match
t_stat, p_val = stats.ttest_ind(treated['Return_Rate'], matched_control['Return_Rate'])
print(f"T-test (Matched): p-value = {p_val:.4f}")
print(f"Kết luận: {'Discount THỰC SỰ ảnh hưởng tới Return Rate' if p_val < 0.05 else 'Discount KHÔNG gây ảnh hưởng thực sự tới Return Rate'}")

# Visualize PSM
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(treated['Propensity_Score'], bins=20, alpha=0.5, label='Treated (Discount)', color='steelblue')
axes[0].hist(control['Propensity_Score'], bins=20, alpha=0.5, label='Control (No Discount)', color='coral')
axes[0].set_title('Trước khi Match: Phân bố Propensity Score')
axes[0].legend()

axes[1].hist(treated['Propensity_Score'], bins=20, alpha=0.5, label='Treated (Discount)', color='steelblue')
axes[1].hist(matched_control['Propensity_Score'], bins=20, alpha=0.5, label='Matched Control', color='coral')
axes[1].set_title('Sau khi Match: Phân bố PS đã cân bằng')
axes[1].legend()
save("04_psm_matching")

# ─── 4. CUSTOMER LIFETIME VALUE (CLV) ───────────────────────────────────────────────────
print("\n=== PHASE 4C: Customer Lifetime Value (CLV) ===")

# Giả sử Churn Rate = 1 - Customer_Satisfaction / 10 (càng hài lòng càng ít churn)
# CLV = (Purchase_Amount * Frequency_of_Purchase) / Churn_Rate
df['Churn_Rate'] = 1.0 - (df['Customer_Satisfaction'] / 10.0)
df['Churn_Rate'] = df['Churn_Rate'].replace(0, 0.05) # Tránh chia cho 0
df['CLV'] = (df['Purchase_Amount'] * df['Frequency_of_Purchase']) / df['Churn_Rate']

print(f"Mean CLV: ${df['CLV'].mean():.2f}")

# Phân lớp CLV
df['CLV_Segment'] = pd.qcut(df['CLV'], q=3, labels=['Low', 'Medium', 'High'])

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x='CLV_Segment', y='Purchase_Amount', data=df, ax=ax, palette='Set2')
ax.set_title('Customer Lifetime Value Segments vs Purchase Amount', fontsize=12, fontweight='bold')
save("05_clv_segments")

# ─── 5. BUSINESS INSIGHTS ───────────────────────────────────────────────────
print("\n=== PHASE 4D: Business Insights ===")

insights = []

# Insight 1: Kênh mua vs AOV
ch = df.groupby('Purchase_Channel')['Purchase_Amount'].mean().sort_values(ascending=False)
top_channel = ch.index[0]
insights.append(f"1. Kênh '{top_channel}' có AOV cao nhất (${ch.iloc[0]:.2f}). Ưu tiên tối ưu ROI Marketing.")

# Insight 2: Loyalty program effect
loy = df.groupby('Customer_Loyalty_Program_Member')['Customer_Satisfaction'].mean()
diff = loy.get(1, 0) - loy.get(0, 0)
insights.append(f"2. Loyalty Program tăng Hài Lòng thêm {diff:.2f} điểm. Cần mở rộng quy mô thẻ thành viên.")

# Insight 3: Social media
sm = df.groupby('Social_Media_Influence')['Purchase_Amount'].mean().sort_values(ascending=False)
insights.append(f"3. Social Media ảnh hưởng trực tiếp đến AOV (${sm.iloc[0]:.2f}). Đẩy mạnh Influencer Campaigns.")

# Insight 4: Causal Inference (Discount)
insights.append(f"4. Theo Causal Inference (PSM), ATE của Discount lên Return Rate là {ate:.4f}. {'Cần xem lại chính sách giảm giá.' if ate > 0 else 'Khuyến mãi đang phát huy tốt.'}")

# Insight 5: CLV
high_clv = df[df['CLV_Segment'] == 'High']
insights.append(f"5. Khách hàng 'High CLV' chiếm {len(high_clv)} người với chi tiêu cao. Phát triển dịch vụ VIP Care cho nhóm này.")

print("\n--- ACTIONABLE BUSINESS INSIGHTS ---")
for ins in insights:
    print(f"  ✓ {ins}")

# ─── 6. Business Summary Chart ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('off')
y_pos = 0.95
ax.text(0.5, 1.02, 'Ecommerce Consumer Behavior — Advanced Business Insights',
        ha='center', va='top', fontsize=14, fontweight='bold', transform=ax.transAxes)
for i, ins in enumerate(insights):
    ax.text(0.02, y_pos - i*0.16, f"• {ins}", va='top', fontsize=10,
            transform=ax.transAxes, wrap=True)
save("06_business_summary")
print("\nPhase 4 done!")
