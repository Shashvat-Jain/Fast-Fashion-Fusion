import requests
import json
# import classification_models as cls
from backend import classification_models as cls
# import utils
from backend import utils
import os
from dotenv import load_dotenv
import pandas as pd
import logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def img2txt2txt_engine(csv_path_in='backend/data/ingested_data.csv', db_path_out='backend/data/extracted_data.db', ontology_path='backend/data/ontology.json'):
    i2t_model_endpoint = os.getenv("OLLAMA_URL")
    t2t_model_endpoint = i2t_model_endpoint

    raw_data = pd.read_csv(csv_path_in)

    for idx, data in raw_data.iterrows():
        logging.info(f"Iteration: {idx}")
        image_url = data['post_image_urls']
        context = data['post_text']
        utils.insert_into_db(db_path_out, 'extracted_data', image_url, context)
    logging.info("Done inserting into db")


    raw_data = utils.read_db_file(db_path_out, 'extracted_data')
    for idx, data in enumerate(raw_data):
        logging.info(f"Iteration: {idx}")
        entity_id = data[0]
        image_url = data[1]
        context = data[2]
        image_description = image2text_model(image_url, i2t_model_endpoint, context)
        logging.info(f"Image Description: {image_description}")
        utils.update_db_file_description(db_path_out, 'extracted_data', entity_id, image_description)
    logging.info("Done for image2text_model")

    raw_data = utils.read_db_file(db_path_out, 'extracted_data')
    for idx, data in enumerate(raw_data):
        logging.info(f"Iteration: {idx}")
        entity_id = data[0]
        image_description = data[3]
        style_attributes = text2text_model(image_description, t2t_model_endpoint)
        # style_attributes = json.loads(style_attributes)
        logging.info(f"Style Attributes: {style_attributes} {type(style_attributes)}")
        utils.update_db_file_attributes(db_path_out, 'extracted_data', entity_id, style_attributes)
    logging.info("Done for text2text_model")

    raw_data = utils.read_db_file(db_path_out, 'extracted_data')
    for idx, data in enumerate(raw_data):
        logging.info(f"Iteration: {idx}")
        entity_id = data[0]
        image_text = data[2]
        image_description = data[3]
        ontology = text2ontology_model(image_description, t2t_model_endpoint, ontology_path)
        logging.info(f"Ontology: {ontology}")
        utils.update_db_file_ontology(db_path_out, 'extracted_data', entity_id, ontology)
    logging.info("Done for text2ontology_model")

    logging.info("ALL DONE")


def image2text_model(image_url, ollama_url, desci=None):
    prompt = """"Analyze the image provided, which contains an advertisement for a fashion product. "
    {description_caption}
    "Your task is to identify and describe only the main fashion item that is the focus of the advertisement. "
    "Ignore background elements, additional accessories, or other secondary items. "
    "Extract and describe the key style attributes of the identified product, such as color, material, pattern, fit, where to wear it, for which gender, what's the name of the product,"
    "and unique design details. If relevant, include how the advertisement’s presentation enhances the product's appeal. "
    "Do not describe unrelated elements in the image—focus solely on the main fashion product being advertised."
    """

    description_caption = ""
    if desci and desci!="" and desci!=" ":
        description_caption = f"Description: {desci}"
    
    prompt.format(description_caption=description_caption)
    encoded_image = utils.encode_image_to_base64(image_url)

    ollama_llama_url = f"{ollama_url}/api/chat"
    payload_llama = {
    "model": "llama3.2-vision",
    "messages": [
        {
        "role": "user",
        "content": prompt,
        "images": [encoded_image]
        }
    ]
    }

    response = requests.post(ollama_llama_url, data=json.dumps(payload_llama))
    logging.info(response.text)
    return utils.get_output_text(response)


def text2text_model(input_text, ollama_url):
    instruction = "I have a product. Extract key style attributes from the provided product description and return them in a JSON dictionary format. Ensure the attributes are concise, relevant to fashion (e.g., color, pattern, fit, material, size, place to wear, gender,). The response should strictly follow the JSON format enclosed in '\{\}', without any additional text."
    alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

    ### Instruction:
    {}

    ### Input:
    {}

    ### Response:
    {}"""
    eos_token = '<|end_of_text|>'
    text = alpaca_prompt.format(instruction, input_text, "") + eos_token

    ollama_llama_url = f"{ollama_url}/api/generate"
    payload_llama = {
        "model": "hf.co/ImJericho/model-t2t-stylumia-8bit",
        "max_tokens": 1000,
        "prompt": text,
        "stream": False
    }

    response = requests.post(ollama_llama_url, data=json.dumps(payload_llama))
    return utils.get_output_text_v2(response)


def text2ontology_model(input_text, ollama_url, ontology_path):
    ontology = json.load(open(ontology_path))

    prompt = input_text
    # try:
    if 1:
        debug = False
        a, superclass = cls.get_existing_class_from_text_using_ollama(prompt, ontology['superclasses'], utils.get_class_defination('superclass'), ollama_url, debug)
        if a:
            superclass = "Clothing"
        b, class_t = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass]['classes'], utils.get_class_defination('class'), ollama_url,debug, parent_classes=[superclass])
        if b:
            c, type_t = cls.get_new_class_from_text_using_ollama(prompt, utils.get_class_defination('type'), ollama_url, debug, parent_classes=[superclass, class_t])
            d, variant = cls.get_new_class_from_text_using_ollama(prompt, utils.get_class_defination('variant'), ollama_url, debug, parent_classes=[superclass, class_t, type_t])
            e, style = cls.get_new_class_from_text_using_ollama(prompt, utils.get_class_defination('style'), ollama_url, debug, parent_classes=[superclass, class_t, type_t])                    
        else:    
            c, type_t = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass][class_t]['types'], utils.get_class_defination('type'), ollama_url, debug, parent_classes=[superclass, class_t])
            if c:
                d, variant = cls.get_new_class_from_text_using_ollama(prompt, utils.get_class_defination('variant'), ollama_url, debug, parent_classes=[superclass, class_t, type_t])
                e, style = cls.get_new_class_from_text_using_ollama(prompt, utils.get_class_defination('style'), ollama_url, debug, parent_classes=[superclass, class_t, type_t])
            else:
                d, variant = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass][class_t][type_t]['variants'], utils.get_class_defination('variant'), ollama_url, debug, parent_classes=[superclass, class_t, type_t])
                e, style = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass][class_t][type_t]['styles'], utils.get_class_defination('style'), ollama_url, debug, parent_classes=[superclass, class_t, type_t])


    ontology_dict = {
        "superclass": superclass,
        "class": class_t,
        "type": type_t,
        "variant": variant,
        "style": style
    }

    return ontology_dict


def call_from_frontend(csv_path_in='backend/data/ingested_data.csv', db_path_out='backend/data/extracted_data.db', ontology_path='backend/data/ontology.json'):
    if os.path.exists(db_path_out):
        pass
    else:
        utils.create_db_file(db_path_out, 'extracted_data')
    img2txt2txt_engine(csv_path_in, db_path_out, ontology_path)

   

if __name__ == "__main__":
    db_path = 'backend/data/extracted_data.db'

    if os.path.exists(db_path):
        # utils.drop_db_file(db_path, 'extracted_data')
        pass
    else:
        utils.create_db_file(db_path, 'extracted_data')


    img2txt2txt_engine()
