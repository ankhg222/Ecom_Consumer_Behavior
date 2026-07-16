"""
EDA + Correlation Analysis - Ecommerce Consumer Behavior
Phase 2: Data Analyst (⭐ Trọng tâm)
Author: 23110236_NguyenPhuocKhang

Cách chạy:
  pip install pandas matplotlib seaborn scipy sqlite3
  jupyter notebook 01_EDA.py  (hoặc đổi sang .ipynb)
"""

# ─── 0. Thư viện ────────────────────────────────────────────────────────────
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from scipy import stats
import warnings
import os

warnings.filterwarnings('ignore')
plt.rcParams['figure.dpi'] = 120
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_palette("husl")

# Path tuyệt đối — hoạt động cả khi chạy .py lẫn Jupyter .ipynb
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_BASE, 'processed', 'ecommerce.db')
OUT_DIR = os.path.join(_BASE, 'processed', 'charts')
os.makedirs(OUT_DIR, exist_ok=True)

def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"{name}.png"), bbox_inches='tight')
    plt.close()

# ─── 1. Load Data ────────────────────────────────────────────────────────────
conn = pd.read_sql_query("SELECT * FROM orders", sqlite3.connect(DB_PATH))
df = conn.copy()
print(f"Shape: {df.shape}")
print(df.dtypes)
print("\nBasic stats:")
print(df.describe())

# ─── 2. KPIs Tổng Quan ──────────────────────────────────────────────────────
print("\n=== KPIs ===")
kpis = {
    "Total Orders":       len(df),
    "Total Revenue ($)":  f"{df['Purchase_Amount'].sum():,.2f}",
    "AOV ($)":            f"{df['Purchase_Amount'].mean():,.2f}",
    "Avg Satisfaction":   f"{df['Customer_Satisfaction'].mean():.2f}/10",
    "Avg Return Rate":    f"{df['Return_Rate'].mean():.3f}",
    "Discount Usage %":   f"{df['Discount_Used'].mean()*100:.1f}%",
    "Loyalty Members %":  f"{df['Customer_Loyalty_Program_Member'].mean()*100:.1f}%",
}
for k, v in kpis.items():
    print(f"  {k:<25} {v}")

# ─── 3. Phân phối Purchase Amount ──────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(df['Purchase_Amount'], bins=30, color='steelblue', edgecolor='white')
axes[0].set_title('Phân phối Purchase Amount', fontsize=13)
axes[0].set_xlabel('USD')
axes[1].boxplot(df['Purchase_Amount'], vert=False, patch_artist=True,
                boxprops=dict(facecolor='steelblue', alpha=0.7))
axes[1].set_title('Boxplot Purchase Amount', fontsize=13)
fig.suptitle('Distribution of Purchase Amount', fontsize=15, fontweight='bold')
save("01_purchase_amount_distribution")

# ─── 4. Doanh thu theo Purchase Channel ─────────────────────────────────────
channel_df = df.groupby('Purchase_Channel').agg(
    total_revenue=('Purchase_Amount', 'sum'),
    num_orders=('Customer_ID', 'count'),
    avg_satisfaction=('Customer_Satisfaction', 'mean')
).reset_index().sort_values('total_revenue', ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(channel_df['Purchase_Channel'], channel_df['total_revenue'],
              color=['#2E86AB', '#A23B72', '#F18F01'])
ax.bar_label(bars, fmt='$%.0f', padding=3)
ax.set_title('Tổng Doanh Thu theo Kênh Mua Hàng', fontsize=13, fontweight='bold')
ax.set_ylabel('Total Revenue ($)')
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:,.0f}'))
save("02_revenue_by_channel")

# ─── 5. Top 8 danh mục sản phẩm ─────────────────────────────────────────────
cat_df = df.groupby('Purchase_Category')['Purchase_Amount'].sum().sort_values(ascending=True).tail(8)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_df.index, cat_df.values, color=sns.color_palette("husl", 8))
ax.bar_label(bars, fmt='$%.0f', padding=3)
ax.set_title('Top 8 Danh Mục Theo Doanh Thu', fontsize=13, fontweight='bold')
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:,.0f}'))
save("03_top_categories")

