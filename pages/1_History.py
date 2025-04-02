import streamlit as st
import pandas as pd
import os
from utils.config import WINES_CSV, RATINGS_CSV
from utils.auth import get_user_id

# --- Data ---
WINES_CSV = "wines.csv"
RATINGS_CSV = "ratings.csv"

# --- Load Data ---
wines = pd.read_csv("wines.csv")
if os.path.exists("ratings.csv"):
    ratings = ratings = pd.read_csv(RATINGS_CSV).fillna("")
    ratings = ratings[ratings["user_id"] == get_user_id()]
else:
    ratings = pd.DataFrame(columns=["wine_id", "color", "nose", "taste", "keywords", "photo", "timestamp"])

# --- Merge and annotate ---
wines["rated"] = wines["id"].isin(ratings["wine_id"])

# --- Display progress ---
rated_count = wines["rated"].sum()
total_count = len(wines)
progress = int((rated_count / total_count) * 100)
st.markdown(f"### {progress}% of wines rated 🍷")

# --- Display wine cards ---
for _, row in wines.iterrows():
    with st.container():
        style = "opacity: 0.3;" if row["rated"] else ""
        st.markdown(f"""
        <div style="border: 3px solid black; padding: 1rem; margin: 0.5rem 0; {style} border-radius: 12px; box-shadow: 4px 4px 0px black;">
            <strong>{row['name']}</strong><br>
            <span style="font-size: 0.8rem; text-transform: uppercase;">{row['region']} – {row['grape']}</span><br>
        """, unsafe_allow_html=True)

        if row["rated"]:
            rating_row = ratings[ratings["wine_id"] == row["id"]].iloc[0]

            # Show photo preview if exists
            photo_filename = rating_row.get("photo", "")
            if isinstance(photo_filename, str) and photo_filename.strip():
                photo_path = os.path.join("data/photos", photo_filename)
                if os.path.exists(photo_path):
                    st.image(photo_path, width=150)

            # Show tag badges
            # tags = rating_row["keywords"].split(",") if rating_row["keywords"] else []
            # for tag in tags:
            #     tag = tag.strip()
            #     if tag:
            #         st.markdown(f"<span class='tag'>{tag}</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)