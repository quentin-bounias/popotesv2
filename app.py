import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from datetime import datetime
from utils.auth import login_form, logout_button, get_user_id

# ---------------------- Custom Functions ----------------------
def draw_rating(label, key):
    st.markdown(f"**{label}**")
    current = st.session_state.get(key, 0.0)
    html = '<div class="rating-container">'
    for i in range(1, 6):
        # Each circle = 0.5 step (clickable in halves)
        left = (i - 1) * 1.0
        half = left + 0.5

        # Determine how to color the circle
        if current >= i:
            cls = "full"
        elif current >= i - 0.5:
            cls = "half"
        else:
            cls = ""

        html += f"""
        <div class="rating-circle {cls}" onclick="document.getElementById('{key}').value='{half}'; document.forms[0].dispatchEvent(new Event('submit'));" title='{half}/5'></div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    # Hidden field to store the value
    value = st.text_input(f"{label} value", value=str(current), key=key)
    try:
        return float(value)
    except:
        return 0.0

# ---------------------- App Config & Auth ----------------------
st.set_page_config(page_title="Popotes", layout="centered")

# Show login form if user is not authenticated
if "user_id" not in st.session_state:
    login_form()
    st.stop()
else:
    logout_button()
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------- Load Data ----------------------
WINES_CSV = "wines.csv"
RATINGS_CSV = "ratings.csv"

wines = pd.read_csv(WINES_CSV)

# Initialize wine selection state
if "selected_wine_id" not in st.session_state:
    st.session_state["selected_wine_id"] = None

# Ensure ratings CSV exists and has the right structure
if not os.path.exists(RATINGS_CSV) or os.stat(RATINGS_CSV).st_size == 0:
    pd.DataFrame(columns=["user_id", "wine_id", "color", "nose", "taste", "keywords", "photo", "timestamp"]).to_csv(RATINGS_CSV, index=False)

# Load only ratings for the logged-in user
ratings = pd.read_csv(RATINGS_CSV).fillna("")
ratings = ratings[ratings["user_id"] == get_user_id()]

# ---------------------- Progress Tracker ----------------------
rated_wine_ids = ratings["wine_id"].unique()
progress = len(rated_wine_ids) / len(wines) * 100
st.markdown(f"### {int(progress)}% of wines rated 🍷")

# ---------------------- Wine Carousel ----------------------
unrated_wines = wines[~wines["id"].isin(rated_wine_ids)]

st.markdown("### Choose a wine to rate:")

html_blocks = []

# Build HTML content for the carousel
carousel_items = ""

for _, wine in unrated_wines.iterrows():
    name = wine["name"]
    region = wine["region"]
    grape = wine["grape"]

    carousel_items += f"""
    <div class="carousel-card">
        <div class="carousel-card-content">
            <div><strong>{name}</strong></div>
            <div>{region} • {grape}</div>
        </div>
    </div>
    """

carousel_html = f"""
<style>
.carousel-wrapper {{
    overflow-x: scroll;
    white-space: nowrap;
    padding: 1rem 0;
    -webkit-overflow-scrolling: touch;
}}
.carousel-card {{
    display: inline-block;
    vertical-align: top;
    width: 70vw;
    max-width: 300px;
    height: 340px;
    margin-right: 16px;
    background-color: #fff;
    border: 3px solid black;
    border-radius: 10px;
    box-shadow: 5px 5px 0 black;
    background-size: cover;
    background-position: center;
    position: relative;
    cursor: pointer;
}}
.carousel-card-content {{
    position: absolute;
    bottom: 0;
    width: 100%;
    background-color: rgba(255,255,255,0.85);
    padding: 0.5rem;
    font-size: 0.9rem;
    font-weight: bold;
    text-align: center;
}}
</style>

<div class="carousel-wrapper">
    {carousel_items}
</div>
"""

components.html(carousel_html, height=380, scrolling=True)

# Hidden field to capture selected wine ID (simulating JS click -> Python state)
selected = st.text_input("Selected wine ID", value=st.session_state.get("selected_wine_id", ""), key="wine_select_input")
if selected and selected.isnumeric():
    st.session_state["selected_wine_id"] = int(selected)

# ---------------------- Rating Form ----------------------
if st.session_state["selected_wine_id"]:
    wine = wines[wines["id"] == st.session_state["selected_wine_id"]].iloc[0]
    st.subheader(f"{wine['name']} ({wine['region']})")

    # Rating fields (0.5 increments)
    color = draw_rating("Color", "rating_color")
    nose = draw_rating("Nose", "rating_nose")
    taste = draw_rating("Taste", "rating_taste")

    # Optional photo upload
    photo = st.file_uploader("Optional photo", type=["png", "jpg", "jpeg"])
    photo_filename = ""
    if photo is not None:
        os.makedirs("data/photos", exist_ok=True)
        photo_filename = f"{get_user_id()}_{wine['id']}_{photo.name}"
        with open(os.path.join("data/photos", photo_filename), "wb") as f:
            f.write(photo.getbuffer())

    # Optional tags
    keywords = st.multiselect("Optional keywords", ["sweet", "dry", "fruity", "flinty", "smoky", "astringent"])

    # Save rating
    if st.button("Submit rating"):
        new_entry = {
            "user_id": get_user_id(),
            "wine_id": wine["id"],
            "color": color,
            "nose": nose,
            "taste": taste,
            "keywords": ", ".join(keywords),
            "photo": photo_filename,
            "timestamp": datetime.now().isoformat()
        }

        ratings = pd.concat([ratings, pd.DataFrame([new_entry])], ignore_index=True)
        ratings.to_csv(RATINGS_CSV, index=False)
        st.success("Rating submitted! 🥂")
        st.rerun()