# ─── 6. Nhân khẩu học: Frequency theo Age group ─────────────────────────────
df['Age_Group'] = pd.cut(df['Age'], bins=[18, 25, 35, 45, 55, 70],
                          labels=['18-25', '26-35', '36-45', '46-55', '55+'])
age_df = df.groupby('Age_Group', observed=True)['Frequency_of_Purchase'].mean()
fig, ax = plt.subplots(figsize=(9, 5))
age_df.plot(kind='bar', ax=ax, color='coral', edgecolor='white')
ax.set_title('Tần Suất Mua Theo Nhóm Tuổi (trung bình)', fontsize=13, fontweight='bold')
ax.set_ylabel('Avg Frequency')
ax.set_xlabel('Age Group')
ax.tick_params(axis='x', rotation=0)
save("04_frequency_by_age")

# ─── 7. Gender × Income → AOV heatmap ──────────────────────────────────────
pivot = df.pivot_table(values='Purchase_Amount', index='Income_Level',
                        columns='Gender', aggfunc='mean')
fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax, linewidths=0.5)
ax.set_title('AOV ($) theo Thu Nhập × Giới Tính', fontsize=13, fontweight='bold')
save("05_aov_heatmap")

# ─── 8. Discount Sensitivity → Satisfaction ────────────────────────────────
disc_order = ['Not Sensitive', 'Somewhat Sensitive', 'Very Sensitive']
disc_df = df[df['Discount_Sensitivity'].isin(disc_order)].copy()
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=disc_df, x='Discount_Sensitivity', y='Customer_Satisfaction',
            order=disc_order, palette='Set2', ax=ax)
ax.set_title('Mức Độ Nhạy Cảm Giảm Giá vs Sự Hài Lòng', fontsize=13, fontweight='bold')
save("06_discount_vs_satisfaction")

# ─── 9. Purchase Intent phân bổ ─────────────────────────────────────────────
intent_counts = df['Purchase_Intent'].value_counts()
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(intent_counts, labels=intent_counts.index, autopct='%1.1f%%',
       startangle=90, colors=sns.color_palette("pastel"))
ax.set_title('Phân Bổ Purchase Intent', fontsize=13, fontweight='bold')
save("07_purchase_intent_pie")

# ─── 10. Tương quan Correlation Matrix ──────────────────────────────────────
num_cols = ['Age', 'Purchase_Amount', 'Frequency_of_Purchase', 'Brand_Loyalty',
            'Product_Rating', 'Research_Hours', 'Return_Rate',
            'Customer_Satisfaction', 'Time_to_Decision']
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(11, 9))
mask = pd.DataFrame([[False]*len(num_cols)]*len(num_cols))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            linewidths=0.5, square=True, ax=ax)
ax.set_title('Ma Trận Tương Quan — Biến Số', fontsize=13, fontweight='bold')
save("08_correlation_matrix")

# ─── 11. Social Media Influence → Brand Loyalty ─────────────────────────────
sm_order = ['None', 'Low', 'Medium', 'High']
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=df, x='Social_Media_Influence', y='Brand_Loyalty',
            order=sm_order, palette='Blues_d', ax=ax, errorbar='sd')
ax.set_title('Social Media Influence vs Brand Loyalty', fontsize=13, fontweight='bold')
save("09_social_media_vs_loyalty")

