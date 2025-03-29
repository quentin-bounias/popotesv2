# src/auth.py
import streamlit as st
from database import UserDatabase
import base64

class Authentication:
    def __init__(self):
        """Initialize authentication system"""
        self.db = UserDatabase()
    
    def login_page(self):
        """
        Create a unified login/registration page
        
        Returns:
        - Authenticated user details or None
        """
        st.title("Popotes - Wine Tasting Companion")
        
        # Check for existing session
        session_token = st.experimental_get_query_params().get('session_token')
        if session_token:
            user = self.db.validate_session(session_token[0])
            if user:
                return user
        
        # Login/Register tabs
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.header("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                user = self.db.authenticate_user(email, password)
                if user:
                    st.experimental_set_query_params(session_token=user['session_token'])
                    st.success(f"Welcome back, {user['name'] or 'Wine Taster'}!")
                    return user
        
        with tab2:
            st.header("Register")
            new_email = st.text_input("Email", key="register_email")
            new_password = st.text_input("Password", type="password", key="register_password")
            name = st.text_input("Name (Optional)")
            profile_picture = st.file_uploader("Upload Profile Picture (Optional)", type=['jpg', 'png'])
            
            if st.button("Register"):
                # Validate inputs
                if not new_email or not new_password:
                    st.error("Email and password are required")
                    return None
                
                # Process profile picture if uploaded
                profile_pic_bytes = None
                if profile_picture:
                    profile_pic_bytes = profile_picture.read()
                
                # Attempt registration
                result = self.db.register_user(new_email, new_password, name)
                if result:
                    # If registration successful and picture uploaded, update profile
                    user = self.db.authenticate_user(new_email, new_password)
                    if user and profile_pic_bytes:
                        self.db.update_user_profile(
                            user['id'], 
                            name=name, 
                            profile_picture=profile_pic_bytes
                        )
                    
                    st.success("Registration successful! You can now log in.")
        
        return None