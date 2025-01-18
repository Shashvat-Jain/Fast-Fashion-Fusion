import streamlit as st
import time
import pandas as pd
import sqlite3
from backend.feature_extraction_models import call_from_frontend

ingested_csv_path = "backend/data/manual_ingested_data.csv"
extracted_db_path = "backend/data/extracted_data.db"

def image_context_extraction_page():
    st.title("Image Context Extraction")

    num_images = st.number_input("Number of Images", min_value=1, step=1, value=1)
    image_links = []
    image_texts = []

    for i in range(num_images):
        col1, col2, col3 = st.columns([1, 4, 4])
        with col1:
            image_no = st.text_input(label="",placeholder=f"Img {i}", disabled=True)
        with col2:
            image_link = st.text_input(label="",placeholder="Enter Image link", key=f"image_link_{i}")
            image_links.append(image_link)
        with col3:
            image_text = st.text_input(label="",placeholder=f"Enter Image Text Context {i + 1} (if available):")
            image_texts.append(image_text)

    data = {"sno": [], "post_image_urls": [], "post_text": []}
    for i, (image_link, image_text) in enumerate(zip(image_links, image_texts)):
        data["sno"].append(i)
        data["post_image_urls"].append(image_link)
        data["post_text"].append(image_text)

    
    df = pd.DataFrame(data)
    df.to_csv(ingested_csv_path, index=False)

    st.write("----------------")
    if st.button("Extract", key="extract_button", help="Click to start extraction"):
        with st.spinner("Processing..."):
            call_from_frontend(csv_path_in=ingested_csv_path, db_path_out=extracted_db_path)

        # Read extracted_data.db
        st.write("")
        st.subheader("Extracted Information")
        st.write("----------------")

        conn = sqlite3.connect(extracted_db_path)
        extracted_df = pd.read_sql_query("SELECT * FROM extracted_data", conn)
        conn.close()

        while extracted_df.empty or extracted_df[['image_description', 'style_attributes', 'superclass', 'class', 'type', 'variant', 'style']].isnull().all().all():
            time.sleep(1)  # Check every second
            conn = sqlite3.connect(extracted_db_path)
            extracted_df = pd.read_sql_query("SELECT * FROM extracted_data", conn)
            conn.close()

        st.dataframe(extracted_df)

image_context_extraction_page()