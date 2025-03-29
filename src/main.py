import streamlit as st
from auth import Authentication
from wine_catalog import WineCatalog

def main():
    """Main application entry point"""
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Authentication flow
    auth = Authentication()
    
    if not st.session_state.authenticated:
        user = auth.login_page()
        if user:
            st.session_state.authenticated = True
            st.session_state.user = user
    
    # Wine catalog display
    if st.session_state.authenticated:
        catalog = WineCatalog()
        catalog.display_wine_cards()

if __name__ == "__main__":
    main()