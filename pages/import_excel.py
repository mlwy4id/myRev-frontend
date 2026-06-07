import os
from io import BytesIO

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REQUIRED_COLS = {
    "tanggal",
    "nama_item",
    "kategori",
    "quantity",
    "harga_satuan",
}

st.title("📂 Import Excel / CSV")

st.markdown("""
Upload file `.xlsx` atau `.csv` dengan kolom berikut:
`tanggal`, `nama_item`, `kategori`, `quantity`, `harga_satuan`
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
    # Derive bulan from tanggal if not provided
    if "bulan" in df.columns:
        df["bulan"] = pd.to_numeric(df["bulan"], errors="coerce").fillna(0).astype(int)
    else:
        df["bulan"] = pd.to_datetime(df["tanggal"], errors="coerce").dt.month

    st.success(f"{len(df)} baris ditemukan.")
    st.dataframe(df.head(10), width="stretch", hide_index=True)

    if st.button("📤 Import", type="primary", width="stretch"):
        token = st.session_state.get("token", "")
        # Write corrected df to buffer
        buf = BytesIO()
        content_type = uploaded.type or "application/octet-stream"
        if uploaded.name.endswith(".csv"):
            df.to_csv(buf, index=False)
        else:
            df.to_excel(buf, index=False)
        buf.seek(0)
        try:
            with st.spinner("Mengimport data..."):
                resp = requests.post(
                    f"{BACKEND_URL}/api/v1/files/import",
                    headers={"Authorization": f"Bearer {token}"},
                    files={"file": ("corrected_" + uploaded.name, buf, content_type)},
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
