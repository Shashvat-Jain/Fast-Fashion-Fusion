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

    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    if uploaded_file:
        # Show progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Process file
        df = pd.read_csv(uploaded_file)
        processed_rows = []

        for index, row in df.iterrows():
            # Update progress
            progress = (index + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"Processing row {index + 1} of {len(df)}")

            # Process row (implement your processing logic here)
            processed_row = process_row(row)
            processed_rows.append(processed_row)

            time.sleep(0.1)  # Simulate processing time

        # Create DataFrame from processed rows
        processed_df = pd.DataFrame(processed_rows)

        # Show processed data
        st.subheader("Processed Data")
        st.dataframe(processed_df)

        # Create frequency graphs
        create_frequency_graphs(processed_df)

        # Update databases
        update_databases(processed_df)


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
    for column in ["superclass", "class", "type", "variant", "style"]:
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


# Page 3: Verification Page
def verification_page():
    st.title("Entity Verification")

    # Get unverified entities
    conn = sqlite3.connect("ontology.db")
    unverified_df = pd.read_sql_query("SELECT * FROM unverified_entities", conn)
    conn.close()

    # Display unverified entities
    st.subheader("Unverified Entities")
    for entity_type in [
        "superclass",
        "class",
        "type",
        "variant",
        "style",
    ]:
        st.markdown(f"### {entity_type.capitalize()}")

        entities = unverified_df[unverified_df["entity_type"] == entity_type]

        for _, row in entities.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(row["entity_value"])
            with col2:
                if st.button(f"Verify {row['entity_value']}"):
                    verify_entity(row["entity_type"], row["entity_value"])
                    st.experimental_rerun()


def verify_entity(entity_type, entity_value):
    # Move entity from unverified to verified database
    conn_verified = sqlite3.connect("verified_ontology.db")
    c_verified = conn_verified.cursor()
    c_verified.execute(
        "INSERT INTO verified_entities VALUES (?, ?)", (entity_type, entity_value)
    )
    conn_verified.commit()
    conn_verified.close()

    conn_ontology = sqlite3.connect("ontology.db")
    c_ontology = conn_ontology.cursor()
    c_ontology.execute(
        "DELETE FROM unverified_entities WHERE entity_type=? AND entity_value=?",
        (entity_type, entity_value),
    )
    conn_ontology.commit()
    conn_ontology.close()


verification_page()
