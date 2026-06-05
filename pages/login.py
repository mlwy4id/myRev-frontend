import streamlit as st

from utils.auth import login


_, col2, _ = st.columns([1, 2, 1])
with col2:
    st.title("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("Email dan password wajib diisi.")
    else:
        err = login(email, password)
        if err:
            st.error(f"Login gagal: {err}")
        else:
            st.rerun()
