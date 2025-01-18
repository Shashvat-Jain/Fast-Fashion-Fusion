from typing import Dict, List, Optional
import pandas as pd
import json
from neo4j import GraphDatabase
import ast
from tqdm import tqdm
import logging
from transformers import pipeline
import os
from dotenv import load_dotenv 
from tqdm import tqdm
load_dotenv() 

class FashionOntologySystem:
    def __init__(self, uri: str, user: str, password: str):
        """Initialize the Fashion Ontology System with Neo4j credentials."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('fashion_ontology.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_ontology_schema(self):
        """Create the basic ontology schema in Neo4j."""
        with self.driver.session() as session:
            # Create constraints and indices
            constraints = [
                # "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE",
                # "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
                # "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE",
                # "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE",
                # "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Feature) REQUIRE f.name IS UNIQUE",
                # "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Retailer) REQUIRE r.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                session.run(constraint)

    def process_feature_list(self, feature_list: str) -> List[str]:
        """Process the feature list string into a list of features."""
        try:
            if isinstance(feature_list, str):
                features = ast.literal_eval(feature_list)
                return [f.strip() for f in features if f.strip()]
            return []
        except:
            return []

    def process_style_attributes(self, style_attrs: str) -> Dict:
        """Process the style attributes string into a dictionary."""
        try:
            if isinstance(style_attrs, str):
                return json.loads(style_attrs)
            return {}
        except:
            return {}

    def extract_features_from_text(self, text: str) -> List[str]:
        """Extract features from text using NLP."""
        # Initialize the zero-shot classification pipeline
        # classifier = pipeline("zero-shot-classification",
        #                     model="facebook/bart-large-mnli")
        
        # # Define feature categories to look for
        # categories = [
        #     "color", "material", "pattern", "style", "fit",
        #     "occasion", "season", "size", "brand", "price_range"
        # ]
        
        # # Classify the text
        # result = classifier(text, categories, multi_label=True)
        
        # Extract relevant features based on confidence threshold
        features = []
        # for label, score in zip(result['labels'], result['scores']):
        #     if score > 0.5:  # Confidence threshold
        #         features.append(f"{label}: {text}")
        
        return features

    def load_data(self, file_path: str, batch_size: int = 1000):
        """Load data from CSV file into Neo4j."""
        self.logger.info(f"Loading data from {file_path}")
        
        # Read CSV in chunks
        for chunk in pd.read_csv(file_path, chunksize=batch_size):
            # use tqdm to show progress bar
            with self.driver.session() as session:
                for _, row in tqdm(chunk.iterrows(), total=len(chunk)):
                # for _, row in chunk.iterrows():
                    try:
                        # Process features and attributes
                        features = self.process_feature_list(row['feature_list'])
                        style_attrs = self.process_style_attributes(row['style_attributes'])
                        
                        # Extract additional features from description
                        text_features = self.extract_features_from_text(row['description'])
                        all_features = features + text_features
                        
                        # Create Cypher query
                        query = """
                        MERGE (p:Product {product_id: $product_id})
                        SET p.name = $product_name,
                            p.description = $description,
                            p.mrp = $mrp
                        
                        MERGE (c:Category {name: $category_name})
                        MERGE (p)-[:BELONGS_TO]->(c)
                        
                        MERGE (d:Department {name: $department_id})
                        MERGE (p)-[:IN_DEPARTMENT]->(d)
                        
                        MERGE (b:Brand {name: $brand})
                        MERGE (p)-[:MADE_BY]->(b)
                        
                        MERGE (r:Retailer {name: $retailer})
                        MERGE (p)-[:SOLD_BY]->(r)
                        
                        WITH p
                        UNWIND $features as feature
                        MERGE (f:Feature {name: feature})
                        MERGE (p)-[:HAS_FEATURE]->(f)
                        
                        WITH p
                        UNWIND $style_attrs as attr
                        MERGE (sa:StyleAttribute {name: attr.key, value: attr.value})
                        MERGE (p)-[:HAS_STYLE]->(sa)
                        """
                        
                        # Convert style_attrs dict to list of key-value pairs
                        style_attrs_list = [
                            {"key": k, "value": v} for k, v in style_attrs.items()
                        ]
                        
                        # Execute query
                        session.run(
                            query,
                            product_id=row['product_id'],
                            product_name=row['product_name'],
                            description=row['description'],
                            mrp=float(row['mrp']) if pd.notna(row['mrp']) else 0.0,
                            category_name=row['category_name'],
                            department_id=str(row['department_id']),
                            brand=row['brand'],
                            retailer=row['Retailer_name'],
                            features=all_features,
                            style_attrs=style_attrs_list
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Error processing row: {row['product_id']}")
                        self.logger.error(str(e))

    def close(self):
        """Close the Neo4j connection."""
        self.driver.close()

def main():
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USERNAME")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    DIR = os.path.dirname(os.path.abspath(__file__))
    DATADIR = os.path.join(DIR, "..", "data")
    # Initialize system
    system = FashionOntologySystem(URI, USER, PASSWORD)
    
    try:
        # Create schema
        system.create_ontology_schema()

        DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Process each CSV file
        csv_files = [
            "Dresses Data Dump.csv",
            "Bathroom Vanities Data Dump.csv",
            "Earrings Data Dump.csv",
            "Kurtis Data Dump Kurtis.csv",
            "Jeans Data Dump.csv",
            "Saree Data Dump.csv",
            "Shirts data_dump.csv",
            "Sneakers Data Dump.csv",
            "Tshirts Data Dump.csv",
            "Watches Data Dump.csv"
        ]
        
        for csv_file in csv_files:
            system.load_data(os.path.join(DATADIR, csv_file))
            
    finally:
        system.close()

if __name__ == "__main__":
    main()