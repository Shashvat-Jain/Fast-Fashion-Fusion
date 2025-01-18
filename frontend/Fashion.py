import streamlit as st
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Fashion Ontology Platform",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hero Section
st.markdown(
    """
    <style>
    .hero {
        text-align: center;
        background-color: #f7f7f7;
        padding: 40px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .hero h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
        color: #333;
    }
    .hero p {
        font-size: 1.2rem;
        color: #666;
    }
    .feature-box {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .feature-box h3 {
        margin: 0;
        font-size: 1.3rem;
        color: #444;
    }
    </style>
    <div class="hero">
        <h1>Welcome to the Fashion Ontology Platform</h1>
        <p>An AI-powered platform for universal feature extraction and intelligent fashion analysis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Section: Key Features
st.markdown("## 🚀 Key Features")

features = [
    "**Ontology Page**: Visualize the hierarchical structure of fashion entities and their relationships.",
    "**Query Page**: Explore the database and retrieve products based on specific filters and relationships.",
    "**Trend Analysis Page**: Upload CSV data, extract features using AI models, and update the database.",
    "**Verification Page**: Ensure only verified entities and features are added to the database.",
    "**Social Trends**: Analyze top social media accounts to identify and ingest trending products into the ontology."
]

for feature in features:
    st.markdown(f"- {feature}")

# Section: Workflows Overview
st.markdown("## 📋 Workflows Overview")
st.markdown(
    """
    This platform provides seamless integration between different components to streamline the process of fashion ontology creation and analysis. Here are the workflows:
    """
)

workflows = [
    {
        "title": "Data Ingestion Workflow",
        "description": "Upload product data via CSV. Extract features using AI models, including image-to-text generation, and update the database.",
        "icon": "📂",
    },
    {
        "title": "Ontology Visualization Workflow",
        "description": "Explore the hierarchical structure of the ontology, including superclasses, classes, types, styles, and variants.",
        "icon": "🌐",
    },
    {
        "title": "Query Workflow",
        "description": "Filter and retrieve specific products and their relationships using an intuitive query interface.",
        "icon": "🔍",
    },
    {
        "title": "Verification Workflow",
        "description": "Verify new features and entities added to the database. Only verified data is stored permanently.",
        "icon": "✅",
    },
    {
        "title": "Trend Analysis Workflow",
        "description": "Identify trending fashion products on social media. Extract and ingest new features into the database.",
        "icon": "📊",
    },
    {
        "title": "Data Extractor",
        "description": "Enrich the database with additional features and relationships using advanced AI models and continuous learning.",
        "icon": "📈",
    }
]

for workflow in workflows:
    st.markdown(
        f"""
        <div class="feature-box">
            <h3>{workflow['icon']} {workflow['title']}</h3>
            <p>{workflow['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Section: Visual Overview
st.markdown("## 🎨 Visual Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Ontology Visualization")
    image = Image.open("ontology_visualization.png")  # Replace with actual path
    st.image(image, caption="Interactive Ontology View")

with col2:
    st.markdown("### Query Interface")
    image = Image.open("query_interface.png")  # Replace with actual path
    st.image(image, caption="Product Query and Relationships")

# Section: About
st.markdown("## ℹ️ About")
st.write(
    "This platform leverages advanced AI and graph database technologies to revolutionize the way fashion data is analyzed and structured. With multi-level ontologies and continuous learning mechanisms, it provides unparalleled insights into the fashion industry."
)

st.markdown(
    """
    ### Technologies Used
    - **Neo4j**: Graph database for efficient ontology storage and querying.
    - **Streamlit**: Interactive frontend for seamless user experience.
    - **LLMs**: For feature extraction, trend analysis, and data enrichment.
    - **PyVis**: Visualizing relationships and hierarchies interactively.
    """
)