# ─── 12. Xu hướng mua theo tháng ────────────────────────────────────────────
if 'Purchase_Month' in df.columns and df['Purchase_Month'].notna().any():
    monthly = df.groupby('Purchase_Month').agg(
        revenue=('Purchase_Amount', 'sum'),
        orders=('Customer_ID', 'count')
    ).reset_index()
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx()
    ax1.plot(monthly['Purchase_Month'], monthly['revenue'], 'b-o', label='Revenue')
    ax2.bar(monthly['Purchase_Month'], monthly['orders'], alpha=0.3, color='orange', label='Orders')
    ax1.set_title('Xu Hướng Doanh Thu & Số Đơn Theo Tháng', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Revenue ($)', color='blue')
    ax2.set_ylabel('Num Orders', color='orange')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    save("10_monthly_trend")

# ─── 13. Statistical Test: Discount Used vs Return Rate ──────────────────────
disc_yes = df[df['Discount_Used'] == 1]['Return_Rate']
disc_no  = df[df['Discount_Used'] == 0]['Return_Rate']
t_stat, p_val = stats.mannwhitneyu(disc_yes, disc_no, alternative='two-sided')
print(f"\n=== A/B Quick Test: Discount vs Return Rate ===")
print(f"  Discount Used mean Return Rate:  {disc_yes.mean():.3f}")
print(f"  No Discount   mean Return Rate:  {disc_no.mean():.3f}")
print(f"  Mann-Whitney U stat: {t_stat:.1f}, p-value: {p_val:.4f}")
print(f"  {'Significant diff (p<0.05)' if p_val < 0.05 else 'No significant diff'}")


# ─── 14. Marital Status → AOV & Satisfaction ────────────────────────────────
marital_df = df.groupby('Marital_Status').agg(
    aov=('Purchase_Amount', 'mean'),
    avg_sat=('Customer_Satisfaction', 'mean'),
    count=('Customer_ID', 'count')
).reset_index().sort_values('aov', ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(marital_df['Marital_Status'], marital_df['aov'],
            color=sns.color_palette('Set3', len(marital_df)), edgecolor='white')
axes[0].set_title('AOV theo Marital Status', fontsize=12, fontweight='bold')
axes[0].set_ylabel('AOV ($)')
axes[0].tick_params(axis='x', rotation=15)
axes[1].bar(marital_df['Marital_Status'], marital_df['avg_sat'],
            color=sns.color_palette('pastel', len(marital_df)), edgecolor='white')
axes[1].set_title('Avg Satisfaction theo Marital Status', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Avg Satisfaction')
axes[1].tick_params(axis='x', rotation=15)
fig.suptitle('Marital Status Analysis', fontsize=14, fontweight='bold')
save("11_marital_status_analysis")

# ─── 15. Education Level → Purchase Behavior ────────────────────────────────
edu_order = ["High School", "Bachelor's", "Master's", "PhD"]
edu_df = df[df['Education_Level'].isin(edu_order)].groupby('Education_Level').agg(
    aov=('Purchase_Amount', 'mean'),
    avg_freq=('Frequency_of_Purchase', 'mean'),
    avg_sat=('Customer_Satisfaction', 'mean'),
    avg_research=('Research_Hours', 'mean'),
    count=('Customer_ID', 'count')
).reindex(edu_order)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes[0,0].bar(edu_order, edu_df['aov'], color='steelblue', edgecolor='white')
axes[0,0].set_title('AOV theo Trình Độ Học Vấn', fontsize=11, fontweight='bold')
axes[0,0].set_ylabel('AOV ($)')
axes[0,0].tick_params(axis='x', rotation=15)

axes[0,1].bar(edu_order, edu_df['avg_freq'], color='coral', edgecolor='white')
axes[0,1].set_title('Tần Suất Mua theo Trình Độ', fontsize=11, fontweight='bold')
axes[0,1].set_ylabel('Avg Frequency')
axes[0,1].tick_params(axis='x', rotation=15)

axes[1,0].bar(edu_order, edu_df['avg_sat'], color='mediumseagreen', edgecolor='white')
axes[1,0].set_title('Mức Hài Lòng theo Trình Độ', fontsize=11, fontweight='bold')
axes[1,0].set_ylabel('Avg Satisfaction')
axes[1,0].tick_params(axis='x', rotation=15)

axes[1,1].bar(edu_order, edu_df['avg_research'], color='mediumpurple', edgecolor='white')
axes[1,1].set_title('Giờ Nghiên Cứu SP theo Trình Độ', fontsize=11, fontweight='bold')
axes[1,1].set_ylabel('Avg Research Hours')
axes[1,1].tick_params(axis='x', rotation=15)

fig.suptitle('Education Level Analysis', fontsize=14, fontweight='bold')
save("12_education_level_analysis")

# ─── 16. Occupation → Revenue & Frequency ───────────────────────────────────
occ_df = df.groupby('Occupation').agg(
    total_rev=('Purchase_Amount', 'sum'),
    aov=('Purchase_Amount', 'mean'),
    avg_freq=('Frequency_of_Purchase', 'mean'),
    avg_loyalty=('Brand_Loyalty', 'mean')
).reset_index().sort_values('total_rev', ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].barh(occ_df['Occupation'], occ_df['total_rev'],
             color=sns.color_palette('husl', len(occ_df)), edgecolor='white')
axes[0].set_title('Tổng Doanh Thu theo Nghề Nghiệp', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Revenue ($)')

axes[1].barh(occ_df['Occupation'], occ_df['avg_loyalty'],
             color=sns.color_palette('Blues_d', len(occ_df)), edgecolor='white')
axes[1].set_title('Brand Loyalty trung bình theo Nghề Nghiệp', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Avg Brand Loyalty')

fig.suptitle('Occupation Analysis', fontsize=14, fontweight='bold')
save("13_occupation_analysis")

# ─── 17. Location Top 15 ─────────────────────────────────────────────────────
loc_df = df.groupby('Location').agg(
    total_rev=('Purchase_Amount', 'sum'),
    num_orders=('Customer_ID', 'count'),
    avg_sat=('Customer_Satisfaction', 'mean')
).reset_index().sort_values('total_rev', ascending=True).tail(15)

fig, ax = plt.subplots(figsize=(11, 8))
bars = ax.barh(loc_df['Location'], loc_df['total_rev'],
               color=sns.color_palette('viridis', len(loc_df)), edgecolor='white')
ax.bar_label(bars, fmt='$%.0f', padding=3, fontsize=8)
ax.set_title('Top 15 Địa Điểm Theo Doanh Thu', fontsize=13, fontweight='bold')
ax.set_xlabel('Revenue ($)')
save("14_top_locations")

# ─── 18. Product Rating Distribution & Impact ────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Phân phối rating
rating_counts = df['Product_Rating'].value_counts().sort_index()
axes[0].bar(rating_counts.index, rating_counts.values,
            color=sns.color_palette('RdYlGn', 5), edgecolor='white', linewidth=0.5)
axes[0].set_title('Phân Phối Product Rating', fontsize=11, fontweight='bold')
axes[0].set_xlabel('Rating (1-5)')
axes[0].set_ylabel('Count')

# Rating → Satisfaction
rating_sat = df.groupby('Product_Rating')['Customer_Satisfaction'].mean()
axes[1].plot(rating_sat.index, rating_sat.values, 'o-', lw=2, color='steelblue', ms=8)
axes[1].fill_between(rating_sat.index, rating_sat.values, alpha=0.2, color='steelblue')
axes[1].set_title('Product Rating vs Avg Satisfaction', fontsize=11, fontweight='bold')
axes[1].set_xlabel('Product Rating')
axes[1].set_ylabel('Avg Customer Satisfaction')

# Rating → Return Rate
rating_ret = df.groupby('Product_Rating')['Return_Rate'].mean()
axes[2].bar(rating_ret.index, rating_ret.values,
            color=['#d73027', '#f46d43', '#fdae61', '#74add1', '#4575b4'], edgecolor='white')
axes[2].set_title('Product Rating vs Return Rate', fontsize=11, fontweight='bold')
axes[2].set_xlabel('Product Rating')
axes[2].set_ylabel('Avg Return Rate')

fig.suptitle('Product Rating Analysis', fontsize=14, fontweight='bold')
save("15_product_rating_analysis")

# ─── 19. Time to Decision Analysis ──────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Distribution
axes[0,0].hist(df['Time_to_Decision'], bins=20, color='mediumpurple', edgecolor='white')
axes[0,0].set_title('Phân Phối Time to Decision', fontsize=11, fontweight='bold')
axes[0,0].set_xlabel('Minutes')

# Time to Decision → Satisfaction
axes[0,1].scatter(df['Time_to_Decision'], df['Customer_Satisfaction'],
                   alpha=0.3, color='steelblue', s=20)
import numpy as np
z = np.polyfit(df['Time_to_Decision'].dropna(), df['Customer_Satisfaction'].dropna(), 1)
p = np.poly1d(z)
x_line = sorted(df['Time_to_Decision'].dropna().unique())
axes[0,1].plot(x_line, p(x_line), 'r-', lw=2)
axes[0,1].set_title('Time to Decision vs Satisfaction', fontsize=11, fontweight='bold')
axes[0,1].set_xlabel('Time (min)')
axes[0,1].set_ylabel('Satisfaction')

# Time to Decision → Purchase Intent
intent_time = df.groupby('Purchase_Intent')['Time_to_Decision'].mean().sort_values()
axes[1,0].barh(intent_time.index, intent_time.values,
               color=sns.color_palette('Set2', len(intent_time)))
axes[1,0].set_title('Avg Decision Time theo Purchase Intent', fontsize=11, fontweight='bold')
axes[1,0].set_xlabel('Minutes')

# Time to Decision → Channel
chan_time = df.groupby('Purchase_Channel')['Time_to_Decision'].mean().sort_values()
axes[1,1].bar(chan_time.index, chan_time.values,
              color=['#2E86AB', '#A23B72', '#F18F01'], edgecolor='white')
axes[1,1].set_title('Avg Decision Time theo Channel', fontsize=11, fontweight='bold')
axes[1,1].set_ylabel('Minutes')

fig.suptitle('Time to Decision Analysis', fontsize=14, fontweight='bold')
save("16_time_to_decision_analysis")

# ─── 20. Day of Week & Quarter Trends ───────────────────────────────────────
if 'Purchase_DayOfWeek' in df.columns and df['Purchase_DayOfWeek'].notna().any():
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    day_df = df.groupby('Purchase_DayOfWeek').agg(
        revenue=('Purchase_Amount', 'sum'),
        orders=('Customer_ID', 'count'),
        avg_amount=('Purchase_Amount', 'mean')
    ).reset_index()

    quarter_df = df.groupby('Purchase_Quarter').agg(
        revenue=('Purchase_Amount', 'sum'),
        orders=('Customer_ID', 'count')
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    axes[0].bar([day_labels[int(d)] for d in day_df['Purchase_DayOfWeek']],
                day_df['revenue'], color=sns.color_palette('husl', 7), edgecolor='white')
    axes[0].set_title('Doanh Thu theo Ngày Trong Tuần', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Revenue ($)')

    axes[1].bar([f'Q{int(q)}' for q in quarter_df['Purchase_Quarter']],
                quarter_df['revenue'], color=['#4e79a7','#f28e2b','#e15759','#76b7b2'],
                edgecolor='white')
    axes[1].set_title('Doanh Thu theo Quý', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Revenue ($)')

    fig.suptitle('Time-Based Purchase Trends', fontsize=14, fontweight='bold')
    save("17_time_trends_dayofweek_quarter")

# ─── 21. Device × Channel Heatmap ───────────────────────────────────────────
device_channel = df.pivot_table(
    values='Purchase_Amount', index='Device_Used_for_Shopping',
    columns='Purchase_Channel', aggfunc='mean'
)
fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(device_channel, annot=True, fmt='.0f', cmap='Blues',
            linewidths=0.5, ax=ax)
ax.set_title('AOV ($) — Device × Purchase Channel', fontsize=13, fontweight='bold')
save("18_device_channel_heatmap")

# ─── 22. Engagement with Ads → Purchase Behavior ────────────────────────────
eng_order = ['None', 'Low', 'Medium', 'High']
eng_df = df[df['Engagement_with_Ads'].isin(eng_order)].groupby('Engagement_with_Ads').agg(
    aov=('Purchase_Amount', 'mean'),
    avg_freq=('Frequency_of_Purchase', 'mean'),
    avg_intent_imp=('Purchase_Intent', lambda x: (x == 'Impulsive').mean() * 100),
    avg_sat=('Customer_Satisfaction', 'mean')
).reindex(eng_order)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
axes[0].bar(eng_order, eng_df['aov'], color=sns.color_palette('Oranges_d', 4), edgecolor='white')
axes[0].set_title('AOV theo Engagement Ads', fontsize=11, fontweight='bold')
axes[0].set_ylabel('AOV ($)')

axes[1].bar(eng_order, eng_df['avg_freq'], color=sns.color_palette('Greens_d', 4), edgecolor='white')
axes[1].set_title('Tần Suất Mua theo Engagement', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Avg Frequency')

axes[2].bar(eng_order, eng_df['avg_intent_imp'], color=sns.color_palette('Reds_d', 4), edgecolor='white')
axes[2].set_title('% Impulsive Purchase theo Engagement', fontsize=11, fontweight='bold')
axes[2].set_ylabel('% Impulsive')

fig.suptitle('Engagement with Ads Analysis', fontsize=14, fontweight='bold')
save("19_engagement_with_ads_analysis")

# ─── 23. Shipping Preference × Satisfaction × Return Rate ───────────────────
ship_df = df.groupby('Shipping_Preference').agg(
    avg_sat=('Customer_Satisfaction', 'mean'),
    avg_ret=('Return_Rate', 'mean'),
    avg_dec=('Time_to_Decision', 'mean'),
    count=('Customer_ID', 'count')
).reset_index().sort_values('avg_sat', ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
colors = sns.color_palette('Set2', len(ship_df))
axes[0].bar(ship_df['Shipping_Preference'], ship_df['avg_sat'], color=colors, edgecolor='white')
axes[0].set_title('Satisfaction theo Shipping Preference', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Avg Satisfaction')

axes[1].bar(ship_df['Shipping_Preference'], ship_df['avg_ret'], color=colors, edgecolor='white')
axes[1].set_title('Return Rate theo Shipping Preference', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Avg Return Rate')

fig.suptitle('Shipping Preference Analysis', fontsize=14, fontweight='bold')
save("20_shipping_preference_analysis")

# ─── 24. Cross Analysis: Education × Channel → Satisfaction (Pivot Heatmap) ─
edu_chan = df.pivot_table(
    values='Customer_Satisfaction',
    index='Education_Level',
    columns='Purchase_Channel',
    aggfunc='mean'
)
fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(edu_chan, annot=True, fmt='.2f', cmap='YlGn',
            linewidths=0.5, ax=ax)
ax.set_title('Avg Satisfaction — Education Level × Channel', fontsize=12, fontweight='bold')
save("21_education_channel_satisfaction")

# ─── 25. Brand Loyalty phân tích đa chiều ───────────────────────────────────
loyalty_bins = pd.cut(df['Brand_Loyalty'], bins=[0, 2, 3, 5],
                       labels=['Low (1-2)', 'Medium (3)', 'High (4-5)'])
df['Loyalty_Group'] = loyalty_bins

loyalty_df = df.groupby('Loyalty_Group', observed=True).agg(
    aov=('Purchase_Amount', 'mean'),
    avg_freq=('Frequency_of_Purchase', 'mean'),
    avg_sat=('Customer_Satisfaction', 'mean'),
    avg_ret=('Return_Rate', 'mean'),
    discount_rate=('Discount_Used', 'mean'),
    loyalty_mem_rate=('Customer_Loyalty_Program_Member', 'mean')
).reset_index()

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
metrics = [('aov','AOV ($)','steelblue'), ('avg_freq','Avg Frequency','coral'),
           ('avg_sat','Avg Satisfaction','mediumseagreen'), ('avg_ret','Avg Return Rate','tomato'),
           ('discount_rate','Discount Usage %','mediumpurple'), ('loyalty_mem_rate','Loyalty Member %','gold')]
for i, (col, label, color) in enumerate(metrics):
    r, c = divmod(i, 3)
    axes[r,c].bar(loyalty_df['Loyalty_Group'], loyalty_df[col], color=color, edgecolor='white')
    axes[r,c].set_title(f'{label} theo Brand Loyalty', fontsize=10, fontweight='bold')
    axes[r,c].set_ylabel(label)
    axes[r,c].tick_params(axis='x', rotation=10)

fig.suptitle('Brand Loyalty — Phân Tích Đa Chiều', fontsize=14, fontweight='bold')
save("22_brand_loyalty_multidim")

# ─── 26. Tóm tắt Missing Values & Data Quality ──────────────────────────────
missing = df.isnull().sum()
missing = missing[missing > 0].sort_values(ascending=True) if missing.any() else pd.Series({'No missing values': 0})
dtype_dist = df.dtypes.value_counts()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].barh(missing.index, missing.values, color='salmon', edgecolor='white')
axes[0].set_title('Missing Values per Column', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Count')

dtype_labels = [str(d) for d in dtype_dist.index]
axes[1].pie(dtype_dist.values, labels=dtype_labels, autopct='%1.0f%%',
            colors=sns.color_palette('Set2'), startangle=90)
axes[1].set_title('Phân Bổ Kiểu Dữ Liệu', fontsize=12, fontweight='bold')

fig.suptitle('Data Quality Overview', fontsize=14, fontweight='bold')
save("23_data_quality_overview")

print(f"\nDone! Total {23} charts saved to: {OUT_DIR}")
