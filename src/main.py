import streamlit as st
from auth import Authentication
from wine_catalog import WineCatalog
from wine_tasting import WineTasting

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

        # Assuming user is authenticated
    user_id = st.session_state.user['id']
    
    # Wine selection (this would typically come from a previous page)
    wine_id = st.number_input("Enter Wine ID to Taste", min_value=1)
    
    if st.button("Start Tasting"):
        tasting_page = WineTasting()
        tasting_page.display_wine_tasting_page(wine_id, user_id)

if __name__ == "__main__":
    main()