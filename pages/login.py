import streamlit as st
from utils.api import api_post

st.title("🔐 Login")

if st.session_state.get("token"):
    st.info("Anda sudah login.")
    if st.button("Ke Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login", type="primary", width="stretch")

if submitted:
    if not email or not password:
        st.error("Email dan password wajib diisi.")
    else:
        try:
            resp = api_post("/api/v1/auth/login", {"email": email, "password": password})
            st.session_state.token = resp.get("access_token", resp.get("token", ""))
            st.success("Login berhasil!")
            st.rerun()
        except Exception as e:
            st.error(f"Login gagal: {e}")

st.page_link("pages/register.py", label="Belum punya akun? Daftar di sini")
