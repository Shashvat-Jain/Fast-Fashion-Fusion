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

load_dotenv()


# Page 2: Trend Analysis
def trend_analysis_page():
    st.title("Trend Analysis")

    # uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    uploaded_file = {}
    if st.button("Retrieve Social Trends Data"):
        uploaded_file = "pages/ingested_data.csv"
    if uploaded_file:
        # Show progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Process file
        df = pd.read_csv(uploaded_file)
        processed_rows = []
        processed_data = []
        graph_placeholder = st.empty()
        table_placeholder = st.empty()
        required_columns = ["superclass", "class", "type", "variant", "style"]

        for index, row in df.iterrows():
            # Update progress
            progress = (index + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"Processing row {index + 1} of {len(df)}")

            # Process row (implement your processing logic here)
            # processed_row = process_row(row)
            # processed_rows.append(processed_row)

            for col in required_columns:
                processed_data.append(row[col])
            processed_rows.append(row)
            if index % 10 == 0 or index == len(df) - 1:
                frequency_df = pd.DataFrame(processed_data, columns=["value"])
                frequency_counts = frequency_df["value"].value_counts().reset_index()
                frequency_counts.columns = ["Value", "Frequency"]

                # Generate the graph
                fig = px.bar(
                    frequency_counts,
                    x="Value",
                    y="Frequency",
                    title="Frequency Analysis",
                    labels={"Value": "Category", "Frequency": "Count"},
                    text="Frequency",
                )
                graph_placeholder.plotly_chart(fig, use_container_width=True)
                processed_df = pd.DataFrame(processed_rows)
                table_placeholder.dataframe(processed_df)

            time.sleep(0.1)  # Simulate processing time

        # Create DataFrame from processed rows
        processed_df = pd.DataFrame(processed_rows)

        # Show processed data
        st.subheader("Processed Data")
        st.dataframe(processed_df)

        # Create frequency graphs
        # create_frequency_graphs(processed_df)

        # Update databases
        # update_databases(processed_df)


def process_row(row):
    # Implement your row processing logic here
    return {
        "superclass": "example_superclass",
        "subclass": "example_subclass",
        "subsubclass": "example_subsubclass",
        "category": "example_category",
        "feature_list": ["feature1", "feature2"],
        "style_attributes": {"attr1": "value1"},
    }


def create_frequency_graphs(df):
    # Create graphs for class hierarchies
    for column in ["superclass", "subclass", "subsubclass", "category"]:
        fig = px.bar(df[column].value_counts(), title=f"{column} Distribution")
        st.plotly_chart(fig)

    # Create graph for features
    feature_counts = {}
    for features in df["feature_list"]:
        for feature in features:
            feature_counts[feature] = feature_counts.get(feature, 0) + 1

    fig = px.bar(pd.Series(feature_counts), title="Feature Distribution")
    st.plotly_chart(fig)

    # Create graph for style attributes
    style_counts = {}
    for attrs in df["style_attributes"]:
        for key in attrs:
            style_counts[key] = style_counts.get(key, 0) + 1

    fig = px.bar(pd.Series(style_counts), title="Style Attributes Distribution")
    st.plotly_chart(fig)


trend_analysis_page()
