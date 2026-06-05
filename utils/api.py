import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"}


def api_get(path: str, params: dict = None):
    resp = requests.get(f"{BACKEND_URL}{path}", headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, data: dict = None, files=None):
    if files:
        resp = requests.post(f"{BACKEND_URL}{path}", headers=_headers(), files=files)
    else:
        resp = requests.post(f"{BACKEND_URL}{path}", headers=_headers(), json=data)
    resp.raise_for_status()
    return resp.json()


def api_delete(path: str):
    resp = requests.delete(f"{BACKEND_URL}{path}", headers=_headers())
    resp.raise_for_status()
    return resp.json()
