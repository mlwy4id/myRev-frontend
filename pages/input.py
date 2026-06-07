from datetime import date

import pandas as pd
import streamlit as st

from utils.api import api_get, api_post

BASE_KATEGORI = ["Makanan", "Minuman", "Elektronik", "Pakaian"]

st.title("✏️ Input Manual")

# Init batch list
if "batch" not in st.session_state:
    st.session_state.batch = [{}]
if "custom_kategori" not in st.session_state:
    st.session_state.custom_kategori = []


def all_kategori():
    return BASE_KATEGORI + sorted(st.session_state.custom_kategori)


def empty_row():
    return {
        "tanggal": date.today(),
        "nama_item": "",
        "kategori": BASE_KATEGORI[0],
        "quantity": 1,
        "harga_satuan": 0,
    }


# Custom kategori management
with st.expander("Kelola Kategori", expanded=False):
    cc1, cc2 = st.columns([3, 1])
    new_kat = cc1.text_input(
        "Tambah kategori baru",
        key="new_kategori_input",
        label_visibility="collapsed",
        placeholder="Nama kategori baru...",
    )
    if cc2.button("Tambah", use_container_width=True) and new_kat.strip():
        if new_kat.strip() not in all_kategori():
            st.session_state.custom_kategori.append(new_kat.strip())
            st.rerun()
        else:
            st.warning("Kategori sudah ada.")
    if st.session_state.custom_kategori:
        st.write("Kategori khusus:")
        for j, k in enumerate(st.session_state.custom_kategori):
            if st.button(f"Hapus {k}", key=f"hapus_kat_{j}"):
                st.session_state.custom_kategori.pop(j)
                # Reset baris yang pakai kategori ini ke default
                for r in st.session_state.batch:
                    if r["kategori"] == k:
                        r["kategori"] = BASE_KATEGORI[0]
                st.rerun()

# Header kolom
kats = all_kategori()
cols = st.columns([1.5, 2, 1.5, 1, 1.5, 1.5, 0.5])
for label, col in zip(
    ["Tanggal", "Nama Item", "Kategori", "Qty", "Harga Satuan", "Total", ""], cols
):
    col.markdown(f"**{label}**")

# Render setiap baris
for i in range(len(st.session_state.batch)):
    row = st.session_state.batch[i]
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 2, 1.5, 1, 1.5, 1.5, 0.5])
    row["tanggal"] = c1.date_input(
        "",
        value=row.get("tanggal", date.today()),
        key=f"tgl_{i}",
        label_visibility="collapsed",
    )
    row["nama_item"] = c2.text_input(
        "",
        value=row.get("nama_item", ""),
        key=f"item_{i}",
        label_visibility="collapsed",
    )
    current_kat = row.get("kategori", BASE_KATEGORI[0])
    kat_index = kats.index(current_kat) if current_kat in kats else 0
    row["kategori"] = c3.selectbox(
        "",
        kats,
        index=kat_index,
        key=f"kat_{i}",
        label_visibility="collapsed",
    )
    row["quantity"] = c4.number_input(
        "",
        min_value=1,
        step=1,
        value=row.get("quantity", 1),
        key=f"qty_{i}",
        label_visibility="collapsed",
    )
    row["harga_satuan"] = c5.number_input(
        "",
        min_value=0,
        step=1000,
        value=row.get("harga_satuan", 0),
        key=f"hrg_{i}",
        label_visibility="collapsed",
    )
    subtotal = row["quantity"] * row["harga_satuan"]
    c6.markdown(
        f"<div style='padding-top:8px'>Rp {subtotal:,.0f}</div>",
        unsafe_allow_html=True,
    )
    if len(st.session_state.batch) > 1:
        if c7.button("🗑️", key=f"del_{i}"):
            st.session_state.batch.pop(i)
            st.rerun()

col_add, col_submit = st.columns([1, 7], vertical_alignment="center")
if col_add.button("➕ Tambah Item"):
    st.session_state.batch.append(empty_row())
    st.rerun()

if col_submit.button("💾  Simpan Semua", type="primary", use_container_width=True):
    errors = [
        i + 1
        for i, r in enumerate(st.session_state.batch)
        if not r.get("nama_item") or r.get("harga_satuan", 0) <= 0
    ]
    if errors:
        st.error(f"Baris {errors}: nama item wajib diisi dan harga satuan > 0.")
    else:
        try:
            for r in st.session_state.batch:
                api_post(
                    "/api/v1/sales",
                    {
                        "tanggal": str(r["tanggal"]),
                        "bulan": r["tanggal"].month,
                        "nama_item": r["nama_item"],
                        "kategori": r["kategori"],
                        "quantity": r["quantity"],
                        "harga_satuan": r["harga_satuan"],
                    },
                )
            st.success(f"{len(st.session_state.batch)} item berhasil disimpan!")
            st.session_state.batch = [empty_row()]
            st.rerun()
        except Exception as e:
            st.error(f"Gagal menyimpan: {e}")

st.divider()
st.subheader("10 Transaksi Terbaru")
try:
    data = api_get("/api/v1/sales", params={"page": 1, "size": 20})
    if data:
        df = pd.DataFrame(data)[
            [
                "tanggal",
                "nama_item",
                "kategori",
                "quantity",
                "harga_satuan",
                "total_harga",
            ]
        ]
        df.columns = [
            "Tanggal",
            "Nama Item",
            "Kategori",
            "Qty",
            "Harga Satuan",
            "Total",
        ]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data.")
except Exception as e:
    st.error(f"Tidak dapat memuat data: {e}")
