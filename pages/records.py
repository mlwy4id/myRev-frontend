import streamlit as st
from utils.api import api_get, api_delete

KATEGORI = ["Semua", "Makanan", "Minuman", "Elektronik", "Pakaian", "Lainnya"]
BULAN = {0: "Semua", 1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei",
         6: "Jun", 7: "Jul", 8: "Ags", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}

st.title("📋 Data Penjualan")

with st.sidebar:
    st.subheader("Filter")
    bulan = st.selectbox("Bulan", options=list(BULAN.keys()), format_func=lambda x: BULAN[x])
    kategori = st.selectbox("Kategori", KATEGORI)

params = {}
if bulan:
    params["bulan"] = bulan
if kategori != "Semua":
    params["kategori"] = kategori

try:
    with st.spinner("Memuat data..."):
        data = api_get("/sales", params=params)
except Exception as e:
    st.error(f"Tidak dapat terhubung ke server: {e}")
    st.stop()

if not data:
    st.info("Tidak ada data.")
    st.stop()

for item in data:
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 0.5])
        c1.markdown(f"**{item['nama_item']}** `{item['kategori']}`")
        c2.markdown(f"📅 {item['tanggal']}")
        c3.markdown(f"Rp {item['total_harga']:,.0f}  \n`{item['quantity']} × Rp {item['harga_satuan']:,.0f}`")
        if c4.button("🗑️", key=f"del_{item['id']}"):
            try:
                api_delete(f"/sales/{item['id']}")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menghapus: {e}")
