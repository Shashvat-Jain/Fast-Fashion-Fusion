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


# Initialize databases
def init_sqlite_db():
    # Create verified ontology database
    conn_verified = sqlite3.connect("verified_ontology.db")
    c = conn_verified.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS verified_entities
                 (entity_type TEXT, entity_value TEXT, PRIMARY KEY (entity_type, entity_value))"""
    )
    conn_verified.commit()
    conn_verified.close()

    # Create unverified ontology database
    conn_ontology = sqlite3.connect("ontology.db")
    c = conn_ontology.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS unverified_entities
                 (entity_type TEXT, entity_value TEXT, PRIMARY KEY (entity_type, entity_value))"""
    )
    conn_ontology.commit()
    conn_ontology.close()


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]


NEOCONN = None


def main():
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USERNAME")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Initialize databases
    init_sqlite_db()
    global NEOCONN

    # Initialize Neo4j connection
    NEOCONN = Neo4jConnection(uri=URI, user=USER, password=PASSWORD)


if __name__ == "__main__":
    main()
