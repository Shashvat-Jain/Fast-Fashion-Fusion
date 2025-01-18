import classification as cls
import load_ontology as lo
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import pandas as pd



def main():
    path = 'dataset/processed_csv'


    prompt_input = ''' product_name: {product_name},
    description: {description},{meta_info},
    {feature_list}
    '''

    for filename in os.listdir(path):
        if filename.endswith('.csv'):
            data = []
            wasted = 0
            total = 0
            i = 0
            update_ontology = False
            print(f"Processing {filename}")
            df = pd.read_csv(f'{path}/{filename}')
            total_rows = len(df)
            ontology = json.load(open('ontology_dict.json'))

            for index, row in df.iterrows():
                product_name = row['product_name']
                description = row['description']
                meta_info = row['meta_info']
                if row['feature_list'] == '[]':
                    feature_list = ''
                else:
                    feature_list = f"features: {row['feature_list']}"

                feature_list = row['feature_list']
                prompt = prompt_input.format(product_name=product_name, description=description, meta_info=meta_info, feature_list=feature_list)
                
                try:
                # if 1:
                    debug = False
                    a, superclass = cls.get_existing_class_from_text_using_ollama(prompt, ontology['superclasses'], lo.get_class_defination('superclass'), debug)
                    b, class_t = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass]['classes'], lo.get_class_defination('class'), debug, parent_classes=[superclass])
                    if b:
                        c, type_t = cls.get_new_class_from_text_using_ollama(prompt, lo.get_class_defination('type'), debug, parent_classes=[superclass, class_t])
                        d, variant = cls.get_new_class_from_text_using_ollama(prompt, lo.get_class_defination('variant'), debug, parent_classes=[superclass, class_t, type_t])
                        e, style = cls.get_new_class_from_text_using_ollama(prompt, lo.get_class_defination('style'), debug, parent_classes=[superclass, class_t, type_t])                    
                    else:    
                        c, type_t = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass][class_t]['types'], lo.get_class_defination('type'), debug, parent_classes=[superclass, class_t])
                        if c:
                            d, variant = cls.get_new_class_from_text_using_ollama(prompt, lo.get_class_defination('variant'), debug, parent_classes=[superclass, class_t, type_t])
                            e, style = cls.get_new_class_from_text_using_ollama(prompt, lo.get_class_defination('style'), debug, parent_classes=[superclass, class_t, type_t])
                        else:
                            d, variant = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass][class_t][type_t]['variants'], lo.get_class_defination('variant'), debug, parent_classes=[superclass, class_t, type_t])
                            e, style = cls.get_new_or_existing_class_from_text_using_ollama(prompt, ontology[superclass][class_t][type_t]['styles'], lo.get_class_defination('style'), debug, parent_classes=[superclass, class_t, type_t])

                    if b:
                        if 'classes' not in ontology[superclass]:
                            ontology[superclass]['classes'] = [class_t]
                        else:
                            ontology[superclass]['classes'].append(class_t)
                        ontology[superclass][class_t] = {}
                        c=True
                        d=True
                        e=True
                    if c:
                        if 'types' not in ontology[superclass][class_t]:
                            ontology[superclass][class_t]['types'] = [type_t]
                        else:
                            ontology[superclass][class_t]['types'].append(type_t)
                        ontology[superclass][class_t][type_t] = {}
                        d=True
                        e=True
                    if d:
                        if 'variants' not in ontology[superclass][class_t][type_t]:
                            ontology[superclass][class_t][type_t]['variants'] = [variant]
                        else:
                            ontology[superclass][class_t][type_t]['variants'].append(variant)
                    if e:
                        if 'styles' not in ontology[superclass][class_t][type_t]:
                            ontology[superclass][class_t][type_t]['styles'] = [style]
                        else:
                            ontology[superclass][class_t][type_t]['styles'].append(style)

                except:
                    print(f"Error classifing row {index + 1} of {total_rows} in {filename}")
                    wasted += 1
                    continue

                ontology_dict = {
                    "superclass": superclass,
                    "class": class_t,
                    "type": type_t,
                    "variant": variant,
                    "style": style
                }
                compulsory_properties = {
                    "product_id": row['product_id'],
                    "product_name": row['product_name']
                }

                properties = json.loads(row['style_attributes'])
                # try:
                #     properties = cls.get_filtered_properties_from_attribute(json.loads(row['style_attributes']), debug=True)
                # except:
                #     print(f"Error filtering row {index + 1} of {total_rows} in {filename}")
                #     wasted += 1
                #     continue

                combined_dict = {**properties, **ontology_dict}
                combined_dict2 = {**combined_dict, **compulsory_properties}
                data.append(combined_dict2)
                
                if i % 10 == 0:
                    print(f"Processed row {index + 1} of {total_rows} in {filename}")

                if i % 50 == 0:
                    with open('ontology_dict.json', 'w') as f:
                            print(f"Updating class in ontology (adding {class_t})")
                            json.dump(ontology, f)      
                    with open(f'dataset/processed_json/FINAL_READY_DATA_{filename[:-4]}.json', 'w') as f:
                        print(f"Saving another chunk data -- Total wasted rows: {wasted} out of {total}")
                        json.dump(data, f)
                i+=1
    
            print("Finished processing", filename)
            with open(f'dataset/processed_json/FINAL_READY_DATA_{filename[:-4]}.json', 'w') as f:
                print("Saving chunk data")
                json.dump(data, f)
    return

                
if __name__ == "__main__":
    # cls.filter_style_attributes('../data/processed_csv', 'dataset/processed_csv', min_num_attributes=0)
    main()
