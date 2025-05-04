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
    

def main():
    image_path=input(f"{Fore.BLUE} Enter the path for the text generation: {Style.RESET_ALL}")
    if not os.path.exists(image_path):
       print(f"{Fore.RED} X The file '{image_path}' does not exist.")
       return
    try:
        image = Image.open(image_path) #Just to validate the image
    except Exception as e:
        print(f"{Fore.RED} X Failed to open image: {e}")
        return
    
    try:
        basic_caption = get_basic_caption(image_path)
        print(f"{Fore.YELLOW}📝 Basic caption: {Style.BRIGHT}{basic_caption}\n")

    except Exception as e:
        print(f"{Fore.RED}❌ Could not generate caption: {e}")
        return
    
    while True:
        print_menu()
        choice = input (f" {Fore.CYAN} Enter your choice (1-4): {Style. RESET_ALL}")
        if choice == "1":
            caption = truncate_text(basic_caption, 5)
            print(f"{Fore. GREEN} Caption (5 words): {Style. BRIGHT}{caption}\n")
        elif choice == "2":
            prompt_text = f"Expand the following caption into a detailed description in 30 words: {basic_caption}"
            try:
                generated = generate_text(prompt_text, max_new_tokens=40)
                description = truncate_text(generated, 30)
                print(f" {Fore. GREEN} Description (30 words): {Style.BRIGHT}{description}\n")
                      
            except Exception as e:
                print(f"{Fore.RED} X Failed to generate description: {e}")

        elif choice == "3":
            prompt_text = f"Summarize the content of the image described by caption to 50 words: {basic_caption}"
            
            try:
                generated = generate_text(prompt_text, max_new_tokens=60)
                summary = truncate_text(generated, 50)
                print(f"{Fore.GREEN}Summary (50 words): {Style.BRIGHT}{summary}\n")
            
            except Exception as e:
                print(f"{Fore.RED} Failed to generate summary: {e}")

        elif choice == "4":
            print(f"{Fore.GREEN} Goodbye!")
            break

if __name__ == "__main__":
    main()