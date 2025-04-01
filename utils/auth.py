import streamlit as st
from utils.config import WINES_CSV, RATINGS_CSV

def login_form():
    st.markdown("### Log in to Popotes")

    login_method = st.radio("Choose login method:", ["Nickname", "Email", "Phone"])
    user_input = st.text_input(f"Enter your {login_method.lower()}")

    if st.button("Log in"):
        if user_input.strip():
            st.session_state["user_id"] = user_input.strip().lower()
            st.success(f"Logged in as {user_input}")
            st.rerun()
        else:
            st.error("Please enter something.")

def logout_button():
    if "user_id" in st.session_state:
        st.markdown(f"**Logged in as:** `{st.session_state['user_id']}`")
        if st.button("Log out"):
            del st.session_state["user_id"]
            st.rerun()

def get_user_id():
    return st.session_state.get("user_id", None)
