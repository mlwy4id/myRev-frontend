import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def _handle_response(resp):
    if resp.status_code == 401:
        st.session_state.clear()
        st.rerun()
    resp.raise_for_status()
    return resp.json()


def _headers():
    token = st.session_state.get("token", "")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_get(path: str, params: dict = None):
    resp = requests.get(f"{BACKEND_URL}{path}", params=params, headers=_headers())
    return _handle_response(resp)


def api_post(path: str, data: dict = None, files=None):
    if files:
        resp = requests.post(f"{BACKEND_URL}{path}", files=files, headers=_headers())
    else:
        resp = requests.post(f"{BACKEND_URL}{path}", json=data, headers=_headers())
    return _handle_response(resp)


def api_put(path: str, data: dict = None):
    resp = requests.put(f"{BACKEND_URL}{path}", json=data, headers=_headers())
    return _handle_response(resp)


def api_delete(path: str):
    resp = requests.delete(f"{BACKEND_URL}{path}", headers=_headers())
    return _handle_response(resp)
