import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
/* your metric-card (keep it) */
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}

div[data-baseweb="tag"], span[data-baseweb="tag"] {
    background-color: #f7b2cc !important;
    color: #3a0f22 !important;
}

</style>
""", unsafe_allow_html=True)

# Load and clean data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/data.csv', encoding='ISO-8859-1')
    except:
        df = pd.read_csv('data/online_retail.csv', encoding='ISO-8859-1')
    
    # Data cleaning
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df = df.dropna(subset=['Description'])
    
    # Create calculated columns
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    df['Date'] = df['InvoiceDate'].dt.date
    df['Hour'] = df['InvoiceDate'].dt.hour
    
    return df

# Load data
try:
    df = load_data()
    #st.sidebar.success("✅ Data loaded successfully!")
except Exception as e:
    st.error(f"⚠️ Error loading data: {e}")
    st.info("Make sure your CSV file is in the 'data/' folder")
    st.stop()

# Header
st.title("📊 Retail Analytics Dashboard")
st.markdown("**Interactive Business Intelligence Dashboard** | E-commerce Sales Analysis")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range
min_date = df['Date'].min()
max_date = df['Date'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Country filter
all_countries = sorted(df['Country'].unique().tolist())
default_countries = ['United Kingdom', 'France', 'Germany']
default_countries = [c for c in default_countries if c in all_countries]

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=default_countries if default_countries else all_countries[:3]
)

# Apply filters
filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Date'] >= date_range[0]) &
        (filtered_df['Date'] <= date_range[1])
    ]

if selected_countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]

# Sidebar stats
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Dataset Info**")
st.sidebar.info(f"""
- **Records**: {len(filtered_df):,}
- **Countries**: {filtered_df['Country'].nunique()}
- **Products**: {filtered_df['Description'].nunique():,}
- **Orders**: {filtered_df['InvoiceNo'].nunique():,}
""")

# Check if we have data
if len(filtered_df) == 0:
    st.warning("⚠️ No data available for selected filters. Please adjust your filters.")
    st.stop()

# KPIs Section
st.header("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df['TotalPrice'].sum()
total_orders = filtered_df['InvoiceNo'].nunique()
total_customers = filtered_df['CustomerID'].dropna().nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

with col1:
    st.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
with col2:
    st.metric("📦 Total Orders", f"{total_orders:,}")
with col3:
    st.metric("👥 Unique Customers", f"{int(total_customers):,}")
with col4:
    st.metric("🧾 Avg Order Value", f"${avg_order_value:.2f}")

st.markdown("---")

# Sales Trends
st.header("📅 Sales Trends Over Time")

col1, col2 = st.columns(2)

with col1:
    monthly_revenue = filtered_df.groupby('YearMonth')['TotalPrice'].sum().reset_index()
    monthly_revenue.columns = ['Month', 'Revenue']
    
    fig_revenue = px.line(
        monthly_revenue,
        x='Month',
        y='Revenue',
        title='Monthly Revenue Trend',
        markers=True
    )
    fig_revenue.update_traces(line_color='#1f77b4', line_width=3)
    fig_revenue.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        hovermode='x unified',
        template='plotly_dark'
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    monthly_orders = filtered_df.groupby('YearMonth')['InvoiceNo'].nunique().reset_index()
    monthly_orders.columns = ['Month', 'Orders']
    
    fig_orders = px.bar(
        monthly_orders,
        x='Month',
        y='Orders',
        title='Monthly Orders',
        #color='Orders',
        #color_continuous_scale='teal'
    )
    fig_orders.update_traces(marker_color="#7fb3d5")
    fig_orders.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Orders",
        showlegend=False,
        template='plotly_dark'
    )
    st.plotly_chart(fig_orders, use_container_width=True)

st.markdown("---")

# Geographic Analysis
st.header("🌍 Geographic Analysis")

col1, col2 = st.columns([2, 1])

with col1:
    country_stats = filtered_df.groupby('Country').agg({
        'TotalPrice': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    country_stats.columns = ['Country', 'Revenue', 'Orders']
    country_stats = country_stats.sort_values('Revenue', ascending=False).head(10)
    
    fig_countries = px.bar(
        country_stats,
        x='Country',
        y='Revenue',
        title='Top Countries by Revenue',
        #color='Revenue',
        #color_continuous_scale='blues'
    )
    fig_countries.update_traces(marker_color="#f4a3b8")
    fig_countries.update_layout(
        xaxis_title="Country",
        yaxis_title="Revenue ($)",
        showlegend=False,
        template='plotly_dark'
    )
    st.plotly_chart(fig_countries, use_container_width=True)

with col2:
    top5 = country_stats.head(5)
    fig_pie = px.pie(
        top5,
        values='Revenue',
        names='Country',
        title='Top Countries Share',
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
    

st.markdown("---")

# Product Analysis
st.header("🛍️ Product Performance")

col1, col2 = st.columns(2)

with col1:
    top_products_qty = filtered_df.groupby('Description')['Quantity'].sum().reset_index()
    top_products_qty = top_products_qty.sort_values('Quantity', ascending=False).head(10)
    
    fig_qty = px.bar(
        top_products_qty,
        y='Description',
        x='Quantity',
        title='Top 10 Products by Quantity Sold',
        orientation='h',
        #color='Quantity',
        #color_continuous_scale='greens'
    )
    fig_qty.update_traces(marker_color="#9adbb3")
    fig_qty.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Quantity Sold",
        yaxis_title="",
        showlegend=False,
        template='plotly_dark',
        height=400
    )
    st.plotly_chart(fig_qty, use_container_width=True)

with col2:
    top_products_rev = filtered_df.groupby('Description')['TotalPrice'].sum().reset_index()
    top_products_rev = top_products_rev.sort_values('TotalPrice', ascending=False).head(10)
    
    fig_rev = px.bar(
        top_products_rev,
        y='Description',
        x='TotalPrice',
        title='Top 10 Products by Revenue',
        orientation='h',
        #color='TotalPrice',
        #color_continuous_scale='oranges'
    )
    fig_rev.update_traces(marker_color="#f4c27a")
    fig_rev.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Revenue ($)",
        yaxis_title="",
        showlegend=False,
        template='plotly_dark',
        height=400
    )
    st.plotly_chart(fig_rev, use_container_width=True)

st.markdown("---")

# Time Analysis
st.header("⏰ Purchase Patterns")

col1, col2 = st.columns(2)

with col1:
    hourly = filtered_df.groupby('Hour')['InvoiceNo'].nunique().reset_index()
    hourly.columns = ['Hour', 'Orders']
    
    fig_hourly = px.line(
        hourly,
        x='Hour',
        y='Orders',
        title='Orders by Hour of Day',
        markers=True
    )
    fig_hourly.update_traces(line_color='#ff7f0e', line_width=3)
    fig_hourly.update_layout(
        xaxis_title="Hour (24h)",
        yaxis_title="Number of Orders",
        template='plotly_dark'
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

with col2:
    # Customer analysis
    customer_orders = filtered_df.groupby('CustomerID')['InvoiceNo'].nunique().reset_index()
    customer_orders.columns = ['CustomerID', 'OrderCount']
    
    order_distribution = customer_orders['OrderCount'].value_counts().sort_index().reset_index()
    order_distribution.columns = ['Orders', 'Customers']
    order_distribution = order_distribution[order_distribution['Orders'] <= 20]
    
    fig_dist = px.bar(
        order_distribution,
        x='Orders',
        y='Customers',
        title='Customer Order Distribution',
        #color='Customers',
        #color_continuous_scale='purples'
    )
    fig_dist.update_traces(marker_color="#b49ddb")
    fig_dist.update_layout(
        xaxis_title="Number of Orders",
        yaxis_title="Number of Customers",
        showlegend=False,
        template='plotly_dark'
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**📊 Built with Streamlit & Plotly** | Data: UCI Online Retail Dataset")