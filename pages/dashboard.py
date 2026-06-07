import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from utils.api import api_get

st.title("📊 Dashboard Analitik")

with st.sidebar:
    st.subheader("Filter")
    tahun = st.number_input("Tahun", min_value=2020, max_value=date.today().year, value=date.today().year, step=1)
    bulan = st.selectbox("Bulan", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                         format_func=lambda x: "Semua" if x == 0 else date(2000, x, 1).strftime("%B"))

params = {"tahun": tahun}
if bulan:
    params["bulan"] = bulan

try:
    with st.spinner("Memuat data analitik..."):
        analytics = api_get("/api/v1/sales/analytics", params=params)
except Exception as e:
    st.error(f"Tidak dapat terhubung ke server: {e}")
    st.stop()

# KPI Row
c1, c2, c3 = st.columns(3)
c1.metric("Total Transaksi", f"{analytics.get('total_transaksi', 0):,}")
c2.metric("Total Pendapatan", f"Rp {analytics.get('total_pendapatan', 0):,.0f}")
avg = analytics.get('total_pendapatan', 0) / max(analytics.get('total_transaksi', 1), 1)
c3.metric("Rata-rata per Transaksi", f"Rp {avg:,.0f}")

st.divider()

# Chart 1: Pendapatan per Kategori
if analytics.get("per_kategori"):
    df_kat = pd.DataFrame(analytics["per_kategori"])
    chart_kat = alt.Chart(df_kat).mark_bar().encode(
        x=alt.X("kategori:N", title="Kategori"),
        y=alt.Y("total_pendapatan:Q", title="Pendapatan (Rp)"),
        color=alt.Color("kategori:N", legend=None),
        tooltip=["kategori", "total_pendapatan"]
    ).properties(title="Pendapatan per Kategori", height=300)
    st.altair_chart(chart_kat, use_container_width=True)
else:
    st.info("Tidak ada data kategori.")

# Chart 2: Trend Harian
if analytics.get("trend_harian"):
    df_trend = pd.DataFrame(analytics["trend_harian"])
    chart_trend = alt.Chart(df_trend).mark_line(point=True).encode(
        x=alt.X("tanggal:T", title="Tanggal"),
        y=alt.Y("total_pendapatan:Q", title="Pendapatan (Rp)"),
        tooltip=["tanggal", "total_pendapatan"]
    ).properties(title="Trend Pendapatan Harian", height=300)
    st.altair_chart(chart_trend, use_container_width=True)
else:
    st.info("Tidak ada data trend harian.")

# Chart 3: Top 5 Item
if analytics.get("top_items"):
    df_top = pd.DataFrame(analytics["top_items"][:5])
    chart_top = alt.Chart(df_top).mark_bar().encode(
        x=alt.X("total_quantity:Q", title="Total Terjual"),
        y=alt.Y("nama_item:N", sort="-x", title="Item"),
        color=alt.Color("nama_item:N", legend=None),
        tooltip=["nama_item", "total_quantity"]
    ).properties(title="Top 5 Item Terlaris", height=300)
    st.altair_chart(chart_top, use_container_width=True)
else:
    st.info("Tidak ada data top item.")
