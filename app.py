import streamlit as st
from utils.auth import logout

st.set_page_config(page_title="myRev", layout="wide")

# if not st.session_state.get("token"):
#     pg = st.navigation([st.Page("pages/login.py", title="Login")], position="hidden")
#     pg.run()
#     st.stop()

# Sidebar
with st.sidebar:
    st.write(f"👤 {st.session_state.get('user_email', '')}")
    if st.button("Logout", use_container_width=True):
        logout()
        st.rerun()

pg = st.navigation([
    st.Page("pages/input.py", title="Input Manual", icon="✏️"),
    st.Page("pages/import_excel.py", title="Import Excel", icon="📂"),
    st.Page("pages/records.py", title="Data Penjualan", icon="📋"),
    st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
])
pg.run()
