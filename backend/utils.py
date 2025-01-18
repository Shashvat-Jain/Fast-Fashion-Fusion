import base64
from PIL import Image
import io
import requests
import sqlite3
import re
import json
import pandas as pd
import logging
# logging.basicConfig(level=logging.ERROR)


def create_db_file(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE {table_name} 
             (entity_id INTEGER PRIMARY KEY AUTOINCREMENT, image_url TEXT, image_caption TEXT, image_description TEXT, style_attributes TEXT, superclass TEXT, class TEXT, type TEXT, variant TEXT, style TEXT)''')
    conn.commit()
    conn.close()

def read_db_file(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return rows

def read_csv_file(csv_path):
    df = pd.read_csv(csv_path)
    return df

#insert rows into the database
def insert_into_db(db_path, table_name, image_url, image_caption):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} (image_url, image_caption) VALUES (?, ?)", (image_url, image_caption))
    conn.commit()
    conn.close()

def update_db_file_description(db_path, table_name, entity_id, image_description):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET image_description = ? WHERE entity_id = ?", (image_description, entity_id))
    conn.commit()
    conn.close()

def update_db_file_attributes(db_path, table_name, entity_id, style_attributes):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET style_attributes = ? WHERE entity_id = ?", (style_attributes, entity_id))
    conn.commit()
    conn.close()

def update_db_file_ontology(db_path, table_name, entity_id, ontology):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET superclass = ?, class = ?, type = ?, variant = ?, style = ? WHERE entity_id = ?", 
                   (ontology['superclass'], ontology['class'], ontology['type'], ontology['variant'], ontology['style'], entity_id))
    conn.commit()
    conn.close()

def get_image_from_url(image_url):
    response = requests.get(image_url, stream=True)
    image = Image.open(response.raw)
    return image

def encode_image_to_base64(image_url):
    image = get_image_from_url(image_url)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

#show image back from base64
def decode_image_from_base64(encoded_image):
    image = base64.b64decode(encoded_image)
    image = Image.open(io.BytesIO(image))
    #show this image in the new window
    image.show()
    return image

def get_output_text_v2(response):
    try:
        response_dict = response.json()
        response = response_dict['response']
        response = response.replace("\n", "")
        # response = response.replace("'", '"')
        start = response.find('{')
        end = response.rfind('}')
        # Extract and print the content
        if start != -1 and end != -1:
            extracted = response[start:end+1]
            # try:
            #     json_obj = json.loads(extracted)
            # except:
            #     pass
            return extracted
        if start !=-1:
            return response[start:]
        return response
    except:
        logging.error("Failed to parse JSON response", exc_info=True)
        return f"{response}"

def get_output_text(response):
    output_text = ""
    for line in response.text.splitlines():
        try:
            data = json.loads(line)
            if 'message' in data and 'content' in data['message']:
                output_text += data['message']['content']
        except:
            pass
        output_text = output_text.replace("*", "")
    return output_text


def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def get_json_from_response(response):
    #replace ' with "
    response = response.replace("'", '"')
    start = response.find('{')
    end = response.rfind('}')
    # Extract and print the content
    if start != -1 and end != -1:
        extracted = response[start:end+1]
        try:
            json_obj = json.loads(extracted)
            return json_obj
        except:
            pass

    match = re.search(r'\{[\s\S]*\}', response)
    if not match:
        return None
    match = match.group()
    return match

def get_list_from_response(response):
    response = response.replace("'", '"')
    start = response.find('[')
    end = response.rfind(']')
    # Extract and print the content
    if start != -1 and end != -1:
        extracted = response[start:end+1]
        try:
            json_obj = json.loads(extracted)
            return json_obj
        except:
            pass

    match = re.search(r'\[[\s\S]*\]', response)
    if not match:
        return None
    match = match.group()
    return match
    

def create_ontology_lists(data):
    superclasses = []
    subclasses = []
    subsubclasses = []  
    categories = []
    products = []
    for superclass in data.get("superclass", []):
        print(f"Superclass: {superclass['name']}")
        superclasses.append(superclass['name'])
        for subclass in superclass.get("subclass", []):
            print(f"  Subclass: {subclass['name']}")
            subclasses.append(subclass['name'])
            for subsubclass in subclass.get("subsubclass", []):
                print(f"    Subsubclass: {subsubclass['name']}")
                subsubclasses.append(subsubclass['name'])
                for category in subsubclass.get("category", []):
                    print(f"      Category: {category['name']}")
                    categories.append(category['name'])
                    for product in category.get("product", []):
                        print(f"        Product: {product['name']}")
                        products.append(product['name'])

    ontology = {
        "superclasses": superclasses,
        "subclasses": subclasses,
        "subsubclasses": subsubclasses,
        "categories": categories
    }
    # return superclasses, subclasses, subsubclasses, categories
    return ontology


def get_ontology_dict(path):
    ontology = read_json(path)
    result = {
        "superclasses": ontology["superclasses"],
    }
    
    for superclass in ontology["superclasses"]:
        result[superclass] = {}
        result[superclass]["classes"] = ontology[superclass]["classes"]
        
        for cls in ontology[superclass]["classes"]:
            result[superclass][cls] = {}
            result[superclass][cls]["types"] = ontology[superclass][cls]["types"]
            
            for type_ in ontology[superclass][cls]["types"]:
                result[superclass][cls][type_] = {}
                result[superclass][cls][type_]["variants"] = ontology[superclass][cls][type_]["variants"]
                result[superclass][cls][type_]["styles"] = ontology[superclass][cls][type_]["styles"]
    
    return result

def get_class_defination(class_name):

    json_obj = {
        "superclass": "The broadest and most stable classification representing the general type of product. This category is fixed and does not change frequently.",
        "class": "A functional or cultural subdivision within each superclass. It defines the primary purpose, context, or cultural relevance of the product. Examples include Traditional Wear, Casual Wear, Formal Wear, Athletic Wear, and Seasonal Wear.",
        "type": "A category that describes the general physical form or body area associated with the product. This is typically where or how the item is used or worn. Examples include Top-wear, Bottom-wear, Footwear, Headwear, Neckwear, and Handbags.",
        "variant": "A specific version or subtype of a product that varies by design, material, or cut. This level reflects distinct product variations that differ in aesthetic or functional aspects but fall under the same type. Examples include Skinny Jeans, Silk Saree, or High-top Sneakers.",
        "style": "Fine-grained descriptors that highlight aesthetic details, patterns, colors, or unique design elements. This level captures subtle features that influence consumer preference but do not change the core classification. Examples include Distressed Jeans, Embroidered Saree, or Minimalist Sneakers.",
    }
    return json_obj[class_name]


