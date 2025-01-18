import json
import re
from sentence_transformers import SentenceTransformer, util
from ollama import chat
from ollama import ChatResponse
import load_ontology as lo
import os
import pandas as pd



def llm_response(msg, model='phi3'):
    if model == 'llama3.2':
        model = 'llama3.2'
    else:
        model = 'phi3'

    model = 'llama3.2'

    response: ChatResponse = chat(model=model, messages=[
        {
        'role': 'system',
        'content': 'You are a fashion expert who can only respond in json with only 1 key - class.',
        },
        {
            'role': 'user',
            'content': msg,
        },
    ])
    return response.message.content


def get_class_from_text_using_llm_cos_sim(text, class_list):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    text_embedding = model.encode(text, convert_to_tensor=True)
    class_embeddings = model.encode(class_list, convert_to_tensor=True)
    similarities = util.cos_sim(text_embedding, class_embeddings)[0]
    
    # Create a dictionary of class: similarity
    similarity_dict = {cls: float(similarity) for cls, similarity in zip(class_list, similarities)}
    print(f"Similarity Dictionary: {similarity_dict}")
    
    return similarity_dict


def get_existing_class_from_text_using_ollama(datapoint, class_list, class_defination, debug=False, parent_classes=None):
    prompt = (
        "You are tasked with classifying a fashion product based on the following description: {description}. "
        "{parent_classes_prompt}"
        "Select the most appropriate class for this item from the list: {class_list}. This list represents classifications based on the class defination as: '{class_defination}'. "
        "Respond with a JSON object containing only one key 'class' and the value as the determined class (must be from the given list list)."
        "example response : {'class': 'class_name'}"
    )

    if parent_classes:
        parent_class_prompt = "The product is already a part of the following tags: {parent_classes}".format(parent_classes=parent_classes)
    else:
        parent_class_prompt = ""
    prompt = prompt.format(description=datapoint, class_list = class_list, parent_classes_prompt=parent_class_prompt, class_defination=class_defination)
    for i in range(5):
        response = llm_response(prompt)
        if debug:
            print(f"Attempt {i+1}, ({response})")
        try:
            json_obj = lo.get_json_from_response(response)
            break
        except:
            if debug:
                print("Error in get_json_from_response")
            continue
    
    if json_obj['class'] not in class_list:
        if debug:
            print(f"Invalid class: {json_obj['class']}")
        return True, json_obj['class']
    
    if debug:
        print(f"Valid class: {json_obj['class']}")
    return False, json_obj['class']


def get_new_class_from_text_using_ollama(datapoint, class_defination, debug=False, parent_classes=None):
    prompt = (
        "You are tasked with classifying a fashion product based on the following description: {description}. "
        "{parent_classes_prompt}"
        "Assign a new tag to this product based on: '{class_defination}'. "
        "Respond with a JSON object containing only one key 'class' and the value as the determined class."
        "example response : {'class': 'class_name'}"
    )
    if parent_classes:
        parent_class_prompt = "The product is already a part of the following tags: {parent_classes}".format(parent_classes=parent_classes)
    else:
        parent_class_prompt = ""
    prompt = prompt.format(description=datapoint, parent_classes_prompt=parent_class_prompt, class_defination=class_defination)

    for i in range(5):
        response = llm_response(prompt)
        if debug:
            print(f"Attempt {i+1}, ({response})")
        try:
            json_obj = lo.get_json_from_response(response)
            break
        except:
            if debug:
                print("Error in get_json_from_response")
            continue
    
    if debug:
        print(f"Valid class: {json_obj['class']}")
    return False, json_obj['class']



