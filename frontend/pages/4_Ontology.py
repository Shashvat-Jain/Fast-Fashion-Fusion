import streamlit as st
from pyvis.network import Network
import os
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


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]


# Update the Neo4j Query Page section with this code
def get_node_types(neo4j_conn):
    """Get all unique node types from the database"""
    query = """
    CALL db.labels() YIELD label
    RETURN collect(label) as labels
    """
    result = neo4j_conn.query(query)
    return result[0]["labels"]


def get_relationship_types(neo4j_conn):
    """Get all unique relationship types from the database"""
    query = """
    CALL db.relationshipTypes() YIELD relationshipType
    RETURN collect(relationshipType) as types
    """
    result = neo4j_conn.query(query)
    return result[0]["types"]


def neo4j_query_page(neo4j_conn):
    st.title("Database Explorer")

    # Sidebar filters
    st.sidebar.header("Filters")

    if neo4j_conn is None:
        st.sidebar.error(
            "Neo4j connection is not available. Please check the connection details and try again."
        )
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
            results = neo4j_conn.query(
                query,
                {"node_types": selected_node_types, "rel_types": selected_rel_types},
            )

            # Create network graph
            G = nx.Graph()

            # Add nodes and edges from results
            for record in results:
                if record["n"]:
                    node1_id = str(record["n"].element_id)
                    node1_labels = list(record["n"].labels)
                    node1_props = dict(record["n"].items())
                    G.add_node(node1_id, labels=node1_labels, **node1_props)

                if record["m"]:
                    node2_id = str(record["m"].id)
                    node2_labels = list(record["m"].labels)
                    node2_props = dict(record["m"].items())
                    G.add_node(node2_id, labels=node2_labels, **node2_props)

                if record["r"] and record["n"] and record["m"]:
                    G.add_edge(
                        str(record["n"].id),
                        str(record["m"].id),
                        type=type(record["r"]).__name__,
                        **dict(record["r"].items()),
                    )

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
                edge_text.append(edge[2]["type"])

            edges_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=0.5, color="#888"),
                hoverinfo="text",
                text=edge_text,
                mode="lines",
            )

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
                    if key != "labels":
                        hover_text += f"{key}: {value}<br>"
                node_text.append(hover_text)

                # Assign different colors based on node labels
                color_idx = hash(str(node[1]["labels"])) % 20  # 20 different colors
                node_color.append(color_idx)

            nodes_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                hoverinfo="text",
                text=node_text,
                marker=dict(
                    showscale=True,
                    colorscale="Rainbow",
                    color=node_color,
                    size=15,
                    line_width=2,
                ),
            )

            # Create the figure
            fig = go.Figure(
                data=[edges_trace, nodes_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(b=0, l=0, r=0, t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Add option to show data in tabular format
            if st.checkbox("Show Data Table"):
                # Convert graph data to DataFrame
                data = []
                for node, attrs in G.nodes(data=True):
                    row = {"Node ID": node}
                    row.update(attrs)
                    data.append(row)

                df = pd.DataFrame(data)
                st.dataframe(df)

        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    else:
        st.info(
            "Select node types and relationship types from the sidebar to explore the data"
        )

# read the ontology data from a JSON file
data = json.load(open("frontend/ontology.json"))

# Define node types and colors
NODE_TYPES = {
    "superclass": "lightblue",
    "class": "lightgreen",
    "type": "lightpink",
    "variant": "lightyellow",
    "style": "lightgray",
}

SEQUENCE = ["superclass", "class", "type", "variant", "style"]


def add_nodes_and_edges(net, parent, node, node_type_ind=0):
    node_type = SEQUENCE[node_type_ind]
    if isinstance(node, dict):
        for key, value in node.items():
            if key not in ["variants", "styles"]:  # Skip leaf lists
                net.add_node(key, label=key, color=NODE_TYPES.get(node_type, "white"))
                net.add_edge(parent, key)
                add_nodes_and_edges(net, key, value, node_type_ind=node_type_ind + 1)
    elif isinstance(node, list):
        for item in node:
            net.add_node(item, label=item, color=NODE_TYPES.get(node_type, "white"))
            net.add_edge(parent, item)


def get_dropdown_options(data, selected_path):
    """Traverse the data to get dropdown options based on the current selection path."""
    node = data
    for key in selected_path:
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return []
    if isinstance(node, dict):
        if "variants" in node and "styles" in node:
            return {"variants": node["variants"], "styles": node["styles"]}
        return list(node.keys())
    elif isinstance(node, list):
        return node
    return []


# Streamlit App
st.title("Interactive Ontology Visualization")

# Add Legend
st.subheader("Legend")
legend_html = """
<div style="display: flex; flex-direction: row;">
    <div style="margin: 5px;">
        <span style="background-color: lightblue; padding: 5px; margin-right: 5px; border-radius: 3px;">&nbsp;</span>
        Superclass
    </div>
    <div style="margin: 5px;">
        <span style="background-color: lightgreen; padding: 5px; margin-right: 5px; border-radius: 3px;">&nbsp;</span>
        Class
    </div>
    <div style="margin: 5px;">
        <span style="background-color: lightpink; padding: 5px; margin-right: 5px; border-radius: 3px;">&nbsp;</span>
        Type
    </div>
</div>
"""
st.markdown(legend_html, unsafe_allow_html=True)

# Create a PyVis network
net = Network(height="750px", width="100%", directed=True)

# Add top-level superclasses
for superclass in data["superclasses"]:
    net.add_node(superclass, label=superclass, color=NODE_TYPES["superclass"])
    add_nodes_and_edges(net, superclass, data.get(superclass, {}))

# Render PyVis Graph
html_content = net.generate_html()
st.components.v1.html(html_content, height=800, scrolling=True)

# Check a Specific Ontology Subtree Section
st.subheader("Check a Specific Ontology Subtree")

selected_path = []

# Superclass Dropdown
superclass_options = data["superclasses"]
selected_superclass = st.selectbox(
    "Select a Superclass", superclass_options, key="superclass"
)
if selected_superclass:
    selected_path.append(selected_superclass)
    class_options = get_dropdown_options(data, selected_path)

    # Class Dropdown
    selected_class = st.selectbox("Select a Class", class_options, key="class")
    if selected_class:
        selected_path.append(selected_class)
        type_options = get_dropdown_options(data, selected_path)

        # Type Dropdown
        selected_type = st.selectbox("Select a Type", type_options, key="type")
        if selected_type:
            selected_path.append(selected_type)
            final_data = get_dropdown_options(data, selected_path)

            if isinstance(final_data, dict):
                st.write("### Variants")
                st.write(final_data.get("variants", []))
                st.write("### Styles")
                st.write(final_data.get("styles", []))

URI = os.getenv("ONT_NEO4J_URI")
USER = os.getenv("ONT_NEO4J_USERNAME")
PASSWORD = os.getenv("ONT_NEO4J_PASSWORD")
NEOCONN = Neo4jConnection(uri=URI, user=USER, password=PASSWORD)
# Connect to Neo4j
neo4j_query_page(NEOCONN)
