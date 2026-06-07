import streamlit as st

st.set_page_config(page_title="myRev", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = ""

if st.session_state.token:
    with st.sidebar:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    pages = [
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/input.py", title="Input Manual", icon="✏️"),
        st.Page("pages/records.py", title="Data Penjualan", icon="📋"),
        st.Page("pages/import_excel.py", title="Import Excel", icon="📂"),
    ]
else:
    pages = [
        st.Page("pages/login.py", title="Login", icon="🔐"),
        st.Page("pages/register.py", title="Register", icon="📝"),
    ]

pg = st.navigation(pages)
pg.run()
