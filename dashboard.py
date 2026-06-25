import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os

# Set page config
st.set_page_config(
    page_title="E-Commerce Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for glassmorphic cards and typography
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Apply Outfit font globally */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* Custom header banner styling */
.header-container {
    background: linear-gradient(135deg, #101424 0%, #1a2238 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    border-left: 6px solid #6366f1;
}

.header-title {
    color: #ffffff;
    font-size: 32px;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}

.header-subtitle {
    color: #a5b4fc;
    font-size: 15px;
    margin-top: 6px;
    font-weight: 400;
    opacity: 0.9;
}

/* Glassmorphic metric card styling */
.glass-metric {
    background: rgba(21, 28, 44, 0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.glass-metric::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
}

.glass-metric:hover {
    transform: translateY(-4px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 12px 30px 0 rgba(99, 102, 241, 0.15);
}

.metric-label {
    font-size: 13px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}

.metric-yoy {
    display: inline-flex;
    align-items: center;
    font-size: 12px;
    font-weight: 600;
    margin-top: 10px;
    padding: 2px 8px;
    border-radius: 20px;
}

.yoy-positive {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
}

.yoy-negative {
    background-color: rgba(239, 68, 68, 0.15);
    color: #ef4444;
}

.yoy-neutral {
    background-color: rgba(107, 114, 128, 0.15);
    color: #9ca3af;
}

/* Custom expander header */
.streamlit-expanderHeader {
    background-color: #151c2c !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
}

/* Fix spacing */
div[data-testid="column"] {
    padding: 0 5px;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# DATA LOADING & CACHING
# ----------------------------------------------------
@st.cache_data
def load_datasets():
    # Verify file existence first
    fact_path = "data/Fact_Orders.csv"
    cust_path = "data/Dim_Customers.csv"
    prod_path = "data/Dim_Products.csv"
    
    if not (os.path.exists(fact_path) and os.path.exists(cust_path) and os.path.exists(prod_path)):
        st.error("Error: Dataset files not found. Please run the `generate_data.py` script first.")
        st.stop()
        
    fact_orders = pd.read_csv(fact_path)
    dim_customers = pd.read_csv(cust_path)
    dim_products = pd.read_csv(prod_path)
    
    # Merge datasets to create a master data model
    df = fact_orders.merge(dim_customers, on="Customer_ID", how="left")
    df = df.merge(dim_products, on="Product_ID", how="left")
    
    # Parse dates
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Ship_Date'] = pd.to_datetime(df['Ship_Date'])
    
    return df

df = load_datasets()

# ----------------------------------------------------
# HEADER SECTION
# ----------------------------------------------------
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 Executive Sales & Profit Intelligence Cockpit</h1>
    <div class="header-subtitle">Interactive Power BI  | Built with Python, NumPy & Pandas</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# FILTERS PANEL (Top-aligned row slicers)
# ----------------------------------------------------
with st.expander("🔍 Interactive Filter Panel (Slicers)", expanded=True):
    col_date, col_region, col_segment, col_category = st.columns(4)
    
    # 1. Date Filter
    min_date = df['Order_Date'].min().to_pydatetime()
    max_date = df['Order_Date'].max().to_pydatetime()
    
    with col_date:
        date_range = st.date_input(
            "Order Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Unpack dates safely
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = min_date.date()
            end_date = max_date.date()
            
    # 2. Region Slicer
    regions = sorted(df['Region'].unique())
    with col_region:
        selected_regions = st.multiselect("Select Regions", options=regions, default=[])
        
    # 3. Customer Segment Slicer
    segments = sorted(df['Segment'].unique())
    with col_segment:
        selected_segments = st.multiselect("Select Segments", options=segments, default=[])
        
    # 4. Product Category Slicer
    categories = sorted(df['Category'].unique())
    with col_category:
        selected_categories = st.multiselect("Select Categories", options=categories, default=[])

# Apply filters
filtered_df = df.copy()

if selected_regions:
    filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
if selected_segments:
    filtered_df = filtered_df[filtered_df['Segment'].isin(selected_segments)]
if selected_categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    
# Filter date range
filtered_df = filtered_df[
    (filtered_df['Order_Date'].dt.date >= start_date) & 
    (filtered_df['Order_Date'].dt.date <= end_date)
]

# ----------------------------------------------------
# METRICS & YOY CALCULATIONS
# ----------------------------------------------------
# Current metrics
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0.0
total_orders = filtered_df['Order_ID'].nunique()
aov = (total_sales / total_orders) if total_orders > 0 else 0.0

# Calculate Prior Year metrics for comparison
py_start = start_date - datetime.timedelta(days=365)
py_end = end_date - datetime.timedelta(days=365)

py_df = df.copy()
if selected_regions:
    py_df = py_df[py_df['Region'].isin(selected_regions)]
if selected_segments:
    py_df = py_df[py_df['Segment'].isin(selected_segments)]
if selected_categories:
    py_df = py_df[py_df['Category'].isin(selected_categories)]
    
py_df = py_df[
    (py_df['Order_Date'].dt.date >= py_start) & 
    (py_df['Order_Date'].dt.date <= py_end)
]

py_sales = py_df['Sales'].sum()
py_profit = py_df['Profit'].sum()
py_orders = py_df['Order_ID'].nunique()
py_profit_margin = (py_profit / py_sales * 100) if py_sales > 0 else 0.0
py_aov = (py_sales / py_orders) if py_orders > 0 else 0.0

# YoY Calculations
def calc_yoy_str(current, prior):
    if prior == 0:
        return "N/A YoY", "yoy-neutral"
    diff = ((current - prior) / prior) * 100
    if diff > 0:
        return f"▲ +{diff:.1f}% YoY", "yoy-positive"
    elif diff < 0:
        return f"▼ {diff:.1f}% YoY", "yoy-negative"
    else:
        return f"0.0% YoY", "yoy-neutral"

sales_yoy, sales_class = calc_yoy_str(total_sales, py_sales)
profit_yoy, profit_class = calc_yoy_str(total_profit, py_profit)
orders_yoy, orders_class = calc_yoy_str(total_orders, py_orders)

margin_diff = profit_margin - py_profit_margin
if margin_diff > 0:
    margin_yoy, margin_class = f"▲ +{margin_diff:.1f} pp YoY", "yoy-positive"
elif margin_diff < 0:
    margin_yoy, margin_class = f"▼ {margin_diff:.1f} pp YoY", "yoy-negative"
else:
    margin_yoy, margin_class = "0.0 pp YoY", "yoy-neutral"

aov_yoy, aov_class = calc_yoy_str(aov, py_aov)

# ----------------------------------------------------
# KPI CARDS RENDER
# ----------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="glass-metric">
        <div class="metric-label">Total Sales</div>
        <div class="metric-value">${total_sales:,.0f}</div>
        <span class="metric-yoy {sales_class}">{sales_yoy}</span>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="glass-metric">
        <div class="metric-label">Total Profit</div>
        <div class="metric-value">${total_profit:,.0f}</div>
        <span class="metric-yoy {profit_class}">{profit_yoy}</span>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="glass-metric">
        <div class="metric-label">Profit Margin</div>
        <div class="metric-value">{profit_margin:.1f}%</div>
        <span class="metric-yoy {margin_class}">{margin_yoy}</span>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="glass-metric">
        <div class="metric-label">Total Orders</div>
        <div class="metric-value">{total_orders:,}</div>
        <span class="metric-yoy {orders_class}">{orders_yoy}</span>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="glass-metric">
        <div class="metric-label">Avg Order Value</div>
        <div class="metric-value">${aov:,.2f}</div>
        <span class="metric-yoy {aov_class}">{aov_yoy}</span>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacing

# ----------------------------------------------------
# VISUALIZATIONS SECTION
# ----------------------------------------------------
row1_left, row1_right = st.columns([2, 1])

# --- Visual 1: Monthly Sales & Profit Trend (Left Column) ---
with row1_left:
    st.subheader("📈 Monthly Revenue & Profit Trend")
    if not filtered_df.empty:
        # Group by Month-Year
        filtered_df['YearMonth'] = filtered_df['Order_Date'].dt.to_period('M')
        trend_df = filtered_df.groupby('YearMonth')[['Sales', 'Profit']].sum().reset_index()
        trend_df['YearMonth'] = trend_df['YearMonth'].astype(str)
        trend_df = trend_df.set_index('YearMonth')
        
        # Display double area/line chart
        st.area_chart(trend_df, y=['Sales', 'Profit'], color=['#6366f1', '#10b981'])
    else:
        st.info("No data available for the selected filters.")

# --- Visual 2: Sales by Customer Segment (Right Column) ---
with row1_right:
    st.subheader("👥 Sales by Customer Segment")
    if not filtered_df.empty:
        segment_df = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
        segment_df = segment_df.set_index('Segment')
        
        # Display bar chart for Segment split
        st.bar_chart(segment_df, color='#a855f7')
    else:
        st.info("No data available.")

st.write("") # Spacing
row2_left, row2_right = st.columns(2)

# --- Visual 3: Sales by Product Sub-Category (Bottom Left) ---
with row2_left:
    st.subheader("📦 Sales by Product Sub-Category")
    if not filtered_df.empty:
        subcat_df = filtered_df.groupby('Sub_Category')['Sales'].sum().sort_values(ascending=True).reset_index()
        subcat_df = subcat_df.set_index('Sub_Category')
        st.bar_chart(subcat_df, color='#6366f1')
    else:
        st.info("No data available.")

# --- Visual 4: Top Profit States (Bottom Right) ---
with row2_right:
    st.subheader("📍 Profit Margin by State")
    if not filtered_df.empty:
        # Calculate Margin per State
        state_df = filtered_df.groupby('State').agg(
            Sales=('Sales', 'sum'),
            Profit=('Profit', 'sum')
        ).reset_index()
        state_df['Profit Margin %'] = (state_df['Profit'] / state_df['Sales']) * 100
        state_df = state_df.sort_values(by='Sales', ascending=False).head(10)
        state_df = state_df.set_index('State')
        
        # Show profit vs sales side-by-side or state margin table
        st.bar_chart(state_df[['Profit Margin %']], color='#10b981')
    else:
        st.info("No data available.")

st.write("") # Spacing

# ----------------------------------------------------
# DETAILED TRANSACTIONS TABLE
# ----------------------------------------------------
with st.expander("📄 Detailed Transactions Explorer", expanded=False):
    if not filtered_df.empty:
        # Display table with relevant columns, formatted nicely
        table_cols = ['Order_ID', 'Order_Date', 'Customer_Name', 'Segment', 'Region', 'State', 
                      'Category', 'Sub_Category', 'Product_Name', 'Quantity', 'Sales', 'Profit']
        
        # Formatting dictionaries
        format_dict = {
            'Sales': '${:,.2f}',
            'Profit': '${:,.2f}'
        }
        
        # Render clean search/dataframe view
        st.dataframe(
            filtered_df[table_cols].sort_values(by='Order_Date', ascending=False),
            use_container_width=True,
            column_config={
                "Sales": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                "Profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
                "Order_Date": st.column_config.DateColumn("Order Date"),
                "Quantity": st.column_config.NumberColumn("Quantity")
            }
        )
    else:
        st.info("No data available.")
