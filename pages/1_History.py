import streamlit as st
import pandas as pd
import os

# --- Load Data ---
wines = pd.read_csv("wines.csv")
if os.path.exists("ratings.csv"):
    ratings = pd.read_csv("ratings.csv")
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
            {'✅ Rated' if row['rated'] else '<span style="color:red;">Not Rated</span>'}
        </div>
        """, unsafe_allow_html=True)
