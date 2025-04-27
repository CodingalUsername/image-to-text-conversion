from config import HF_API_KEY
import requests
from PIL import Image
import os
from colorama import init, Fore, Style
import json

init()

def query_hf_api (api_url, payload=None, files=None, method="post"):
    headers = {
        "Authorization": "Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception("Status {response.status_code}: {response.text}")
        return response.content
    except Exception as e:
        print("{Fore.RED} X Error while calling API: {e}")
        raise

def generate_text(prompt, model="gpt2", max_new_tokens=60):
    print(f"{Fore.CYAN} Generating text with prompt: {prompt}")
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload={"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens}}
    text_bytes = query_hf_api (api_url, payload=payload)
    try:
        result = json.loads(text_bytes.decode("utf-8"))
    except Exception:
        raise Exception("Failed to decode text generation response")
    if isinstance(result, dict) and "error" in result:
        raise Exception(result["error"])
    generated = result[0].get("generated_text", "")
    return generated

def truncate_text(text, word_limit):
    words = text.strip().split()
    return " ".join(words[:word_limit])

import base64 

def get_basic_caption(image_path, model = "nlpconnect/vit-gpt2-image-captioning"):
    print(f"{Fore.MAGENTA}Getting basic caption for image: {image_path}")
    api_url= f"https://api-inference.huggingface.co/models/{model}"
    
    with open (image_path, "rb") as image_file:
        image_bytes = image_file.read()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        payload = {"inputs": encoded_image}
        response = query_hf_api(api_url, payload=payload)


        try:
            result = json.loads(response.decode("utf-8"))
            return result[0].get("generated_text", "")
        except Exception as e:
            raise Exception("Failed to decode image caption response: {e}")
        
def print_menu():
    print(f"""{Style.BRIGHT}
    {Fore.GREEN}=====
    Select output type:
       1. Caplion (5 words)
       2. Description (30 words)
       3. Summary (50 words)
       4. Exit 
       ============ """)