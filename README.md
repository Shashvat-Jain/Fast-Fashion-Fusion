# Fashion Ontology and Trend Analysis Platform

## Overview

Our solution is a cutting-edge AI-powered platform designed to revolutionize the fashion industry. By combining advanced machine learning models with a scalable graph database, we automate feature extraction, ontology creation, and trend analysis for fashion products. Our system ensures adaptability to emerging trends, providing unparalleled insights into the ever-changing fashion landscape.

### Key Features:

- **AI-Driven Models** for feature extraction from text and images.
- **Dynamic Ontology Framework** that evolves with incoming data.
- **Scalable Neo4j AuraDB** for efficient data storage and querying.
- **Interactive User Interface** for stakeholders and fashion experts.
- **Social Media Trend Analysis Engine** for identifying emerging styles.

---

## User Interface

### 1. **Query Page**:

- Filter and retrieve specific products based on ontology attributes.
- Display relationships between selected products and other entities.

### 2. **Trend Analysis Page**:

- Highlights trending products, styles, and categories.
- Tracks emerging trends based on patterns across social media.

### 3. **Verification Page**:

- Human-in-the-loop validation to ensure ontology accuracy.
- Verified updates are automatically uploaded to Neo4j.

### 4. **Ontology Page**:

- Visualize hierarchical structures of fashion entities.
- Explore relationships and connections in an interactive panel.

### 5. **Social Trends Page**:

- Monitors top celebrity posts on platforms like Instagram.
- Extracts features and updates the ontology for statistical assessment.

### 6. **Data Extractor**:

- For manually extracting fashion attribute and generating ontology.
- Provide image with or without some context and generate features.

---

## Directories Explanation

### In this Repo:

- **models**: Includes scripts for model training, data processing, and initial ontology generation (training conducted on Kaggle).
- **neo4j**: Contains scripts for building the graph database on Neo4j AuraDB and creating the ontology.
- **web-scrapper-engine**: Contains scripts related to web scraping.
- **backend**: Contains scripts for running the backend, including models for feature extraction and ontology generation.
- **frontend**: Hosts the UI for fashion experts to interact with the ontology.

### Online scripts:

- **Data Prepration for Model Fine Tunningtps** : [Kaggle Notebook](https://www.kaggle.com/code/vivecode/stylumia-ontology-generation-script)
- **Model Training**: [Kaggle Notebook](https://www.kaggle.com/code/vivecode/stylumia-model-training)
- **Data Prepration for Model Fine Tunning** : [Jupyter Notebook](https://github.com/ImJericho/stylumia-nxt/blob/main/text_model/data_processing.ipynb)

### Hosted Model and Data:

- **Fine Tunned Model** : [HuggingFace] https://huggingface.co/datasets/ImJericho/Stylumia-nxt-text2text
- **Processed Dataset** : [HuggingFace] https://huggingface.co/ImJericho/model-t2t-stylumia-8bit


---
## Data Storage(Neo4j AuraDB)

- **Two Databases**:
  - **Ontology Database**: Stores hierarchical structures and relationships.
  - **Product Database**: Contains product data with 80k+ data points.
- **Optimizations**:
  - Graph-based structure for fast retrieval.
  - Interactive visualization tools integrated with Neo4j.

![hippo](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWl1dDEyeHRuZGZhMmh5cml6aHUzb2E0cnk0M2todHc0bzJmbnIxayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/7s7Vf07bdL1eQQ1vUQ/giphy.gif)

---

## Trend Analysis Engine

### Workflow:

1. Monitor top 100 celebrities' latest posts on social media (Instagram).
2. Extract product features using AI models.
3. Submit extracted features to verification.
4. Verified features are added to the ontology.
5. Analyze trends by detecting repeated patterns.

### Example:

- If multiple celebrities wear distressed jeans, the engine identifies it as a trend.
- Public interest analysis confirms its relevance in fast fashion.

---


## Take a look for yourself [here](https://stylumia-fashion.streamlit.app/)

---

## Technologies Used

- **Unsloth**: For fine-tunning the open-source models effentiantly in free tier notebooks.
- **Ollama**: For using the model in python and usage of transformers lib at the time of fine-tunning
- **Ngrok**: For connecting the hosted ollama.
- **Kaggle**: Used kaggle notebooks for all the above mentioned training.
- **HuggingFace**: To store the dataset and hosting the fine-tuned model.
- **Neo4j**: Graph database for ontology storage and retrieval.
- **Streamlit**: Intuitive frontend for user interactions.
- **PyVis**: Visualization of relationships and hierarchies.
- **Python**: Core programming language for backend and model pipelines.

---

## How to Run the Solution Locally

### Prerequisites:

1. Python 3.9 or higher.
2. Required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup Instaloader module
   ```bash
   instaloader --login=instagram_username
   ```
   Once you enter the password, Instaloader will create an Instagram session for your ID and the script will run.
4. Install our feature extraction models:
   ```bash
   ollama pull hf.co/ImJericho/model-t2t-stylumia-8bit
   ollama pull llama3.2
   ollama oull llava:13b / llama3.2-vision
   ```
5. Install internal folders as modules
   ```bash
   pip install -e .
   ```

### Steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/ImJericho/stylumia-nxt
   ```
2. Set env variables `.env`:
   ```env
   NEO4J_URI=bolt://<your-neo4j-uri>
   NEO4J_USER=<your-username>
   NEO4J_PASSWORD=<your-password>
   ONT_NEO4J_URI=bolt://<your-neo4j-ontology-uri>
   ONT_NEO4J_USER=<your-username> # for ontology database
   ONT_NEO4J_PASSWORD=<your-password> # for ontology database
   OLLAMA_URL=<your-ollama-url> // where all the fine-tunned model will be hosted
   HUGGINGFACE_TOKEN=<your-hf-token>
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run .\frontend\Fashion.py
   ```
4. Access the application at `http://localhost:8501`.

---

## Team

- **Shashvat Jain** (IIT Dhanbad)
- **Vivek Patidar** (IIT Dhanbad)
- **Pranay Pandey** (IIT Dhanbad)

---