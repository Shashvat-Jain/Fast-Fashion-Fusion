import json 
import os

for filename in os.listdir('processed_json'):
    filename = 'processed_json/' + filename
    with open(filename) as f:
        data = json.load(f)
        print(f"{len(data)} for {filename[15+17:-4]}")