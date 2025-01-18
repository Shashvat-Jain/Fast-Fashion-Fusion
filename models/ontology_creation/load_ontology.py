import json
import re

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
    json_obj = json.load(open('ontology_definations.json'))
    return json_obj[class_name]


def print_hierarchy(data, level=0):
    """
    Prints the JSON data in a hierarchical format with indentation.

    Args:
        data: The JSON data to print.
        level: The current indentation level.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            print("  " * level + f"- {key}:")
            print_hierarchy(value, level + 1)
    elif isinstance(data, list):
        for item in data:
            print("  " * level + f"- {item}")
    else:
        print("  " * level + f"- {data}")

def print_ontology(path):
    with open(path, "r") as f:
        data = json.load(f)
    print_hierarchy(data)




if __name__ == "__main__":
    # json_obj = read_json('ontology.json')
    # data = get_ontology_dict(json_obj)

    # # print(data['superclasses'])
    # print(data['clothing']['traditional wear']['subsubclasses'])

    # #save this data to a file
    # with open('ontology_dict.json', 'w') as file:
    #     json.dump(data, file, indent=4)


    # print_ontology('ontology_dict.json')

    print(get_class_defination('superclass'))