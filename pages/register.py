import streamlit as st
from utils.api import api_post

st.title("📝 Register")

with st.form("register_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")
    submitted = st.form_submit_button("Daftar", type="primary", width="stretch")

if submitted:
    if not email or not password:
        st.error("Email dan password wajib diisi.")
    elif password != confirm:
        st.error("Password tidak cocok.")
    else:
        try:
            api_post("/api/v1/auth/register", {"email": email, "password": password})
            st.success("Register berhasil! Silakan login.")
            st.switch_page("pages/login.py")
        except Exception as e:
            st.error(f"Register gagal: {e}")

st.page_link("pages/login.py", label="Sudah punya akun? Login di sini")
