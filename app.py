import streamlit as st

st.set_page_config(page_title="myRev", layout="wide")

pg = st.navigation([
    st.Page("pages/input.py", title="Input Manual", icon="✏️"),
    st.Page("pages/import_excel.py", title="Import Excel", icon="📂"),
    st.Page("pages/records.py", title="Data Penjualan", icon="📋"),
    st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
])
pg.run()
