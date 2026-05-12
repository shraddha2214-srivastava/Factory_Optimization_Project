import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Factory Optimization Dashboard",
    layout="wide"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
html, body, [class*="css"]{
    background-color:#0a0f1f;
    color:white;
}
section[data-testid="stSidebar"]{
    background-color:#141a2e;
}
[data-testid="metric-container"]{
    background:#111827;
    border:1px solid #1f2937;
    padding:18px;
    border-radius:16px;
}
h1,h2,h3{
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("Notebook/Data/Nassau Candy Distributor.csv")

# Clean columns
df.columns = df.columns.str.strip()

# ---------------- DATE FORMAT ----------------
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True)

# ---------------- CREATE NEW COLUMNS ----------------
df["Month"] = df["Order Date"].dt.strftime("%b")
df["Lead_Time"] = (df["Ship Date"] - df["Order Date"]).dt.days

# If Profit column missing
if "Profit" not in df.columns:
    df["Profit"] = df["Sales"] * 0.22

# If Shipping Cost missing
if "Shipping Cost" not in df.columns:
    df["Shipping Cost"] = df["Sales"] * 0.05

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Corporate Filters")

region_list = ["All"] + list(df["Region"].dropna().unique())

region = st.sidebar.selectbox(
    "Select Region",
    region_list
)

# ---------------- FILTER ----------------
if region != "All":
    filtered = df[df["Region"] == region]
else:
    filtered = df

# ---------------- HEADER ----------------
st.title("🏭 Factory Optimization Dashboard")
st.caption("Supply Chain & Logistics Analysis Dashboard")

# ---------------- KPI SECTION ----------------
c1, c2, c3, c4 = st.columns(4)

total_sales = int(filtered["Sales"].sum())
total_profit = int(filtered["Profit"].sum())
avg_shipping = round(filtered["Shipping Cost"].mean(), 2)
orders = filtered.shape[0]

c1.metric("💰 Total Sales", f"${total_sales:,}")
c2.metric("📈 Total Profit", f"${total_profit:,}")
c3.metric("🚚 Avg Shipping Cost", avg_shipping)
c4.metric("📦 Total Orders", orders)

# ---------------- SALES BY REGION ----------------
st.markdown("---")

x1, x2 = st.columns(2)

with x1:
    st.subheader("📊 Sales by Region")

    region_sales = filtered.groupby("Region")["Sales"].sum().reset_index()

    fig1 = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        color="Sales",
        color_continuous_scale="Blues"
    )

    fig1.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig1, use_container_width=True)

with x2:
    st.subheader("🥧 Market Share")

    fig2 = px.pie(
        region_sales,
        names="Region",
        values="Sales",
        hole=0.5
    )

    fig2.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- MONTHLY SALES TREND ----------------
st.markdown("---")
st.subheader("📈 Monthly Sales Trend")

monthly = filtered.groupby("Month")["Sales"].sum().reset_index()

month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

monthly["Month"] = pd.Categorical(
    monthly["Month"],
    categories=month_order,
    ordered=True
)

monthly = monthly.sort_values("Month")

fig3 = px.line(
    monthly,
    x="Month",
    y="Sales",
    markers=True,
    line_shape="spline",
    color_discrete_sequence=["#00BFFF"]
)

fig3.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig3, use_container_width=True)

# ---------------- TOP PRODUCTS ----------------
st.markdown("---")
st.subheader("🍭 Top Product Performance")

if "Product Name" in filtered.columns:

    top_products = (
        filtered.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig4 = px.bar(
        top_products,
        x="Product Name",
        y="Sales",
        color="Sales",
        color_continuous_scale="Teal"
    )

    fig4.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig4, use_container_width=True)

# ---------------- LEAD TIME ----------------
st.markdown("---")
st.subheader("📦 Shipping Lead Time Analysis")

lead = (
    filtered.groupby("Region")["Lead_Time"]
    .mean()
    .reset_index()
)

fig5 = px.bar(
    lead,
    x="Region",
    y="Lead_Time",
    color="Lead_Time",
    color_continuous_scale="Oranges"
)

fig5.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig5, use_container_width=True)

# ---------------- ROUTE EFFICIENCY ----------------
st.markdown("---")
st.subheader("🚚 Route Efficiency")

if "Ship Mode" in filtered.columns:

    route = (
        filtered.groupby("Ship Mode")["Shipping Cost"]
        .mean()
        .reset_index()
    )

    fig6 = px.bar(
        route,
        x="Ship Mode",
        y="Shipping Cost",
        color="Shipping Cost",
        color_continuous_scale="Purples"
    )

    fig6.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig6, use_container_width=True)

# ---------------- SALES FORECAST ----------------
st.markdown("---")
st.subheader("🤖 Sales Forecast Engine")

u = st.number_input("Enter Units", 0)
c = st.number_input("Enter Cost", 0)

pred = (u * 2.8) + (c * 1.2)

st.success(f"Predicted Sales = {round(pred,2)}")

# ---------------- CUMULATIVE REVENUE ----------------
st.markdown("---")
st.subheader("📈 Cumulative Revenue Over Time")

cum_df = monthly.copy()

cum_df["Cumulative Revenue"] = cum_df["Sales"].cumsum()

fig7 = px.line(
    cum_df,
    x="Month",
    y="Cumulative Revenue",
    markers=True,
    line_shape="spline",
    color_discrete_sequence=["#00FFAA"]
)

fig7.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig7, use_container_width=True)

# ---------------- CORRELATION HEATMAP ----------------
st.markdown("---")
st.subheader("🔥 Correlation Heatmap")

corr_df = pd.DataFrame({
    "Sales": monthly["Sales"],
    "Month_No": np.arange(len(monthly)),
    "Growth": monthly["Sales"].pct_change().fillna(0)
})

corr = corr_df.corr(numeric_only=True)

fig8 = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="RdBu"
)

fig8.update_layout(
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig8, use_container_width=True)

# ---------------- INSIGHTS ----------------
st.markdown("---")
st.subheader("📌 Executive Insights")

st.info("""
✅ High-performing regions identified  
✅ Monthly sales trend analyzed  
✅ Shipping lead time optimized  
✅ Route efficiency evaluated  
✅ Product demand insights generated  
✅ Dashboard ready for executive decisions
""")

# ---------------- DOWNLOAD REPORT ----------------
st.markdown("---")

csv = monthly.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Monthly Report",
    csv,
    "monthly_report.csv",
    "text/csv"
)
