from datetime import date

import pandas as pd
import streamlit as st

from utils.api import api_get, api_post

st.title("✏️ Input Manual")

# Init session state
if "batch" not in st.session_state:
    st.session_state.batch = [{}]
if "kategori_list" not in st.session_state:
    try:
        raw = api_get("/api/v1/sales/categories")
        # support both list of strings and list of {nama: str}
        if raw and isinstance(raw[0], dict):
            st.session_state.kategori_list = [c["nama"] for c in raw]
        else:
            st.session_state.kategori_list = list(raw)
    except Exception:
        st.session_state.kategori_list = []


def empty_row():
    kats = st.session_state.kategori_list
    return {
        "tanggal": date.today(),
        "nama_item": "",
        "kategori": kats[0] if kats else "",
        "quantity": 1,
        "harga_satuan": 0,
    }


kats = st.session_state.kategori_list

# Header kolom
cols = st.columns([1.5, 2, 2, 1, 1.5, 1.5, 0.5])
for label, col in zip(
    ["Tanggal", "Nama Item", "Kategori", "Qty", "Harga Satuan", "Total", ""], cols
):
    col.markdown(f"**{label}**")

# Render setiap baris
for i in range(len(st.session_state.batch)):
    row = st.session_state.batch[i]
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 2, 2, 1, 1.5, 1.5, 0.5])
    row["tanggal"] = c1.date_input(
        "Tanggal",
        value=row.get("tanggal", date.today()),
        key=f"tgl_{i}",
        label_visibility="collapsed",
    )
    row["nama_item"] = c2.text_input(
        "Nama Item",
        value=row.get("nama_item", ""),
        key=f"item_{i}",
        label_visibility="collapsed",
    )
    current_kat = row.get("kategori", kats[0] if kats else "")
    kat_options = kats + ["+ Buat baru"] if kats else ["+ Buat baru"]
    kat_index = kat_options.index(current_kat) if current_kat in kat_options else len(kat_options) - 1
    selected = c3.selectbox(
        "Kategori",
        kat_options,
        index=kat_index,
        key=f"kat_{i}",
        label_visibility="collapsed",
    )
    if selected == "+ Buat baru":
        row["kategori"] = ""
    else:
        row["kategori"] = selected
    row["quantity"] = c4.number_input(
        "Qty",
        min_value=1,
        step=1,
        value=row.get("quantity", 1),
        key=f"qty_{i}",
        label_visibility="collapsed",
    )
    row["harga_satuan"] = c5.number_input(
        "Harga Satuan",
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

    # Input for new category name
    if row["kategori"] == "":
        new_name = c3.text_input(
            "Nama kategori baru",
            key=f"new_kat_{i}",
            label_visibility="collapsed",
            placeholder="Ketik kategori baru...",
        )
        if new_name.strip():
            row["kategori"] = new_name.strip()

col_add, col_submit = st.columns([1, 7], vertical_alignment="center")
if col_add.button("➕ Tambah Item"):
    st.session_state.batch.append(empty_row())
    st.rerun()

if col_submit.button("💾  Simpan Semua", type="primary", width="stretch"):
    errors = [
        i + 1
        for i, r in enumerate(st.session_state.batch)
        if not r.get("nama_item") or not r.get("kategori") or r.get("harga_satuan", 0) <= 0
    ]
    if errors:
        st.error(f"Baris {errors}: nama item, kategori, dan harga satuan > 0 wajib diisi.")
    else:
        try:
            server_kats = kats
            for r in st.session_state.batch:
                kat = r["kategori"]
                api_post(
                    "/api/v1/sales",
                    {
                        "tanggal": str(r["tanggal"]),
                        "bulan": r["tanggal"].month,
                        "nama_item": r["nama_item"],
                        "kategori": kat,
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
    data = api_get("/api/v1/sales", params={"page": 1, "page_size": 20})
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
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("Belum ada data.")
except Exception as e:
    st.error(f"Tidak dapat memuat data: {e}")
