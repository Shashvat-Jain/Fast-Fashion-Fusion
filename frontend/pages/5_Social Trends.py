import os
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import json
from neo4j import GraphDatabase
import ast
from tqdm import tqdm
import networkx as nx
import plotly.graph_objects as go
import time
from streamlit_plotly_events import plotly_events
import ast
from dotenv import load_dotenv
from remove_fields_from_json import remove_fields_from_json
import requests
from PIL import Image
from io import BytesIO
import os
import shutil

# from backend import img2txt2txt_engine

# import sys

# sys.path.append("/C:/IITISM/Dev/Stylumia/stylumia-nxt/web-scraper-engine")

# import post_scraper
from top100_bs import top100
from profile_scraper import profiles_scraper
from posts_scraper import all_posts_info

load_dotenv()
main_folder = os.path.dirname(os.path.abspath(__file__))
main_folder = main_folder[:-6]
frontend_path = main_folder
backend_path = main_folder[:-8] + "backend\data"


def display_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        st.image(img, caption="Image Loaded Successfully", use_column_width=True)
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading image: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# Page 5:Social Trends page
def social_trends_page():

    st.title("Social Trends")
    st.write("Social Trends extracted from Instagram")
    if st.button("Get the List of Top 100 Insta Influencers"):
        top100_list = top100()
        st.write("Here is the list:")
        st.write(top100_list)

    if st.button("Get the profiles of Top 100 Insta Influencers"):
        posts_urls_list = profiles_scraper()
        st.write("Here is the list:")
        st.write(posts_urls_list)

    if st.button("Posts of Top 100"):
        # image_urls_list = [
        #     "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS1lIMq-ex44_W0z5WTCOgDDrqpYaSZ1LQOkA&s",
        #     "https://dist.neo4j.com/wp-content/uploads/20210621234221/0EdRw_utw9F-Hd7MW.png",
        # ]
        image_urls_list = all_posts_info()
        dict = {"post_image_urls": image_urls_list, "post_text": ""}
        dpf = pd.DataFrame(dict)
        dpf.to_csv("ingested_data.csv")
        csvfile_frontend_path = os.path.join(frontend_path, "ingested_data.csv")
        csvfile_backend_path = os.path.join(backend_path, "ingested_data.csv")
        shutil.move(csvfile_frontend_path, csvfile_backend_path)
        # img2txt2txt_engine()
        st.write("Here are the image URLs and the images:")
        for url in image_urls_list:
            display_image_from_url(url)
            # st.image(url, caption=f"Image from {url}", use_column_width=True)

    if st.button("Process Image URLs for Product Description and Style Attributes"):
        with st.spinner("Data is Processing"):
            time.sleep(1)

        st.success("Processing Complete !")

        file_path = frontend_path + "\pages\ingested_data.csv"
        df = pd.read_csv(file_path)
        df = df.iloc[:, :9]
        st.write("Here is the processed data:")
        st.dataframe(df)

    # if st.button("Get Trends analysis on the Verified Trends:"):
    #     uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    #     if uploaded_file:
    #         # Show progress bar
    #         progress_bar = st.progress(0)
    #         status_text = st.empty()

    #         # Process file
    #         df = pd.read_csv(uploaded_file)
    #         processed_rows = []
    #         processed_data = []
    #         graph_placeholder = st.empty()
    #         table_placeholder = st.empty()
    #         required_columns = ["superclass", "class", "type", "variant", "style"]

    #         for index, row in df.iterrows():
    #             # Update progress
    #             progress = (index + 1) / len(df)
    #             progress_bar.progress(progress)
    #             status_text.text(f"Processing row {index + 1} of {len(df)}")

    #             # Process row (implement your processing logic here)
    #             # processed_row = process_row(row)
    #             # processed_rows.append(processed_row)

    #             for col in required_columns:
    #                 processed_data.append(row[col])
    #             processed_rows.append(row)
    #             if index % 10 == 0 or index == len(df) - 1:
    #                 frequency_df = pd.DataFrame(processed_data, columns=["value"])
    #                 frequency_counts = (
    #                     frequency_df["value"].value_counts().reset_index()
    #                 )
    #                 frequency_counts.columns = ["Value", "Frequency"]

    #                 # Generate the graph
    #                 fig = px.bar(
    #                     frequency_counts,
    #                     x="Value",
    #                     y="Frequency",
    #                     title="Frequency Analysis",
    #                     labels={"Value": "Category", "Frequency": "Count"},
    #                     text="Frequency",
    #                 )
    #                 graph_placeholder.plotly_chart(fig, use_container_width=True)
    #                 processed_df = pd.DataFrame(processed_rows)
    #                 table_placeholder.dataframe(processed_df)

    #             time.sleep(0.1)  # Simulate processing time

    # Create DataFrame from processed rows
    # processed_df = pd.DataFrame(processed_rows)

    # Show processed data
    # st.subheader("Processed Data")
    # st.dataframe(processed_df)


social_trends_page()