def get_new_or_existing_class_from_text_using_ollama(datapoint, class_list, class_defination, debug=False, parent_classes=None):
    prompt = (
        "You are tasked with classifying a fashion product based on the following description: {description}. "
        "{parent_classes_prompt}"
        "Select the most appropriate class for this item from the list: {class_list}. This list represents classifications based on the class defination as '{class_defination}'. "
        "If the item does not fit any of the existing classes, generate a new class that best describes it, but remember if you are creating a new class then make sure it follows the class defination and it is generic to fit few other products in it. "
        "Respond with a JSON object containing only the key 'class' and the value as the determined class (from the list, a newly generated class)."
    )
    if parent_classes:
        parent_class_prompt = "The product is already a part of the following tags: {parent_classes}".format(parent_classes=parent_classes)
    else:
        parent_class_prompt = ""

    prompt = prompt.format(description=datapoint, class_list=class_list, class_defination=class_defination, parent_classes_prompt=parent_class_prompt)
    

    for i in range(5):
        response = llm_response(prompt)
        if debug:
            print(f"Attempt {i+1}, ({response})")
        try:
            json_obj = lo.get_json_from_response(response)
            break
        except:
            if debug:
                print("Error in get_json_from_response")
            continue
    
    if json_obj['class'] not in class_list:
        if debug:
            print(f"Invalid class: {json_obj['class']}")
        return True, json_obj['class']
    
    if debug:
        print(f"Valid class: {json_obj['class']}")
    return False, json_obj['class']


def get_closest_class(llm_class, class_list, debug=False):
    """
    Finds the closest class from the provided class_list to the LLM-suggested class using SentenceTransformer.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode the LLM-suggested class and the available class list
    llm_embedding = model.encode(llm_class, convert_to_tensor=True)
    class_embeddings = model.encode(class_list, convert_to_tensor=True)

    # Compute cosine similarities
    similarities = util.cos_sim(llm_embedding, class_embeddings)[0]

    # Get the class with the highest similarity
    max_index = similarities.argmax().item()
    closest_class = class_list[max_index]
    
    if debug:
        print(f"LLM Class: {llm_class}")
        print(f"Closest Class: {closest_class}")
        print(f"Similarity Scores: {similarities.tolist()}")

    return closest_class

def get_class_from_text_using_ollama_with_approximation(datapoint, class_list, class_defination, debug=False):
    """
    Similar to get_class_from_text_using_ollama, but ensures that the returned class is always in the provided class list.
    """
    is_new_class, llm_class = get_class_from_text_using_ollama(datapoint, class_list, class_defination, debug=debug)

    if is_new_class:
        # Approximate the closest class from the list if the LLM-suggested class is not in the list
        closest_class = get_closest_class(llm_class, class_list, debug=debug)
        return False, closest_class

    return False, llm_class

def get_filtered_properties_from_attribute(attribute_dict, debug=False):

    prompt = (
        "I have a fashion item with the following attributes: {attribute_list}. "
        "Based on this attribute, filter out the properties that are most likely to be associated to understanding the fashion ontology. "
        "try to add atleast {num} properties including the name of product. "
        "Your response should be contain only a json list of strings nothing else."
    )

    attribute_list = list(attribute_dict.keys())
    print(attribute_list)

    prompt = prompt.format(attribute_list=attribute_list, num=len(attribute_list)//2)
    props = []
    for i in range(5):
        response = llm_response(prompt)
        if debug:
            print(f"Attempt {i+1}, ({response})")
        try:
            props = lo.get_list_from_response(response)
            break
        except:
            print("Error in get_list_from_response")
            continue
    
    properties = {}
    for prop in props:
        if prop in attribute_dict:
            if prop == 'sno':
                continue
            properties[prop] = attribute_dict[prop]

    return properties



def filter_style_attributes(path, final_path, min_num_attributes=4):
    for filename in os.listdir(path):
        df = pd.read_csv(f'{path}/' + filename)
        new_df = pd.DataFrame(columns=df.columns)
        skip = 0
        for index, row in df.iterrows():
            i = row['style_attributes']
            i = i.replace("'", '"').encode('utf-8').decode('unicode_escape')
            try: 
                json_obj = json.loads(i)
            except:
                skip += 1
                continue
            if len(json_obj) < min_num_attributes:
                skip += 1
                continue
            df.at[index, 'style_attributes'] = i
            new_df = pd.concat([new_df, df.iloc[[index]]], ignore_index=True)    
        new_df.to_csv(f'{final_path}/{filename}', index=False)
        print(f"Saved {filename} with {skip} skipped rows out of {len(df)}")
