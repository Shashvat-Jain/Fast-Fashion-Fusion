from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os
import logging
from transformers.utils import logging as hf_logging

hf_logging.set_verbosity_debug()
hf_logging.enable_default_handler()
hf_logging.enable_explicit_format()

# Load the model and processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)


# Function to generate caption from an image
def describe_image(image_path):
    try:
        # Open the image
        image = Image.open(image_path).convert("RGB")

        # Preprocess and generate caption
        inputs = processor(image, return_tensors="pt")
        output = model.generate(**inputs)
        caption = processor.decode(output[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        return f"Error processing {image_path}: {e}"


# Folder containing images
image_folder = "path_to_images_folder"
descriptions = {}

# Process each image in the folder
# for image_file in os.listdir(image_folder):
#     if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
#         image_path = os.path.join(image_folder, image_file)
#         description = describe_image(image_path)
#         descriptions[image_file] = description
#         print(f"{image_file}: {description}")

# Output results
print("\nGenerated Descriptions:")
print(describe_image("image.jpg"))
# for image, desc in descriptions.items():
#     print(f"{image}: {desc}")
