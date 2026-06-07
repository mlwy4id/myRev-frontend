import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REQUIRED_COLS = {
    "tanggal",
    "bulan",
    "nama_item",
    "kategori",
    "quantity",
    "harga_satuan",
}

st.title("📂 Import Excel / CSV")

st.markdown("""
Upload file `.xlsx` atau `.csv` dengan kolom berikut:
`tanggal`, `bulan`, `nama_item`, `kategori`, `quantity`, `harga_satuan`
""")

uploaded = st.file_uploader("Pilih file", type=["xlsx", "csv"])

if uploaded:
    try:
        df = (
            pd.read_excel(uploaded)
            if uploaded.name.endswith(".xlsx")
            else pd.read_csv(uploaded)
        )
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        st.stop()

    missing = REQUIRED_COLS - set(df.columns.str.lower())
    if missing:
        st.error(
            f"Kolom tidak lengkap. Kolom yang kurang: **{', '.join(sorted(missing))}**"
        )
        st.stop()

    df.columns = df.columns.str.lower()
    st.success(f"{len(df)} baris ditemukan.")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

    if st.button("📤 Import", type="primary", use_container_width=True):
        token = st.session_state.get("token", "")
        uploaded.seek(0)
        try:
            with st.spinner("Mengimport data..."):
                resp = requests.post(
                    f"{BACKEND_URL}/api/v1/sales/import",
                    headers={"Authorization": f"Bearer {token}"},
                    files={"file": (uploaded.name, uploaded, uploaded.type)},
                )
            resp.raise_for_status()
            result = resp.json()
            st.success(
                f"Import selesai: **{result.get('imported', '?')}** record berhasil disimpan."
            )
        except requests.HTTPError as e:
            st.error(f"Import gagal: {e}")
        except Exception as e:
            st.error(f"Tidak dapat terhubung ke server: {e}")
