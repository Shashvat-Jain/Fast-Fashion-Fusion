import os
import json

def iterate_nested_dict(d, parent_key=''):
    for k, v in d.items():
        if isinstance(v, dict):
            iterate_nested_dict(v, parent_key + k + '.')
        else:
            print(f"{parent_key}{k}: {v}")

# combine all the json files(containing list of dict) in the processed_csv directory into one single list of dict
def combine_json_files(directory):
    combined_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    combined_data.extend(data)
    print(f"Combined {len(combined_data)} json files")
    return combined_data




def get_superclasses(data):
    return {item['superclass'] for item in data if 'superclass' in item}

def get_classes(data, superclass):
    class_t = {}
    for item in data:
        if item.get('superclass') == superclass and 'class' in item:
            class_t[item['class']] = item
    return {item['class'] for item in data if 'class' in item and item['superclass'] == superclass}

def get_types(data, class_t, superclass):
    return {item['type'] for item in data if 'type' in item and (item['class'] == class_t and item['superclass'] == superclass)}

def get_variants(data, type_t, class_t, superclass):
    return {tuple(item['variant']) if isinstance(item['variant'], list) else item['variant'] for item in data if 'variant' in item and (item['type'] == type_t and item['class'] == class_t and item['superclass'] == superclass)}

def get_styles(data, type_t, class_t, superclass):
    styles = set()
    for item in data:
        if 'style' in item and item['type'] == type_t and item['class'] == class_t and item['superclass'] == superclass:
            styles.add(tuple(item['style']) if isinstance(item['style'], list) else item['style'])
    return styles

# def get_styles(data, type_t, class_t, superclass):
#     return {item['style'] for item in data if 'style' in item and (item['type'] == type_t and item['class'] == class_t and item['superclass'] == superclass)}

if __name__ == "__main__":
    directory = 'dataset/processed_json'
    combined_data = combine_json_files(directory)
    # print(combined_data)
    ontology = {}
    ontology['superclasses'] = list(get_superclasses(combined_data))

    for superclass in ontology['superclasses']:
        ontology[superclass] = {}
        ontology[superclass]['classes'] = list(get_classes(combined_data, superclass))
        for class_t in ontology[superclass]['classes']:
            ontology[superclass][class_t] = {}
            ontology[superclass][class_t]['types'] = list(get_types(combined_data, class_t, superclass))
            for type_t in ontology[superclass][class_t]['types']:
                ontology[superclass][class_t][type_t] = {}
                ontology[superclass][class_t][type_t]['variants'] = list(get_variants(combined_data, type_t, class_t, superclass))
                ontology[superclass][class_t][type_t]['styles'] = list(get_styles(combined_data, type_t, class_t, superclass))


    # Frequency analysis on styles and variants
    style_frequency = {}
    variant_frequency = {}

    for item in combined_data:
        if 'style' in item:
            style = tuple(item['style']) if isinstance(item['style'], list) else item['style']
            if style in style_frequency:
                style_frequency[style] += 1
            else:
                style_frequency[style] = 1

        if 'variant' in item:
            variant = tuple(item['variant']) if isinstance(item['variant'], list) else item['variant']
            if variant in variant_frequency:
                variant_frequency[variant] += 1
            else:
                variant_frequency[variant] = 1

    # Filter styles and variants with more than 50 occurrences
    filtered_styles = {style: count for style, count in style_frequency.items() if count > 30}
    filtered_variants = {variant: count for variant, count in variant_frequency.items() if count > 30}

    # Create a new ontology with filtered styles and variants
    filtered_ontology = {}
    filtered_ontology['superclasses'] = list(get_superclasses(combined_data))

    for superclass in filtered_ontology['superclasses']:
        filtered_ontology[superclass] = {}
        filtered_ontology[superclass]['classes'] = list(get_classes(combined_data, superclass))
        for class_t in filtered_ontology[superclass]['classes']:
            filtered_ontology[superclass][class_t] = {}
            filtered_ontology[superclass][class_t]['types'] = list(get_types(combined_data, class_t, superclass))
            for type_t in filtered_ontology[superclass][class_t]['types']:
                filtered_ontology[superclass][class_t][type_t] = {}
                filtered_ontology[superclass][class_t][type_t]['variants'] = [variant for variant in get_variants(combined_data, type_t, class_t, superclass) if variant in filtered_variants]
                filtered_ontology[superclass][class_t][type_t]['styles'] = [style for style in get_styles(combined_data, type_t, class_t, superclass) if style in filtered_styles]

    # Save the filtered ontology to a json file
    with open('FILTERED_ONTOLOGY.json', 'w') as file:
        json.dump(filtered_ontology, file, indent=4)


    #save the ontology to a json file
    with open('ONTOLOGY.json', 'w') as file:
        json.dump(ontology, file, indent=4)