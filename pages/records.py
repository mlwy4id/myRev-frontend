import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.api import api_delete, api_get, api_put

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

if "records_kategori" not in st.session_state:
    try:
        raw = api_get("/api/v1/sales/categories")
        if raw and isinstance(raw[0], dict):
            st.session_state.records_kategori = ["Semua"] + [c["nama"] for c in raw]
        else:
            st.session_state.records_kategori = ["Semua"] + list(raw)
    except Exception:
        st.session_state.records_kategori = ["Semua"]
KATEGORI = st.session_state.records_kategori
KATEGORI_ITEM = KATEGORI[1:]
BULAN = {
    0: "Semua",
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "Mei",
    6: "Jun",
    7: "Jul",
    8: "Ags",
    9: "Sep",
    10: "Okt",
    11: "Nov",
    12: "Des",
}

st.title("📋 Data Penjualan")

if "page" not in st.session_state:
    st.session_state.page = 1
if "filter_key" not in st.session_state:
    st.session_state.filter_key = ""
if "drawer" not in st.session_state:
    st.session_state.drawer = None


def toggle_drawer(item_id):
    st.session_state.drawer = None if st.session_state.drawer == item_id else item_id

with st.sidebar:
    st.subheader("Filter")
    bulan = st.selectbox(
        "Bulan", options=list(BULAN.keys()), format_func=lambda x: BULAN[x]
    )
    kategori = st.selectbox("Kategori", KATEGORI)
    nama_item = st.text_input("Nama Item")
    tanggal_dari = st.date_input("Tanggal Dari", value=None)
    tanggal_sampai = st.date_input("Tanggal Sampai", value=None)
    page_size = st.selectbox("Per Halaman", [10, 25, 50, 100, 200], index=3)

    export_params = {}
    if bulan:
        export_params["bulan"] = bulan
    if kategori != "Semua":
        export_params["kategori"] = kategori
    if nama_item:
        export_params["nama_item"] = nama_item
    try:
        headers = {}
        token = st.session_state.get("token", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(f"{BACKEND_URL}/api/v1/files/export", params=export_params, headers=headers, stream=True)
        resp.raise_for_status()
        st.download_button(
            "📥 Export XLSX",
            data=resp.content,
            file_name="data_penjualan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
    except Exception:
        pass

# Reset page when filters change
current_filter = f"{bulan}_{kategori}_{nama_item}_{tanggal_dari}_{tanggal_sampai}_{page_size}"
if current_filter != st.session_state.filter_key:
    st.session_state.filter_key = current_filter
    st.session_state.page = 1

params = {"page": st.session_state.page, "page_size": page_size}
if bulan:
    params["bulan"] = bulan
if kategori != "Semua":
    params["kategori"] = kategori
if nama_item:
    params["nama_item"] = nama_item
if tanggal_dari:
    params["tanggal_dari"] = str(tanggal_dari)
if tanggal_sampai:
    params["tanggal_sampai"] = str(tanggal_sampai)

try:
    with st.spinner("Memuat data..."):
        data = api_get("/api/v1/sales", params=params)
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
        c3.markdown(
            f"Rp {item['total_harga']:,.0f}  \n`{item['quantity']} × Rp {item['harga_satuan']:,.0f}`"
        )
        c4.button("⋮", key=f"menu_{item['id']}", help="Opsi", on_click=toggle_drawer, args=(item["id"],))

    # Action buttons (toggle)
    if st.session_state.get("drawer") == item["id"]:
        ac1, ac2 = st.columns([1, 1])
        if ac1.button("✏️ Edit", key=f"act_edit_{item['id']}", width="stretch"):
            st.session_state.edit_id = item["id"]
            st.session_state.drawer = None
            st.rerun()
        if ac2.button("🗑️ Hapus", key=f"act_del_{item['id']}", width="stretch"):
            try:
                api_delete(f"/api/v1/sales/{item['id']}")
                st.session_state.drawer = None
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menghapus: {e}")

    # Edit form
    if st.session_state.get("edit_id") == item["id"]:
        with st.container(border=True):
            st.markdown(f"**✏️ Edit: {item['nama_item']}**")
            ec1, ec2 = st.columns(2)
            new_nama = ec1.text_input(
                "Nama Item", value=item["nama_item"], key=f"enama_{item['id']}"
            )
            new_kat = ec2.selectbox(
                "Kategori",
                KATEGORI_ITEM,
                index=KATEGORI_ITEM.index(item["kategori"])
                if item["kategori"] in KATEGORI_ITEM
                else 0,
                key=f"ekat_{item['id']}",
            )
            ec3, ec4, ec5 = st.columns(3)
            new_qty = ec3.number_input(
                "Qty",
                min_value=1,
                step=1,
                value=item["quantity"],
                key=f"eqty_{item['id']}",
            )
            new_hrg = ec4.number_input(
                "Harga Satuan",
                min_value=0,
                step=1000,
                value=item["harga_satuan"],
                key=f"ehrg_{item['id']}",
            )
            new_tgl = ec5.date_input(
                "Tanggal",
                value=date.fromisoformat(item["tanggal"])
                if isinstance(item["tanggal"], str)
                else item["tanggal"],
                key=f"etgl_{item['id']}",
            )
            ecol1, ecol2 = st.columns(2)
            if ecol1.button(
                "💾 Simpan",
                type="primary",
                width="stretch",
                key=f"esave_{item['id']}",
            ):
                try:
                    api_put(
                        f"/api/v1/sales/{item['id']}",
                        {
                            "tanggal": str(new_tgl),
                            "bulan": new_tgl.month,
                            "nama_item": new_nama,
                            "kategori": new_kat,
                            "quantity": new_qty,
                            "harga_satuan": new_hrg,
                        },
                    )
                    st.session_state.edit_id = None
                    st.success("Berhasil diupdate!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal mengupdate: {e}")
            if ecol2.button(
                "Batal", width="stretch", key=f"ecancel_{item['id']}"
            ):
                st.session_state.edit_id = None
                st.rerun()

st.divider()

# Pagination
pc1, pc2, pc3 = st.columns([2, 1, 2])
if pc1.button(
    "⬅ Sebelumnya", disabled=st.session_state.page <= 1, width="stretch"
):
    st.session_state.page -= 1
    st.rerun()
pc2.markdown(
    f"<div style='text-align:center;padding-top:8px'><b>Halaman {st.session_state.page}</b></div>",
    unsafe_allow_html=True,
)
if pc3.button("Berikutnya ➡", disabled=len(data) < page_size, width="stretch"):
    st.session_state.page += 1
    st.rerun()
