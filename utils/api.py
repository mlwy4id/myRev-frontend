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


def api_get(path: str, params: dict = None):
    resp = requests.get(f"{BACKEND_URL}{path}", params=params)
    return _handle_response(resp)


def api_post(path: str, data: dict = None, files=None):
    if files:
        print(f"Body: {data}")
        resp = requests.post(f"{BACKEND_URL}{path}", files=files)

    else:
        resp = requests.post(f"{BACKEND_URL}{path}", json=data)
    return _handle_response(resp)


def api_put(path: str, data: dict = None):
    resp = requests.put(f"{BACKEND_URL}{path}", json=data)
    return _handle_response(resp)


def api_delete(path: str):
    resp = requests.delete(f"{BACKEND_URL}{path}")
    return _handle_response(resp)
