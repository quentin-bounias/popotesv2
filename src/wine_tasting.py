# src/wine_tasting.py
import streamlit as st
import pandas as pd
import sqlite3
from database import UserDatabase

class WineTasting:
    def __init__(self, db_path='data/wines.db'):
        """
        Initialize Wine Tasting Page
        
        Args:
        - db_path: Path to the wines database
        """
        self.db_path = db_path
    
    def _get_wine_details(self, wine_id):
        """
        Retrieve detailed information for a specific wine
        
        Args:
        - wine_id: Unique identifier for the wine
        
        Returns:
        - Dictionary of wine details
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT wine_name, estate_name, vintage, color, 
                       region, appellation 
                FROM wines 
                WHERE id = ?
            ''', (wine_id,))
            columns = ['wine_name', 'estate_name', 'vintage', 'color', 'region', 'appellation']
            wine = cursor.fetchone()
            
            return dict(zip(columns, wine)) if wine else None
    
    def _check_existing_tasting(self, user_id, wine_id):
        """
        Check if user has already tasted this wine
        
        Args:
        - user_id: User's unique identifier
        - wine_id: Wine's unique identifier
        
        Returns:
        - Boolean indicating if wine has been tasted before
        """
        with sqlite3.connect('data/users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) 
                FROM wine_tastings 
                WHERE user_id = ? AND wine_id = ?
            ''', (user_id, wine_id))
            return cursor.fetchone()[0] > 0
    
    def display_wine_tasting_page(self, wine_id, user_id):
        """
        Create a comprehensive wine tasting page
        
        Args:
        - wine_id: Unique identifier for the wine
        - user_id: User's unique identifier
        """
        # Check if user has already tasted this wine
        if self._check_existing_tasting(user_id, wine_id):
            st.error("You have already rated this wine. Each wine can only be rated once.")
            return
        
        # Retrieve wine details
        wine = self._get_wine_details(wine_id)
        
        if not wine:
            st.error("Wine not found")
            return
        
        # Display wine information
        st.title(f"Tasting: {wine['wine_name']}")
        
        # Wine Details Section
        st.header("Wine Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Estate:** {wine['estate_name']}")
            st.write(f"**Vintage:** {wine['vintage']}")
            st.write(f"**Color:** {wine['color']}")
        
        with col2:
            st.write(f"**Region:** {wine['region']}")
            st.write(f"**Appellation:** {wine['appellation']}")
        
        # Tasting Evaluation Section
        st.header("Your Tasting Evaluation")
        
        # Dress (Appearance) Rating
        st.subheader("Dress (Appearance)")
        dress_rating = st.slider(
            "Rate the wine's appearance", 
            min_value=0.0, 
            max_value=5.0, 
            step=0.5,
            key="dress_rating"
        )
        dress_notes = st.text_area("Dress Notes (Optional)", key="dress_notes")
        
        # Nose (Aroma) Rating
        st.subheader("Nose (Aroma)")
        nose_rating = st.slider(
            "Rate the wine's aroma", 
            min_value=0.0, 
            max_value=5.0, 
            step=0.5,
            key="nose_rating"
        )
        nose_notes = st.text_area("Nose Notes (Optional)", key="nose_notes")
        
        # Taste Rating
        st.subheader("Taste")
        taste_rating = st.slider(
            "Rate the wine's taste", 
            min_value=0.0, 
            max_value=5.0, 
            step=0.5,
            key="taste_rating"
        )
        taste_notes = st.text_area("Taste Notes (Optional)", key="taste_notes")
        
        # Overall Notes
        st.subheader("Overall Impression")
        overall_notes = st.text_area("Additional Tasting Notes (Optional)", key="overall_notes")
        
        # Submit Tasting
        if st.button("Submit Tasting"):
            # Calculate average rating
            avg_rating = round((dress_rating + nose_rating + taste_rating) / 3, 1)
            
            # Prepare tasting data
            tasting_data = {
                'user_id': user_id,
                'wine_id': wine_id,
                'dress_rating': dress_rating,
                'dress_notes': dress_notes,
                'nose_rating': nose_rating,
                'nose_notes': nose_notes,
                'taste_rating': taste_rating,
                'taste_notes': taste_notes,
                'overall_rating': avg_rating,
                'overall_notes': overall_notes
            }
            
            # Save to database
            self._save_tasting(tasting_data)
            
            st.success("Tasting submitted successfully!")
    
    def _save_tasting(self, tasting_data):
        """
        Save wine tasting to the database
        
        Args:
        - tasting_data: Dictionary containing tasting information
        """
        with sqlite3.connect('data/users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO wine_tastings (
                    user_id, wine_id, 
                    dress_rating, dress_notes,
                    nose_rating, nose_notes,
                    taste_rating, taste_notes,
                    overall_rating, overall_notes
                ) VALUES (
                    :user_id, :wine_id, 
                    :dress_rating, :dress_notes,
                    :nose_rating, :nose_notes,
                    :taste_rating, :taste_notes,
                    :overall_rating, :overall_notes
                )
            ''', tasting_data)
            conn.commit()