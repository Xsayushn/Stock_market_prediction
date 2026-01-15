import streamlit as st
from src.utils import read_json

USERS_FILE = "data/users.json"

def login_ui():
    st.sidebar.subheader("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    users = read_json(USERS_FILE, {"demo": "demo"})

    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Invalid username/password")

def require_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login_ui()
        st.stop()

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.rerun()
