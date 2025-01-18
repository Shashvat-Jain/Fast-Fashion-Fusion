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
from config import NEOCONN, init_sqlite_db, main as main_config

main_config()

# Update the Neo4j Query Page section with this code
def get_node_types(neo4j_conn):
    """Get all unique node types from the database"""
    query = """
    CALL db.labels() YIELD label
    RETURN collect(label) as labels
    """
    result = neo4j_conn.query(query)
    return result[0]['labels']

def get_relationship_types(neo4j_conn):
    """Get all unique relationship types from the database"""
    query = """
    CALL db.relationshipTypes() YIELD relationshipType
    RETURN collect(relationshipType) as types
    """
    result = neo4j_conn.query(query)
    return result[0]['types']

def neo4j_query_page(neo4j_conn):
    st.title("Database Explorer")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    while neo4j_conn is None:
        st.sidebar.error("Neo4j connection is not available. Please check the connection details and try again.")
        return
    # Node Types section

    node_types = get_node_types(neo4j_conn)
    selected_node_types = []
    
    # Create multiselect with "x" button styling
    col1, col2 = st.sidebar.columns([3, 3])
    with col1:
        col1.header("Node Types")
        for node_type in node_types:
            if st.checkbox(node_type, key=f"node_{node_type}"):
                selected_node_types.append(node_type)

    # Relationship Types section
    rel_types = get_relationship_types(neo4j_conn)
    selected_rel_types = []
    
    with col2:
        col2.header("Relationship Types")
        for rel_type in rel_types:
            if st.checkbox(rel_type, key=f"rel_{rel_type}"):
                selected_rel_types.append(rel_type)

    # Main content area
    if selected_node_types or selected_rel_types:
        # Construct query based on selections
        query = """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN $node_types)
        """
        
        if selected_rel_types:
            query += """
            OPTIONAL MATCH (n)-[r]->(m)
            WHERE type(r) IN $rel_types
            """
        else:
            query += """
            OPTIONAL MATCH (n)-[r]->(m)
            """
            
        query += "RETURN n, r, m"
        
        try:
            results = neo4j_conn.query(query, {
                'node_types': selected_node_types,
                'rel_types': selected_rel_types
            })
            
            # Create network graph
            G = nx.Graph()
            
            # Add nodes and edges from results
            for record in results:
                if record['n']:
                    node1_id = str(record['n'].element_id)
                    node1_labels = list(record['n'].labels)
                    node1_props = dict(record['n'].items())
                    G.add_node(node1_id, 
                             labels=node1_labels,
                             **node1_props)
                
                if record['m']:
                    node2_id = str(record['m'].id)
                    node2_labels = list(record['m'].labels)
                    node2_props = dict(record['m'].items())
                    G.add_node(node2_id,
                             labels=node2_labels,
                             **node2_props)
                
                if record['r'] and record['n'] and record['m']:
                    G.add_edge(str(record['n'].id),
                             str(record['m'].id),
                             type=type(record['r']).__name__,
                             **dict(record['r'].items()))

            # Create interactive visualization using Plotly
            pos = nx.spring_layout(G)
            
            # Create edges trace
            edge_x = []
            edge_y = []
            edge_text = []
            
            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_text.append(edge[2]['type'])

            edges_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='text',
                text=edge_text,
                mode='lines')

            # Create nodes trace
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            
            for node in G.nodes(data=True):
                x, y = pos[node[0]]
                node_x.append(x)
                node_y.append(y)
                
                # Create hover text with all node properties
                hover_text = f"Labels: {', '.join(node[1]['labels'])}<br>"
                for key, value in node[1].items():
                    if key != 'labels':
                        hover_text += f"{key}: {value}<br>"
                node_text.append(hover_text)
                
                # Assign different colors based on node labels
                color_idx = hash(str(node[1]['labels'])) % 20  # 20 different colors
                node_color.append(color_idx)

            nodes_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='Rainbow',
                    color=node_color,
                    size=15,
                    line_width=2))

            # Create the figure
            fig = go.Figure(data=[edges_trace, nodes_trace],
                          layout=go.Layout(
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=0, l=0, r=0, t=0),
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                          ))

            

            st.plotly_chart(fig, use_container_width=True)

            # Add option to show data in tabular format
            if st.checkbox("Show Data Table"):
                # Convert graph data to DataFrame
                data = []
                for node, attrs in G.nodes(data=True):
                    row = {'Node ID': node}
                    row.update(attrs)
                    data.append(row)
                
                df = pd.DataFrame(data)
                st.dataframe(df)

        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    else:
        st.info("Select node types and relationship types from the sidebar to explore the data")

def main():
    st.set_page_config(page_title="Fashion Analytics", layout="wide")
    # Connect to Neo4j
    neo4j_query_page(NEOCONN)

if __name__ == "__main__":
    main()