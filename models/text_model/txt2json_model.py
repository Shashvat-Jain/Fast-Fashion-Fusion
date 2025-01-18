from ollama import chat
from ollama import ChatResponse
import time
import re
import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def llm_response(msg, model='phi3'):
    if model == 'llama':
        model = 'llama3.2'
    else:
        model = 'phi3'

    response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': msg,
        },
    ])
    return response.message.content


def get_json_from_response(response):

    start = response.find('{')
    end = response.rfind('}')

    # Extract and print the content
    if start != -1 and end != -1:
        extracted = response[start:end+1]
        return extracted

    match = re.search(r'\{[\s\S]*\}', response)
    if not match:
        return None
    match = match.group()
    return match



def get_json_from_text_using_llm(text):
    prompt = "Convert the following text into a single JSON format: {msg}"
    prompt = prompt.format(msg=text)
    json_fin = None

    for i in range(10):
        log.info(f"Attempt {i+1}")
        response = llm_response(prompt)
        json_txt = get_json_from_response(response)

        log.info(f"Response: {response} and json_txt: {json_txt}")

        if json_txt:
            # json_txt = json_txt.replace("'", '"')
            # json_txt = json_txt.replace('True', 'true')
            # json_txt = json_txt.replace('False', 'false')
            # json_txt = json_txt.replace('None', 'null')
            # json_txt = json_txt.replace('nan', 'null')
            # json_txt = json_txt.replace('inf', 'null')
            # json_txt = json_txt.replace('-inf', 'null')

            try: 
                json_fin = json.loads(json_txt)
                return json_fin
            except:
                pass
        
    return None 



if __name__ == "__main__":

    msg = '''{'Size & Fit': "The model's height is 5' 6", 'Manufactured & Marketed By': 'FABINDIA LIMITED.Plot No. 10, Local Shopping Complex, Sector B, Pocket- 7, Vasant Kunj, New Delhi- 110070,PH: 011-40692000,Email: mailus@fabindia.net', 'Care Instructions': 'Dry Clean Only', 'Country Of Origin': 'India', 'Dimensions': '6.4M X1.16M (inclusive of blouse piece)', 'Material': 'Silk'}'''
    start_time = time.time()
    print(get_json_from_text_using_llm(msg))
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

    # print(response)

