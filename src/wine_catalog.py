import pandas as pd
import streamlit as st

class WineCatalog:
    def __init__(self, catalog_path='data/wines.csv'):
        """
        Initialize wine catalog from CSV
        
        Args:
        - catalog_path: Path to wine catalog CSV
        """
        self.wines = pd.read_csv(catalog_path)
    
    def display_wine_cards(self):
        """
        Display wine cards in a grid layout
        
        Each card contains:
        - Wine Name
        - Estate Name
        - Region
        - Appellation
        - Vintage
        """
        st.title("Wine Catalog")
        
        # Create columns for grid layout
        columns = st.columns(3)
        
        for index, wine in self.wines.iterrows():
            with columns[index % 3]:
                with st.container():
                    st.write(f"**{wine['wine_name']}**")
                    st.write(f"Estate: {wine['estate_name']}")
                    st.write(f"Region: {wine['region']}")
                    st.write(f"Appellation: {wine['appellation']}")
                    st.write(f"Vintage: {wine['vintage']}")
                    
                    if st.button(f"Rate Wine {wine['wine_name']}", key=f"rate_{index}"):
                        # Redirect to rating page for this specific wine
                        st.session_state.selected_wine = wine
                        st.experimental_rerun()