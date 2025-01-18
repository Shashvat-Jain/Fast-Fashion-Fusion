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
import json

def getShortField(field):
    replacements = {
        " ": "_",
        "-": "_",
        "(": "",
        ")": "",
        "/": "_",
        ".": "",
        ",": "",
        "&": "and",
        ".": "",
        "?": "",
        "!": "",
        "'": "",
        '"': "",
        ":": "",
    }
    for key, value in replacements.items():
        field = field.replace(key, value)
    return field

class FashionOntologySystem:
    def __init__(self, uri: str, user: str, password: str):
        """Initialize the Fashion Ontology System with Neo4j credentials."""
        self.driver =  GraphDatabase.driver(uri, auth=(user, password))
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

    def load_data(self, objects: list[dict], batch_size: int = 1000):
        """Load data from Json Object into Neo4j."""
        self.logger.info(f"Loading data")

        with self.driver.session() as session:
            for obj in tqdm(objects):
                try:
                    # Create Cypher query
                    query = """
                    MERGE (p:Product {product_id: $product_id})
                    SET p.name = $product_name

                    MERGE (sc:Superclass {name: $superclass})
                    MERGE (p)-[:BELONGS_TO]->(sc)

                    MERGE (c:Class {name: $className})
                    MERGE (p)-[:BELONGS_TO]->(c)

                    MERGE (ty:Type {name: $type})
                    MERGE (p)-[:TYPE_OF]->(ty)

                    MERGE (var:Variant {name: $variant})
                    MERGE (p)-[:VARIANT_OF]->(var)

                    MERGE (st:Style {name: $style})
                    MERGE (p)-[:STYLE_OF]->(st)
                    """

                    # Add other relations if they exist
                    for key, value in obj.items():
                        if key not in ['product_id', 'product_name', 'superclass', 'class', 'type', 'variant', 'style']:
                            fieldKey = getShortField(key)
                            relationKey = "HAS_" + fieldKey.upper()
                            query += f"""
                            MERGE (a"""+fieldKey+":"+fieldKey +"{name: $"+fieldKey+"""}) 
                            MERGE (p)-[:"""+relationKey+"]->(a"+fieldKey+""")
                            """
                            )

                    # Execute query
                    session.run(
                        query,
                        product_id=obj['product_id'],
                        product_name=obj['product_name'],
                        superclass=obj['superclass'],
                        className=obj['class'],
                        type=obj['type'],
                        variant=obj['variant'],
                        style=obj['style'],
                        **{getShortField(key): obj[key] for key in obj if key not in ['product_id', 'product_name', 'superclass', 'class', 'type', 'variant', 'style']}
                    )

                except Exception as e:
                    self.logger.error(f"Error processing row: {obj['product_name']}")
                    self.logger.error(str(e))
    def close(self):
        """Close the Neo4j connection."""
        self.driver.close()

def main():
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USERNAME")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    DIR = os.path.dirname(os.path.abspath(__file__))
    DATADIR = os.path.join(DIR, "..", "ontology_creation", "dataset", "processed_json")
    # Initialize system
    system = FashionOntologySystem(URI, USER, PASSWORD)
    
    try:

        for filename in os.listdir(DATADIR):
            if filename.endswith(".json"):
                with open(os.path.join(DATADIR, filename), "r") as f:
                    objects = json.load(f)

                    print(f"Loading {filename}")

                    system.load_data(objects)
            
    finally:
        system.close()

if __name__ == "__main__":
    main()

