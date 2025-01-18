import json
import pandas as pd


def remove_fields_from_json():
    fields = [
        "superclass",
        "class",
        "type",
        "variant",
        "style",
        "product_id",
        "product_name",
    ]
    with open("FINAL_READY_DATA_Dresses.json", "r") as file:
        file = json.load(file)

    filtered_data = [{key: obj[key] for key in fields if key in obj} for obj in file]

    df = pd.DataFrame(filtered_data)
    return df


# df.to_csv("csvfile.csv", encoding="utf-8", index=False)
