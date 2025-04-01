import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.auth import login_form, logout_button, get_user_id

# --- Config ---
st.set_page_config(page_title="Popotes", layout="centered")
if "user_id" not in st.session_state:
    login_form()
    st.stop()
else:
    logout_button()
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Data ---
WINES_CSV = "wines.csv"
RATINGS_CSV = "ratings.csv"

wines = pd.read_csv(WINES_CSV)

if not os.path.exists(RATINGS_CSV) or os.stat(RATINGS_CSV).st_size == 0:
    pd.DataFrame(columns=["user_id", "wine_id", "color", "nose", "taste", "keywords", "photo", "timestamp"]).to_csv(RATINGS_CSV, index=False)

ratings = pd.read_csv(RATINGS_CSV)
ratings = ratings[ratings["user_id"] == get_user_id()]

# --- Progress ---
rated_wine_ids = ratings["wine_id"].unique()
progress = len(rated_wine_ids) / len(wines) * 100

st.markdown(f"### {int(progress)}% of wines rated 🍷")

# --- Wine Selection ---
unrated_wines = wines[~wines["id"].isin(rated_wine_ids)]

selected = st.selectbox("Select a wine to rate:", options=unrated_wines["name"])

if selected:
    wine = wines[wines["name"] == selected].iloc[0]

    st.subheader(f"{wine['name']} ({wine['region']})")

    st.markdown("#### Rate this wine")

    col1, col2, col3 = st.columns(3)
    with col1:
        color = st.number_input("Color", min_value=0.0, max_value=5.0, step=0.5, format="%.1f")
    with col2:
        nose = st.number_input("Nose", min_value=0.0, max_value=5.0, step=0.5, format="%.1f")
    with col3:
        taste = st.number_input("Taste", min_value=0.0, max_value=5.0, step=0.5, format="%.1f")

    photo = st.file_uploader("Optional photo", type=["png", "jpg", "jpeg"])
    keywords = st.multiselect("Optional keywords", ["sweet", "dry", "fruity", "flinty", "smoky", "astringent"])

    if st.button("Submit rating"):
        new_entry = {
            "user_id": get_user_id(),
            "wine_id": wine["id"],
            "color": color,
            "nose": nose,
            "taste": taste,
            "keywords": ", ".join(keywords),
            "photo": photo.name if photo else "",
            "timestamp": datetime.now().isoformat()
        }
        ratings = pd.concat([ratings, pd.DataFrame([new_entry])], ignore_index=True)
        ratings.to_csv(RATINGS_CSV, index=False)
        st.success("Rating submitted! 🥂")
        st.rerun()