import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

_client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_ANON_KEY", ""),
)


def login(email: str, password: str) -> str:
    """Sign in and store token in session_state. Returns error message or None."""
    try:
        res = _client.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["token"] = res.session.access_token
        st.session_state["user_email"] = res.user.email
        return None
    except Exception as e:
        return str(e)


def logout() -> None:
    _client.auth.sign_out()
    st.session_state.clear()
