import argparse
import os

from dotenv import load_dotenv
from mistralai import Mistral
from pdf2image import convert_from_path
from pydantic import BaseModel
from PIL import Image

from utils import *

load_dotenv()
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

class TranscriptionResponse(BaseModel):
    markdown_content: str

class AdaptationResponse(BaseModel):
    html_content: str

def process_adaptation(mistral_model: str, # mistral ou pixtral
                       mistral_client,
                       first_prompt: str,
                       exercise_image: Image.Image, 
                       exercise_text: str) -> str:

    first_message = {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": first_prompt
                            }
                        ]
                    }
    
    # Automate the adaptation of the exercice using Mistral small language model (text-only)
    if mistral_model == "mistral":
    
        messages = [first_message,
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Adapt this exercise into clean, raw HTML content.
                                {exercise_text}"""
                            },
                            # TODO tester si l'envoi de l'exercice en 2e input texte a une influence
                            # {
                            #     "type": "text",
                            #     "text": exercise_text
                            # }
                        ]
                    }
                   ]

        response = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            max_tokens=4000
        )
    
    # Automate the adaptation of the exercice using small Pixtral vision model
    elif mistral_model == "pixtral":
    
        messages = [first_message,
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Adapt this exercise into clean, raw HTML content.
                                {exercise_text}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{exercise_image}"
                            },
                        ]
                    }
                   ]
        
        response = mistral_client.chat.complete(
            model="pixtral-12b-2409",
            messages=messages,
            max_tokens=4000
        )
    
    return response.choices[0].message.content

def adapt_exercise(ex_id:str,
                   adaptation_type:str,
                   mistral_model="mistral") -> str:

    try:
        if mistral_model == "pixtral":
            # Read input exercise PDF file + convert to image
            pdf_path = f"input/{adaptation_type}/{ex_id}.pdf"
            exercise_images = convert_from_path(pdf_path, dpi=100, thread_count=4)
            if not exercise_images:
                raise ValueError("No images extracted from PDF")
            exercise_image = exercise_images[0]
            exercise_image = image_to_base64(exercise_image)
        else:
            exercise_image = None

        # Read input exercise txt file
        txt_path = f"input/{adaptation_type}/{ex_id}.txt"
        with open(txt_path, 'r', encoding='utf-8') as file:
            exercise_text = file.read()

        # Read initial prompt txt file
        initial_prompt_path = f"prompts/{adaptation_type}.txt"
        with open(initial_prompt_path, 'r', encoding='utf-8') as file:
            first_prompt = file.read()

        # Send to mistral or pixtral
        # Use the right prompt according to the adaptation type
        html = process_adaptation(
                mistral_model=mistral_model,
                mistral_client=mistral_client,
                first_prompt=first_prompt,
                exercise_image=exercise_image, 
                exercise_text=exercise_text)

        html = wrap_html(html, ex_id)
        
        return html

    except Exception as e:
        raise RuntimeError(f"Processing error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Adapt PDF exercise")
    parser.add_argument("mistral_model", type=str, help="'mistral' (small language model) or 'pixtral' (small vision language model)")
    parser.add_argument("adaptation_type", type=str, help="E.g. CacheIntrus, EditPhrase, RCCadre")
    parser.add_argument("ex_id", type=str)
    args = parser.parse_args()

    ex_id = args.ex_id
    mistral_model = args.mistral_model
    adaptation_type = args.adaptation_type
    html = adapt_exercise(ex_id=ex_id,
                          adaptation_type = adaptation_type,
                          mistral_model=mistral_model)
    print(html)

    # Save output HTML file
    html_path = f"html_display/{ex_id}.html" # output path
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html)
    print(f"HTML content has been written to {html_path}")

if __name__ == "__main__":
    main()