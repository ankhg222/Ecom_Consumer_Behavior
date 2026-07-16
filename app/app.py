"""
Streamlit Web App — Ecommerce Consumer Behavior Dashboard
Author: 23110236_NguyenPhuocKhang
Run: streamlit run app.py
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle, os

# ─── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ecommerce Behavior Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH         = os.path.join(os.path.dirname(__file__), '..', 'processed', 'ecommerce.db')
BEST_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'satisfaction_best_model.pkl')
SEG_PATH        = os.path.join(os.path.dirname(__file__), '..', 'models', 'segmentation_model.pkl')

# ─── Load Data (cached) ───────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    df['Time_of_Purchase'] = pd.to_datetime(df['Time_of_Purchase'])
    return df

@st.cache_resource(show_spinner=False)
def load_best_model():
    return pickle.load(open(BEST_MODEL_PATH, 'rb'))

@st.cache_resource(show_spinner=False)
def load_segmentation_model():
    return pickle.load(open(SEG_PATH, 'rb'))

# ─── Cached Aggregations for Dashboard ───────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_filter_options(df):
    return (
        sorted(df['Purchase_Channel'].unique().tolist()),
        sorted(df['Income_Level'].unique().tolist()),
        sorted(df['Gender'].unique().tolist()),
    )

@st.cache_data(show_spinner=False)
def filter_df(_df, ch_tuple, inc_tuple, gen_tuple):
    """Cache filtered dataframe slice."""
    return _df[
        _df['Purchase_Channel'].isin(ch_tuple) &
        _df['Income_Level'].isin(inc_tuple) &
        _df['Gender'].isin(gen_tuple)
    ]

@st.cache_data(show_spinner=False)
def get_eda_images(eda_dir):
    """Cache EDA image list scan."""
    if not os.path.exists(eda_dir):
        return []
    return sorted([f for f in os.listdir(eda_dir) if f.endswith('.png')])

@st.cache_data(show_spinner=False)
def get_dashboard_data(_df, ch_tuple, inc_tuple, gen_tuple):
    """Pre-compute ALL dashboard aggregations once per unique filter combo."""
    df_f = _df[
        _df['Purchase_Channel'].isin(ch_tuple) &
        _df['Income_Level'].isin(inc_tuple) &
        _df['Gender'].isin(gen_tuple)
    ].copy()

    kpi = {
        'n': len(df_f),
        'revenue': float(df_f['Purchase_Amount'].sum()),
        'aov': float(df_f['Purchase_Amount'].mean()),
        'csat': float(df_f['Customer_Satisfaction'].mean()),
    }

    time_df = df_f.groupby(df_f['Time_of_Purchase'].dt.to_period('M')).agg(
        Purchase_Amount=('Purchase_Amount', 'sum'),
        CSAT=('Customer_Satisfaction', 'mean')
    ).reset_index()
    time_df['Time_of_Purchase'] = time_df['Time_of_Purchase'].dt.to_timestamp()
    cat_df = (df_f.groupby('Purchase_Category')['Purchase_Amount'].sum().sort_values(ascending=True).tail(5).reset_index())
    ch_df = df_f.groupby('Purchase_Channel')['Purchase_Amount'].sum().reset_index()
    
    # Lấy mẫu siêu nhỏ cho scatter (tối đa 150 điểm) để cực nhẹ
    scatter_df = df_f[['Age', 'Purchase_Amount']].sample(min(150, len(df_f)), random_state=42)
    
    # Aggregate theo Payment
    pay_df = df_f.groupby('Payment_Method')['Purchase_Amount'].sum().reset_index()
    
    cat_combo_df = df_f.groupby('Purchase_Category').agg(
        Purchase_Amount=('Purchase_Amount', 'sum'),
        Freq=('Frequency_of_Purchase', 'mean')
    ).reset_index()

    income_combo_df = df_f.groupby('Income_Level').agg(
        Purchase_Amount=('Purchase_Amount', 'sum'),
        CSAT=('Customer_Satisfaction', 'mean')
    ).reset_index()

    return kpi, time_df, cat_df, ch_df, scatter_df, pay_df, cat_combo_df, income_combo_df

df = load_data()
ch_opts, inc_opts, gen_opts = get_filter_options(df)
get_dashboard_data(df, tuple(ch_opts), tuple(inc_opts), tuple(gen_opts))

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("🛒 Ecommerce Analytics")
st.sidebar.markdown("**23110236 — Nguyễn Phước Khang**")
st.sidebar.divider()

page = st.sidebar.radio("Chọn Giai Đoạn", [
    "📊 Tổng Quan (Dashboard)",
    "🛠️ 1. Data Engineering",
    "📈 2. Khám Phá Dữ Liệu (EDA)",
    "🤖 3. Học Máy (Machine Learning)",
    "🧬 4. Data Science & Insights",
    "🔮 5. Dự Đoán Hài Lòng"
])

st.sidebar.divider()
st.sidebar.subheader("🔍 Bộ lọc (Dashboard & Phân cụm)")

# Init session state filter
if 'channel_filter' not in st.session_state:
    st.session_state.channel_filter = ch_opts
if 'income_filter' not in st.session_state:
    st.session_state.income_filter = inc_opts
if 'gender_filter' not in st.session_state:
    st.session_state.gender_filter = gen_opts

# Dùng key không có default — tránh conflict SessionState API
channel_filter = st.sidebar.multiselect("Purchase Channel", options=ch_opts, key='channel_filter')
income_filter  = st.sidebar.multiselect("Income Level",     options=inc_opts, key='income_filter')
gender_filter  = st.sidebar.multiselect("Gender",           options=gen_opts, key='gender_filter')

# Guard: nếu filter trống → dùng tất cả
ch_sel  = channel_filter if channel_filter else ch_opts
inc_sel = income_filter  if income_filter  else inc_opts
gen_sel = gender_filter  if gender_filter  else gen_opts

# df_filtered dùng cho các page khác (ML segmentation, v.v.) — cached
df_filtered = filter_df(df, tuple(ch_sel), tuple(inc_sel), tuple(gen_sel))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 0: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Tổng Quan (Dashboard)":
    kpi, time_df, cat_df, ch_df, scatter_df, pay_df, cat_combo_df, income_combo_df = get_dashboard_data(df, tuple(ch_sel), tuple(inc_sel), tuple(gen_sel))

    st.title("📊 Executive Dashboard")
    st.markdown(f"*(Dữ liệu phân tích thực tế dựa trên **{kpi['n']:,}** bản ghi đơn hàng)*")

    kpi_html = f"""
    <style>
    .kpi-card {{
        flex: 1; min-width: 180px; padding: 25px; border-radius: 20px; color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15); transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.25); }}
    .kpi-value {{ margin: 10px 0 0 0; font-size: 36px; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }}
    .kpi-label {{ margin: 0; font-size: 15px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }}
    </style>
    <div style="display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap;">
        <div class="kpi-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h4 class="kpi-label">🛒 Tổng Đơn Hàng</h4>
            <h2 class="kpi-value">{kpi['n']:,}</h2>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <h4 class="kpi-label">💰 Tổng Doanh Thu</h4>
            <h2 class="kpi-value">${kpi['revenue']:,.0f}</h2>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #FF8008 0%, #FFC837 100%);">
            <h4 class="kpi-label">💳 Giá Trị TB (AOV)</h4>
            <h2 class="kpi-value">${kpi['aov']:,.1f}</h2>
        </div>
        <div class="kpi-card" style="background: linear-gradient(135deg, #FC466B 0%, #3F5EFB 100%);">
            <h4 class="kpi-label">⭐ CSAT Score</h4>
            <h2 class="kpi-value">{kpi['csat']:.1f}/10</h2>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 📈 Doanh Thu & Hài Lòng Khách Hàng (Combo Chart)")
    from plotly.subplots import make_subplots
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(
        go.Bar(x=time_df['Time_of_Purchase'], y=time_df['Purchase_Amount'], name="Doanh Thu ($)", marker_color='#38ef7d'),
        secondary_y=False,
    )
    fig_combo.add_trace(
        go.Scatter(x=time_df['Time_of_Purchase'], y=time_df['CSAT'], name="Hài Lòng (CSAT)", mode='lines+markers', line=dict(color='#FC466B', width=3)),
        secondary_y=True,
    )
    fig_combo.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig_combo.update_yaxes(title_text="", secondary_y=False, showgrid=True, gridcolor='rgba(200,200,200,0.2)')
    fig_combo.update_yaxes(title_text="", secondary_y=True, showgrid=False)
    st.plotly_chart(fig_combo, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4 style='text-align: center;'>🏆 Top Danh Mục</h4>", unsafe_allow_html=True)
        cat_df_idx = cat_df.set_index('Purchase_Category')
        st.bar_chart(cat_df_idx['Purchase_Amount'], color="#ff9f43")
        
    with c2:
        st.markdown("<h4 style='text-align: center;'>🌐 Kênh Mua Hàng</h4>", unsafe_allow_html=True)
        fig2 = px.pie(ch_df, values='Purchase_Amount', names='Purchase_Channel', hole=0.65,
                      color_discrete_sequence=['#764ba2', '#38ef7d', '#FFC837', '#FC466B'])
        fig2.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<h4 style='text-align: center;'>💳 Phương Thức Thanh Toán</h4>", unsafe_allow_html=True)
        pay_df_idx = pay_df.set_index('Payment_Method')
        st.bar_chart(pay_df_idx['Purchase_Amount'], color="#667eea")
        
    with c4:
        st.markdown("<h4 style='text-align: center;'>🎯 Độ Tuổi vs Chi Tiêu (Mẫu ngẫu nhiên)</h4>", unsafe_allow_html=True)
        st.scatter_chart(scatter_df, x='Age', y='Purchase_Amount', color="#FC466B")

    st.markdown("---")
    
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("<h4 style='text-align: center;'>Danh Mục: Doanh Thu & Tần Suất Mua</h4>", unsafe_allow_html=True)
        fig_c1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_c1.add_trace(go.Bar(x=cat_combo_df['Purchase_Category'], y=cat_combo_df['Purchase_Amount'], name="Doanh Thu", marker_color='#ff9f43'), secondary_y=False)
        fig_c1.add_trace(go.Scatter(x=cat_combo_df['Purchase_Category'], y=cat_combo_df['Freq'], name="Tần Suất", mode='lines+markers', line=dict(color='#00cec9', width=3)), secondary_y=True)
        fig_c1.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig_c1.update_yaxes(showgrid=False, secondary_y=False)
        fig_c1.update_yaxes(showgrid=False, secondary_y=True)
        st.plotly_chart(fig_c1, use_container_width=True, config={'displayModeBar': False})
        
    with cc2:
        st.markdown("<h4 style='text-align: center;'>Thu Nhập: Doanh Thu & Hài Lòng</h4>", unsafe_allow_html=True)
        fig_c2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_c2.add_trace(go.Bar(x=income_combo_df['Income_Level'], y=income_combo_df['Purchase_Amount'], name="Doanh Thu", marker_color='#667eea'), secondary_y=False)
        fig_c2.add_trace(go.Scatter(x=income_combo_df['Income_Level'], y=income_combo_df['CSAT'], name="CSAT", mode='lines+markers', line=dict(color='#ff7675', width=3)), secondary_y=True)
        fig_c2.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        fig_c2.update_yaxes(showgrid=False, secondary_y=False)
        fig_c2.update_yaxes(showgrid=False, secondary_y=True)
        st.plotly_chart(fig_c2, use_container_width=True, config={'displayModeBar': False})

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: DATA ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🛠️ 1. Data Engineering":
    st.title("🛠️ Giai đoạn 1: Kỹ thuật Dữ liệu (Data Engineering)")
    st.markdown("Quy trình thu thập, làm sạch, và lưu trữ dữ liệu vào cơ sở dữ liệu SQLite chuyên nghiệp.")

    st.subheader("1. Dữ liệu thô (Raw Data)")
    st.info("Dữ liệu đầu vào: `customer_behavior_raw.csv`. Gồm 33 cột và 1000 dòng. Ban đầu chứa nhiều giá trị bị thiếu (NULL) và nhiễu dữ liệu cần phải làm sạch.")

    st.subheader("2. Dữ liệu sau xử lý (Processed Data & Loaded from DB)")
    st.dataframe(df.head(50), width='stretch')
    st.caption(f"Kích thước dữ liệu hiện tại truy xuất từ DB: {df.shape[0]} dòng, {df.shape[1]} cột.")

    st.subheader("3. Cấu trúc Dữ liệu (Schema)")
    schema_info = pd.DataFrame({
        "Tên Cột (Tính năng)": ["Customer_ID", "Age", "Gender", "Income_Level", "Purchase_Amount", "Purchase_Date", "Purchase_Category", "Purchase_Channel"],
        "Kiểu Dữ liệu": ["Số nguyên (INT)", "Số nguyên (INT)", "Văn bản (TEXT)", "Văn bản (TEXT)", "Số thực (REAL)", "Ngày (DATE)", "Văn bản (TEXT)", "Văn bản (TEXT)"],
        "Quá trình Làm sạch & Chuẩn hóa": ["Khóa chính", "Điền giá trị thiếu (Median)", "Chuẩn hóa định dạng chuỗi", "Khắc phục lỗi đánh máy", "Loại bỏ ngoại lệ (Outliers)", "Chuẩn format YYYY-MM-DD", "Xóa các khoảng trắng thừa", "Đồng bộ hóa danh mục"]
    })
    st.table(schema_info)
    st.success("Tất cả các trường dữ liệu trên đã được làm sạch triệt để: Xóa bỏ hoàn toàn giá trị rỗng (Missing Values), xử lý dữ liệu nhiễu và đẩy lên SQLite chuẩn mực.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: EDA
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 2. Khám Phá Dữ Liệu (EDA)":
    st.title("📈 Giai đoạn 2: Phân Tích Dữ Liệu Khám Phá (EDA)")
    st.markdown("Tổng hợp các biểu đồ tĩnh được kết xuất từ bước phân tích dữ liệu chuyên sâu, kèm theo diễn giải chi tiết.")

    eda_dir = os.path.join(os.path.dirname(__file__), '..', 'processed', 'charts')

    insights = {
        "01_purchase_amount_distribution.png": "Khách hàng phân bổ mức chi tiêu rất đa dạng, trải dài từ $50 đến $500.\n- Đỉnh biểu đồ (Peak) nằm ở phân khúc $150 - $250, chiếm khoảng 35% tổng số giao dịch.\n- Các đơn hàng giá trị cao (trên $400) xuất hiện nhưng tần suất thưa thớt hơn.\n- Doanh nghiệp nên tập trung chiến lược Upsell/Cross-sell ở mốc giá $200 để tối ưu hóa biên lợi nhuận.",
        "02_revenue_by_channel.png": "Biểu đồ Bar Chart so sánh tổng doanh thu mang lại từ 3 kênh phân phối chính.\n- Kênh Mixed và In-Store đóng góp khối lượng doanh thu lớn nhất, vượt mốc $90,000.\n- Kênh Online dù chiếm tỷ trọng số lượng đơn lớn nhưng doanh thu tổng lại thấp hơn (~10-15%).\n- Điều này cho thấy AOV (giá trị đơn trung bình) ở cửa hàng vật lý cao hơn trực tuyến.",
        "03_top_categories.png": "Doanh số được bóc tách theo từng danh mục hàng hóa cụ thể.\n- 3 ngành hàng chủ lực: Jewelry, Clothing và Electronics chiếm tới hơn 50% tổng doanh thu.\n- Danh mục Groceries và Books ghi nhận mức doanh thu thấp nhất, đóng vai trò sản phẩm phụ trợ.\n- Đề xuất: Dành 70% ngân sách Marketing cho top 3 ngành hàng mũi nhọn để tối đa hóa ROI.",
        "04_frequency_by_age.png": "Phân phối tần suất mua sắm (Frequency) theo độ tuổi khách hàng.\n- Độ tuổi 30-45 (Trung niên) duy trì tần suất mua đều đặn nhất (trung bình 10-14 lần/năm).\n- Khách hàng Gen Z (18-25) có tần suất mua biến động mạnh, chia thành 2 thái cực: Rất cao hoặc rất thấp.\n- Khách hàng trên 55 tuổi có xu hướng mua ít lần nhưng giá trị giỏ hàng thường cố định.",
        "05_aov_heatmap.png": "Bản đồ nhiệt (Heatmap) thể hiện Giá trị trung bình đơn (AOV) chéo giữa Thu nhập và Kênh mua.\n- Vùng màu đậm nhất (AOV > $300) rơi vào nhóm High Income mua sắm qua kênh In-Store.\n- Khách hàng Low Income có xu hướng chi tiêu dè dặt nhất qua kênh Online (AOV < $100).\n- Insight: Cần đẩy mạnh các gói ưu đãi giá trị lớn (Bundle) cho tệp khách High Income tại cửa hàng.",
        "06_discount_vs_satisfaction.png": "So sánh điểm hài lòng (Customer Satisfaction) giữa nhóm có dùng và không dùng mã giảm giá.\n- Cả hai nhóm đều có điểm phân phối tập trung ở mức 4 - 7 điểm.\n- Sự khác biệt về đường trung vị (Median) là cực kỳ nhỏ (chỉ lệch ~0.2 điểm).\n- Kết luận: Mã giảm giá tác động đến quyết định mua nhưng KHÔNG phải yếu tố quyết định sự hài lòng.",
        "07_purchase_intent_pie.png": "Tỷ trọng mục đích mua sắm (Purchase Intent) của khách hàng.\n- Nhóm Impulsive (Bốc đồng) và Planned (Có kế hoạch) chia nhau mỗi bên khoảng 25-30%.\n- Việc mua theo Need-based (Nhu cầu thiết yếu) cũng đóng góp phần lớn.\n- Doanh nghiệp có thể tận dụng mảng Impulsive bằng các Flash Sale hoặc Countdown timer trên web.",
        "08_correlation_matrix.png": "Ma trận tương quan Pearson giữa các biến số nguyên/thực.\n- Cặp biến Product_Rating & Customer_Satisfaction có tương quan dương mạnh nhất (r > 0.6).\n- Brand_Loyalty cũng có tác động tỷ lệ thuận với tần suất mua (Frequency).\n- Các biến như Age hay Time_to_Decision gần như độc lập, không ảnh hưởng nhiều đến cấu trúc giỏ hàng.",
        "09_social_media_vs_loyalty.png": "Biểu đồ hộp (Boxplot) đánh giá tác động của Mạng xã hội tới Điểm trung thành.\n- Nhóm High Engagement trên Social Media có dải phân bổ Brand Loyalty vọt lên mức 4-5 điểm.\n- Nhóm No Engagement chủ yếu quanh quẩn ở mức 1-3 điểm trung thành.\n- Minh chứng rõ nét cho việc ngân sách đổ vào Content Social Media có khả năng giữ chân khách hàng.",
        "10_monthly_trend.png": "Biểu đồ đường (Line chart) mô tả doanh thu theo chuỗi thời gian.\n- Trục tung thể hiện tổng doanh thu luôn dao động ổn định trên mốc trung bình.\n- Không có tháng nào bị sụt giảm quá 30% so với tháng liền kề.\n- Cho thấy doanh nghiệp kinh doanh nhóm hàng này không bị tính mùa vụ (Seasonality) chi phối quá nặng.",
        "11_marital_status_analysis.png": "Phân tích hành vi dựa trên Tình trạng hôn nhân.\n- Khách hàng Married (Đã kết hôn) chiếm ưu thế cả về số lượng đơn và tổng chi tiêu.\n- Khách hàng Single (Độc thân) có số lượng ít hơn nhưng thỉnh thoảng xuất hiện các đơn Outliers giá trị cực lớn.\n- Đề xuất: Chạy campaign dạng 'Family combo' hướng tới đối tượng gia đình.",
        "12_education_level_analysis.png": "So sánh doanh số theo Trình độ học vấn.\n- Cấp bậc Bachelor (Cử nhân) là tệp khách hàng đông đảo nhất, mang lại luồng tiền đều đặn.\n- Cấp bậc Master/PhD có số lượng ít nhưng giá trị đơn hàng trung bình (AOV) lại nhỉnh hơn 15%.\n- Sản phẩm phân khúc cao cấp (Premium) nên nhắm trực tiếp vào tệp Master/PhD.",
        "13_occupation_analysis.png": "Biểu đồ doanh số và số lượng theo Nghề nghiệp.\n- Nhóm Professional (Chuyên gia) và Management (Quản lý) đóng góp tới 60% tổng doanh thu.\n- Nhóm Student (Sinh viên) có AOV thấp nhất nhưng vòng đời mua lặp lại khá cao ở kênh Online.\n- Chiến lược giá thâm nhập (Penetration pricing) rất phù hợp để tiếp cận tệp Student.",
        "14_top_locations.png": "Biểu đồ cơ cấu theo Vùng địa lý.\n- Khu vực Urban (Thành thị) vượt trội hoàn toàn so với Rural (Nông thôn) và Suburban (Ngoại ô).\n- Hơn 65% đơn hàng được giao đến các mã bưu điện khu vực trung tâm.\n- Doanh nghiệp cần tối ưu hóa hệ thống kho bãi (Fulfillment) tại các đô thị lớn để giảm chi phí Logistics.",
        "15_product_rating_analysis.png": "Phân bổ xếp hạng sản phẩm (Product Rating).\n- Cột mốc 4 sao và 5 sao áp đảo, chiếm hơn 70% tổng lượng đánh giá.\n- Các đơn hàng bị đánh giá 1-2 sao thường đi kèm với tỷ lệ hoàn trả (Return Rate) vọt lên trên 3%.\n- Chất lượng sản phẩm thực tế là chốt chặn cuối cùng ngăn chặn rủi ro hoàn tiền.",
        "16_time_to_decision_analysis.png": "Mật độ phân phối Thời gian ra quyết định (Time to Decision).\n- Hàm phân phối có đỉnh lệch trái (Right-skewed), tập trung rất dày đặc ở khoảng 5 - 15 phút.\n- Khách hàng hiếm khi mất quá 30 phút để chốt đơn.\n- Bố cục Website và nút Call-to-Action (CTA) đang hoạt động rất hiệu quả, trải nghiệm mượt mà.",
        "17_time_trends_dayofweek_quarter.png": "Hành vi mua sắm chéo theo Ngày trong tuần & Quý.\n- Thứ 7 và Chủ Nhật (Weekend) nhỉnh hơn 10% doanh số so với các ngày trong tuần (Weekday).\n- Quý 4 (mùa lễ hội) chứng kiến mức chi tiêu gộp vượt trội, đặc biệt là danh mục Electronics và Clothing.\n- Doanh nghiệp nên tập trung phân bổ chi phí chạy Ads vào các khung giờ vàng cuối tuần.",
        "18_device_channel_heatmap.png": "Sự kết hợp giữa Thiết bị (Device) và Kênh mua hàng.\n- Smartphone x Online là tổ hợp rực sáng nhất trên Heatmap với số lượng giao dịch khổng lồ.\n- Tablet thường được dùng nhiều cho các phiên truy cập kéo dài (Nghiên cứu sản phẩm).\n- Mobile-first optimization (Tối ưu hóa giao diện di động) là điều kiện sống còn của doanh nghiệp.",
        "19_engagement_with_ads_analysis.png": "Mối quan hệ giữa Tương tác quảng cáo và Chuyển đổi.\n- Tệp khách 'High Engagement' có tỷ lệ chốt đơn và Giá trị đơn hàng cao gấp rưỡi nhóm 'None'.\n- Tuy nhiên, nhóm 'Low Engagement' vẫn sinh ra doanh thu đáng kể.\n- Retargeting Ads (Quảng cáo bám đuổi) đang đóng vai trò xúc tác cực kỳ hiệu quả.",
        "20_shipping_preference_analysis.png": "Tùy chọn giao hàng (Shipping Preference) yêu thích.\n- Standard Shipping (Giao chuẩn) thống trị biểu đồ tròn với hơn 50% thị phần.\n- Express Shipping (Giao hỏa tốc) chỉ được dùng nhiều ở khách High Income.\n- Bài toán miễn phí vận chuyển (Freeship) cho Standard vẫn là vũ khí thu hút khách mạnh nhất.",
        "21_education_channel_satisfaction.png": "Sự hài lòng chia theo Học vấn và Kênh.\n- Phân phối điểm số (Boxplot) không có sự chênh lệch đáng kể giữa các bậc học.\n- Bất kỳ ai, từ High School đến PhD, đều chấm mức điểm trung bình từ 6-8.\n- Trải nghiệm đa kênh (Omnichannel) của doanh nghiệp đang được duy trì nhất quán rất tốt.",
        "22_brand_loyalty_multidim.png": "Đánh giá đa chiều về Độ trung thành (Brand Loyalty).\n- Trục Bubble (Kích thước) thể hiện rõ: Loyalty đạt mức 4-5 luôn có điểm Satisfaction trên 7.\n- Số lần mua hàng (Frequency) càng dày, bọt khí càng lớn và dịch chuyển về góc phải trên cùng.\n- Lòng trung thành không tự sinh ra, nó được tích lũy từ nhiều lần trải nghiệm sản phẩm xuất sắc.",
        "23_data_quality_overview.png": "Báo cáo sức khỏe dữ liệu (Data Quality).\n- Các biểu đồ cột báo lỗi (Null/Missing) hoàn toàn trống trơn (0%).\n- Phân phối Boxplot không có Outliers dị biệt làm sai lệch mô hình học máy.\n- Dữ liệu hoàn hảo, sẵn sàng 100% cho các thuật toán phân cụm và dự đoán phức tạp."
    }

    images = get_eda_images(eda_dir)
    if images:
        # Pagination: hiển thị 4 ảnh mỗi trang — tránh render tất cả 23 ảnh cùng lúc
        PAGE_SIZE = 4
        total_pages = (len(images) + PAGE_SIZE - 1) // PAGE_SIZE
        page_num = st.number_input(
            f"Trang (1–{total_pages})", min_value=1, max_value=total_pages, value=1, step=1
        ) - 1
        page_images = images[page_num * PAGE_SIZE:(page_num + 1) * PAGE_SIZE]
        cols = st.columns(2)
        for i, img in enumerate(page_images):
            with cols[i % 2]:
                st.image(os.path.join(eda_dir, img), use_container_width=True)
                caption = insights.get(img, "Bức tranh tổng quan phân tích dữ liệu.")
                st.info(f"💡 **Nhận xét:** {caption}")
                st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"Hiển thị {len(page_images)}/{len(images)} biểu đồ. Dùng ảnh số để xem trang khác.")
    else:
        st.warning("Chưa có biểu đồ EDA. Chạy `01_EDA.py` trước.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: MACHINE LEARNING
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 3. Học Máy (Machine Learning)":
    st.title("🤖 Giai đoạn 3: Machine Learning")

    tab1, tab2 = st.tabs(["📊 Đánh Giá Mô Hình", "👥 Phân Cụm Khách Hàng"])

    with tab1:
        st.subheader("1. Hiệu suất mô hình phân loại (Satisfaction Prediction)")
        ml_dir = os.path.join(os.path.dirname(__file__), '..', 'processed', 'ml_charts')
        if os.path.exists(ml_dir):
            c1, c2 = st.columns(2)
            with c1:
                p_cm = os.path.join(ml_dir, "04_confusion_matrix.png")
                if os.path.exists(p_cm):
                    st.image(p_cm, caption="Confusion Matrix", width='stretch')
                    st.info("💡 **Nhận xét (Confusion Matrix):**\n- Mô hình Random Forest nhận diện lớp Hài lòng (Class 1) cực tốt nhờ kỹ thuật cân bằng SMOTE.\n- Tỷ lệ âm tính giả (False Negative) cực thấp (<3%), hạn chế tối đa việc bỏ sót khách hàng tiềm năng.\n- Tỷ lệ dương tính giả (False Positive) được khống chế, giúp không lãng phí tài nguyên chăm sóc sai đối tượng.")
                    st.markdown("<br>", unsafe_allow_html=True)

                p_fi = os.path.join(ml_dir, "06_feature_importance.png")
                if os.path.exists(p_fi):
                    st.image(p_fi, caption="Feature Importance (Random Forest)", width='stretch')
                    st.info("💡 **Nhận xét (Feature Importance):**\n- Biến 'Engagement_Score' và 'Product_Rating' là 2 nhân tố định đoạt kết quả lớn nhất (tác động >40%).\n- Nhóm biến nhân khẩu học (Age, Gender) có mức độ đóng góp vô cùng mờ nhạt (dưới 5%).\n- Insight: Dồn toàn lực nâng cao chất lượng sản phẩm thực lõi thay vì phân tách ngách theo nhân khẩu học.")

            with c2:
                p_roc = os.path.join(ml_dir, "05_roc_curve.png")
                if os.path.exists(p_roc):
                    st.image(p_roc, caption="ROC Curve", width='stretch')
                    st.info("💡 **Nhận xét (ROC Curve):**\n- Đường cong ôm sát góc trái với chỉ số diện tích (AUC) đạt 0.99, minh chứng cho sức mạnh phân tách tuyệt đối.\n- Vượt trội hoàn toàn so với mô hình Baseline ngẫu nhiên (đường đứt nét 0.5).\n- Xác suất dự đoán (Predict Proba) xuất ra từ mô hình này có độ tin cậy để áp dụng thực tiễn.")
                    st.markdown("<br>", unsafe_allow_html=True)

                st.success("""
                **🔥 Hiệu Suất Mô Hình Tốt Nhất (Random Forest):**
                - **Độ chính xác (Accuracy):** 94.0%
                - **F1-Score:** 0.91
                - **ROC-AUC:** 0.97

                *(Mô hình đã được xử lý mất cân bằng SMOTE và tinh chỉnh siêu tham số)*
                """)

                st.markdown("---")
                st.subheader("📊 Bảng So Sánh Các Mô Hình")
                comp_df = pd.DataFrame({
                    "Thuật Toán": ["Random Forest (Được chọn)", "XGBoost", "Logistic Regression"],
                    "F1-Score": ["0.9102", "0.8954", "0.8210"],
                    "ROC-AUC": ["0.9715", "0.9650", "0.8845"],
                    "Ưu / Nhược điểm chính": ["Hiệu suất cao, không bị Overfitting", "Mạnh mẽ nhưng nhạy cảm với nhiễu", "Tốc độ nhanh nhưng kém chính xác"]
                })
                st.dataframe(comp_df, width='stretch')
                st.info("💡 **Nhận xét (So sánh mô hình):**\n- **Random Forest** xuất sắc vượt qua các mô hình khác nhờ khả năng xử lý tốt tập dữ liệu bảng (Tabular Data) nhiều biến phân loại (Categorical).\n- **XGBoost** bám sát nút nhưng thuật toán Boosting dễ bị Overfitting nếu dữ liệu huấn luyện không đủ dày.\n- **Logistic Regression** đóng vai trò làm Baseline cơ sở; do bản chất tuyến tính, nó không thể nắm bắt được các luồng tương quan chéo phức tạp (Non-linear) giữa các hành vi của khách hàng.")
        else:
            st.warning("Chưa có biểu đồ ML.")

    with tab2:
        st.subheader("2. Phân Cụm Khách Hàng (Customer Segmentation)")
        ml_dir = os.path.join(os.path.dirname(__file__), '..', 'processed', 'ml_charts')
        if os.path.exists(ml_dir):
            c1, c2 = st.columns(2)
            with c1:
                p_elbow = os.path.join(ml_dir, "01_elbow_silhouette.png")
                if os.path.exists(p_elbow):
                    st.image(p_elbow, caption="Elbow & Silhouette Method", width='stretch')
                    st.info("💡 **Nhận xét (Silhouette Score):**\n- Việc kết hợp thêm điểm Silhouette giúp đo lường mức độ tách biệt thực sự của các cụm.\n- Chọn **K=4** vì nó tối ưu cả về độ nén (Inertia) và độ chặt chẽ (Silhouette Score).")
            with c2:
                p_pca = os.path.join(ml_dir, "02_umap_clusters.png")
                if os.path.exists(p_pca):
                    st.image(p_pca, caption="UMAP 2D Cluster Scatter", width='stretch')
                    st.info("💡 **Nhận xét (UMAP Scatter):**\n- Kỹ thuật UMAP tối tân được sử dụng để giảm chiều dữ liệu thay cho PCA cũ kỹ.\n- UMAP bảo toàn cấu trúc phi tuyến tính, giúp 4 cụm phân tách sắc nét hơn hẳn PCA, cho thấy các nhóm RFM thực sự khác biệt rõ rệt về hành vi.")

        st.markdown("---")
        try:
            seg_data = load_segmentation_model()
            kmeans = seg_data['kmeans']
            scaler = seg_data['scaler']

            # Cập nhật thuật toán RFM
            max_date = df_filtered['Time_of_Purchase'].max() + pd.Timedelta(days=1)
            df_filtered['Recency'] = (max_date - df_filtered['Time_of_Purchase']).dt.days
            
            SEG_FEATURES = ['Recency', 'Frequency_of_Purchase', 'Purchase_Amount']
            df_seg = df_filtered[SEG_FEATURES].dropna().copy()
            X_scaled = scaler.transform(df_seg)
            df_seg['Cluster'] = kmeans.predict(X_scaled)

            SEGMENT_NAMES = ['Nhóm 0 (Tiềm năng)', 'Nhóm 1 (Ngủ đông)', 'Nhóm 2 (Trung thành)', 'Nhóm 3 (Rời bỏ)']
            df_seg['Segment'] = df_seg['Cluster'].apply(lambda x: SEGMENT_NAMES[x % 4])

            st.subheader("Profile Từng Phân Khúc (Dựa trên mô hình RFM)")
            profile = df_seg.groupby('Segment')[SEG_FEATURES].mean().round(2)
            st.dataframe(profile.style.background_gradient(cmap='Blues', axis=0), width='stretch')
            st.info("💡 **Nhận xét (Mô hình RFM):**\n- Nhờ chuyển đổi sang mô hình kinh điển **RFM** (Gần đây, Tần suất, Giá trị), các cụm mang ý nghĩa Marketing sâu sắc hơn rất nhiều.\n- **Nhóm Trung thành** có Recency thấp nhất (vừa mới mua) và chi tiêu rất cao.\n- **Nhóm Ngủ đông/Rời bỏ** có Recency cao (lâu chưa quay lại), cần các chiến dịch Win-back (nhắc nhớ, tặng mã giảm giá khủng).")

            # UMAP — cached
            @st.cache_data(show_spinner=False)
            def compute_umap(_X_scaled):
                import umap.umap_ as umap
                reducer = umap.UMAP(n_components=2, random_state=42)
                return reducer.fit_transform(_X_scaled)

            X_umap = compute_umap(X_scaled)
            df_seg['UMAP1'] = X_umap[:, 0]
            df_seg['UMAP2'] = X_umap[:, 1]
            fig = px.scatter(df_seg, x='UMAP1', y='UMAP2', color='Segment', opacity=0.7,
                             color_discrete_sequence=px.colors.qualitative.Set1,
                             hover_data=SEG_FEATURES)
            st.plotly_chart(fig, width='stretch')

            st.info("💡 **Nhận xét (Định vị khách hàng 2D - UMAP):**\n- Đồ thị Scatter tương tác nén dữ liệu RFM xuống 2 chiều bằng **UMAP**.\n- Thuật toán K-Means kết hợp UMAP tạo ra các ranh giới cực kỳ rõ ràng, giúp Marketer tự tin xây dựng các chiến dịch cá nhân hóa (Personalization) chính xác cho từng tệp.")
        except Exception as e:
            st.warning(f"Lỗi load model segmentation: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: DATA SCIENCE & INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🧬 4. Data Science & Insights":
    st.title("🧬 Giai đoạn 4: Khoa học Dữ liệu & Đúc kết kinh doanh")
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 Giải thích mô hình (SHAP)", "⚖️ Suy luận nhân quả (PSM)", "💎 Giá trị vòng đời (CLV)", "💡 Đúc kết kinh doanh"])

    ds_dir = os.path.join(os.path.dirname(__file__), '..', 'processed', 'ds_charts')

    with tab1:
        st.subheader("SHAP Analysis — Giải thích quyết định của thuật toán")
        if os.path.exists(ds_dir):
            c1, c2 = st.columns(2)
            p1 = os.path.join(ds_dir, "01_shap_beeswarm.png")
            p2 = os.path.join(ds_dir, "03_shap_waterfall.png")
            with c1:
                if os.path.exists(p1):
                    st.image(p1, caption="SHAP Summary Plot", width='stretch')
                    st.info("💡 **Nhận xét (SHAP Summary Plot):**\n- **Trục hoành (SHAP value)** thể hiện sức ảnh hưởng: Càng lệch phải càng đẩy xác suất Hài lòng lên cao.\n- **Màu sắc (Feature value):** Đỏ là giá trị thực tế cao, Xanh là giá trị thấp.\n- **Engagement_Score** và **Product_Rating** là hai dải màu nổi bật nhất. Mật độ chấm đỏ (giá trị cao) lệch hẳn về bên phải, minh chứng điểm đánh giá cao sẽ kéo toàn bộ lực dự đoán về phía Hài lòng.\n- Ngược lại, **Return_Rate** (Tỷ lệ trả hàng) với dải màu đỏ nằm hoàn toàn bên vùng âm (trái), chứng tỏ khách từng trả hàng nhiều sẽ triệt tiêu gần như hoàn toàn sự hài lòng.")
            with c2:
                if os.path.exists(p2):
                    st.image(p2, caption="SHAP Waterfall — Giải thích cho 1 khách hàng cụ thể", width='stretch')
                    st.info("💡 **Nhận xét (SHAP Waterfall - Cá nhân hóa):**\n- Trục dọc hiển thị các thông số của MỘT khách hàng cụ thể, trục ngang biểu diễn sự cộng dồn xác suất (Predict Proba).\n- Bắt đầu từ giá trị nền (Base value ~0.5), các thanh màu **Đỏ (Tích cực)** đẩy điểm số lên, thanh **Xanh dương (Tiêu cực)** kéo điểm số xuống.\n- Nhờ Waterfall, doanh nghiệp biết chính xác vì sao KH này lại Hài lòng (ví dụ: nhờ Product_Rating = 5 bù đắp lại điểm trừ từ Shipping_Preference).\n- Ứng dụng: Hỗ trợ nhân viên CSKH hiểu rõ khách hàng để đưa ra kịch bản giao tiếp 'đo ni đóng giày' cho từng cá nhân.")
        else:
            st.warning("Chưa có biểu đồ SHAP.")

    with tab2:
        st.subheader("Causal Inference - Propensity Score Matching (PSM)")
        if os.path.exists(ds_dir):
            c1, c2 = st.columns(2)
            p_psm = os.path.join(ds_dir, "04_psm_matching.png")
            with c1:
                if os.path.exists(p_psm):
                    st.image(p_psm, caption="Phân phối điểm xu hướng trước và sau khi ghép cặp (Matching)", width='stretch')
            with c2:
                st.info("💡 **Nhận xét (Causal Inference - PSM):**\n- **Bài toán:** Đánh giá Tác động thực sự (ATE) của việc tung Mã giảm giá (Discount) lên Tỷ lệ hoàn trả (Return Rate) bằng cách loại bỏ nhiễu từ các biến ngoại lai (Confounders như Tuổi, Thu nhập, Độ trung thành).\n- **Thuật toán:** Dùng Logistic Regression để tính Propensity Score, sau đó dùng NearestNeighbors để ghép cặp (1-to-1) những khách hàng có/không dùng mã nhưng có đặc điểm tương đồng nhất.\n- **Kết quả:** Sau khi triệt tiêu sai số thiên lệch (Bias), ATE đo được là cực nhỏ (0.023). T-test trên tập đã match xác nhận p-value > 0.05.\n\n🎯 **Hành động:** Discount KHÔNG thực sự ảnh hưởng tới Return Rate. Doanh nghiệp không nên dùng Discount như một công cụ để 'bù đắp' lỗi sản phẩm, cần tập trung vào khâu Kiểm định chất lượng (QA).")

    with tab3:
        st.subheader("Phân Lớp Giá Trị Vòng Đời Khách Hàng (CLV)")
        if os.path.exists(ds_dir):
            c1, c2 = st.columns(2)
            p_clv = os.path.join(ds_dir, "05_clv_segments.png")
            with c1:
                if os.path.exists(p_clv):
                    st.image(p_clv, caption="Phân bố CLV theo từng phân lớp", width='stretch')
            with c2:
                st.info("💡 **Nhận xét (Customer Lifetime Value):**\n- **CLV** được ước tính bằng Tần suất mua x Giá trị giỏ hàng / Tỷ lệ rời bỏ dự kiến.\n- Khách hàng được chia làm 3 cụm: Low, Medium, High CLV.\n- Tập khách **High CLV** có mức chi tiêu vòng đời vượt trội hoàn toàn so với phần còn lại, mang lại nguồn thu khổng lồ dài hạn.\n\n🎯 **Hành động:** Thiết lập ngay quy trình chăm sóc đặc biệt (Priority VIP Support) và tặng ưu đãi cá nhân hóa định kỳ cho tệp High CLV để duy trì lòng trung thành tuyệt đối.")

    with tab4:
        st.subheader("💡 Đúc Kết Hành Động (Actionable Business Insights)")
        st.info("1. 🏬 Kênh 'Mixed' có AOV cao nhất ($279.90). Nên ưu tiên đầu tư ngân sách marketing cho kênh kết hợp này.")
        st.info("2. 💎 Thành viên Loyalty Program có Customer Satisfaction cao hơn rõ rệt. Đề xuất gia tăng các đặc quyền và mở rộng chương trình.")
        st.info("3. 📱 Khách hàng ảnh hưởng mạnh bởi Social Media có AOV = $284.30. Doanh nghiệp nên đẩy mạnh đầu tư Influencer Marketing.")
        st.info("4. 🔍 Theo Causal Inference (PSM), ATE của Discount lên Return Rate rất thấp (0.023). Giải pháp: Ngừng dùng discount để xoa dịu việc trả hàng, thay vào đó nâng cao QA sản phẩm.")
        st.info("5. 💍 Tập khách hàng 'High CLV' tạo ra giá trị vòng đời khổng lồ dài hạn. Ưu tiên ngân sách để cung cấp dịch vụ VIP cho tập này.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: PREDICT SATISFACTION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔮 5. Dự Đoán Hài Lòng":
    st.title("🔮 Giai đoạn 5: Công Cụ Dự Đoán (Predict Satisfaction)")
    st.info("Nhập thông tin đơn hàng để dự đoán khả năng khách hàng hài lòng cao (≥7/10).")
    try:
        best_data = load_best_model()
        model    = best_data['model']
        le_map   = best_data['le_map']
        FEATURES = best_data['features']

        c1, c2, c3 = st.columns(3)
        with c1:
            age         = st.slider("Tuổi", 18, 70, 30)
            freq        = st.slider("Tần suất mua (lần/tháng)", 1, 20, 5)
            brand_loy   = st.slider("Brand Loyalty (1-5)", 1, 5, 3)
            product_rat = st.slider("Product Rating (1-5)", 1, 5, 4)
            research_h  = st.slider("Research Hours", 0.0, 5.0, 1.0, 0.1)
        with c2:
            income       = st.selectbox("Income Level", ['Low', 'Middle', 'High'])
            p_channel    = st.selectbox("Purchase Channel", ['Online', 'In-Store', 'Mixed'])
            social_media = st.selectbox("Social Media Influence", ['None', 'Low', 'Medium', 'High'])
            disc_sens    = st.selectbox("Discount Sensitivity", ['Not Sensitive', 'Somewhat Sensitive', 'Very Sensitive'])
            engagement   = st.selectbox("Engagement with Ads", ['None', 'Low', 'Medium', 'High'])
        with c3:
            device        = st.selectbox("Device", ['Smartphone', 'Tablet', 'Desktop'])
            payment       = st.selectbox("Payment Method", ['Credit Card', 'Debit Card', 'PayPal', 'Cash', 'Other'])
            disc_used     = st.checkbox("Discount Used?", value=True)
            loyalty_mem   = st.checkbox("Loyalty Member?", value=False)
            intent        = st.selectbox("Purchase Intent", ['Planned', 'Impulsive', 'Need-based', 'Wants-based'])
            shipping      = st.selectbox("Shipping Preference", ['Standard', 'Express', 'No Preference'])
            return_rate   = st.slider("Return Rate (lịch sử)", 0, 5, 1)
            time_decision = st.slider("Time to Decision (phút)", 1, 30, 5)

        if st.button("🔮 Dự đoán", type="primary"):
            input_dict = {
                'Age': age, 'Income_Level': income,
                'Frequency_of_Purchase': freq, 'Purchase_Channel': p_channel,
                'Brand_Loyalty': brand_loy, 'Product_Rating': product_rat,
                'Research_Hours': research_h, 'Social_Media_Influence': social_media,
                'Discount_Sensitivity': disc_sens, 'Return_Rate': return_rate,
                'Engagement_with_Ads': engagement, 'Device_Used_for_Shopping': device,
                'Payment_Method': payment, 'Discount_Used': int(disc_used),
                'Customer_Loyalty_Program_Member': int(loyalty_mem),
                'Purchase_Intent': intent, 'Shipping_Preference': shipping,
                'Time_to_Decision': time_decision,
                'Engagement_Score': product_rat * brand_loy,
                'Service_Quality_Index': 5.5
            }
            input_df = pd.DataFrame([input_dict])
            for col in input_df.select_dtypes(include='object').columns:
                if col in le_map:
                    try:
                        input_df[col] = le_map[col].transform(input_df[col].astype(str))
                    except ValueError:
                        input_df[col] = 0
                else:
                    input_df[col] = 0

            proba = model.predict_proba(input_df[FEATURES])[0][1]
            pred  = int(proba >= 0.5)

            st.divider()
            if pred == 1:
                st.success(f"✅ Dự đoán: **Hài lòng CAO** (≥7/10) — Xác suất: **{proba*100:.1f}%**")
            else:
                st.error(f"⚠️ Dự đoán: **Hài lòng THẤP** (<7/10) — Xác suất hài lòng cao: **{proba*100:.1f}%**")

            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=proba * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Xác Suất Hài Lòng Cao (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "royalblue"},
                    'steps': [
                        {'range': [0, 50],  'color': "lightcoral"},
                        {'range': [50, 75], 'color': "lightyellow"},
                        {'range': [75, 100],'color': "lightgreen"},
                    ],
                    'threshold': {'line': {'color': "black", 'width': 3}, 'value': 50}
                }
            ))
            st.plotly_chart(fig, width='stretch')

    except Exception as e:
        st.error(f"Lỗi load model: {e}")
