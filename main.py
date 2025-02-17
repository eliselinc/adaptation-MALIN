import argparse
import os

from dotenv import load_dotenv
from mistralai import Mistral
from pdf2image import convert_from_path
from pydantic import BaseModel

from cacheintrus import process_cacheintrus
# from editphrase import process_editphrase
# from rccadre import process_rccadre
# from rcdouble import process_rcdouble

from utils import *

load_dotenv()
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

class TranscriptionResponse(BaseModel):
    markdown_content: str

class AdaptationResponse(BaseModel):
    html_content: str

def adapt_exercise(ex_id:str, txt_path: str, pdf_path: str, 
                   adaptation_type:str,
                   mistral_model="mistral") -> str:

    try:
        if mistral_model == "pixtral":
            # Convert PDF -> image
            if not pdf_path.lower().endswith('.pdf'):
                raise ValueError("Invalid PDF file")
            exercise_images = convert_from_path(pdf_path, dpi=100, thread_count=4)
            if not exercise_images:
                raise ValueError("No images extracted from PDF")
            exercise_image = exercise_images[0]
            exercise_image = image_to_base64(exercise_image)
        else:
            exercise_image = None

        # Read txt file
        with open(txt_path, 'r', encoding='utf-8') as file:
            exercise_text = file.read()

        # Send to mistral or pixtral
        # Use the right prompt according to the adaptation type
        if adaptation_type == "CacheIntrus":
            html = process_cacheintrus(
                mistral_model=mistral_model,
                mistral_client=mistral_client,
                exercise_image=exercise_image, 
                exercise_text=exercise_text)
        # elif adaptation_type == "EditPhrase":
        #     html = process_editphrase(
        #         mistral_model=mistral_model,
        #         exercise_image=exercise_image, 
        #         exercise_text=exercise_text)
        # elif adaptation_type == "RCCadre":
        #     html = process_rccadre(
        #         mistral_model=mistral_model,
        #         exercise_image=exercise_image, 
        #         exercise_text=exercise_text)
        # elif adaptation_type == "RCDouble":
        #     html = process_rcdouble(
        #         mistral_model=mistral_model,
        #         exercise_image=exercise_image, 
        #         exercise_text=exercise_text)
        else:
            raise ValueError("Invalid adaptation type. Currently supported: CacheIntrus, EditPhrase, RCCadre, RCDouble")

        html = wrap_html(html, ex_id)

        return html

    except Exception as e:
        raise RuntimeError(f"Processing error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Adapt PDF exercise")
    parser.add_argument("mistral_model", type=str, help="'mistral' (small language model) or 'pixtral' (small vision language model)")
    parser.add_argument("adaptation_type", type=str, help="Currently supported adaptation types: CacheIntrus")#, EditPhrase, RCCadre, RCDouble")
    parser.add_argument("ex_id", type=str)
    # parser.add_argument("pdf_path", type=str, help="Path to the input PDF file")
    # parser.add_argument("txt_path", type=str, help="Path to the input TXT file")
    # parser.add_argument("html_path", type=str, help="Path to the output HTML file")
    args = parser.parse_args()

    ex_id = args.ex_id
    mistral_model = args.mistral_model
    adaptation_type = args.adaptation_type
    txt_path = f"input/{adaptation_type}/{ex_id}.txt" # txt input path
    if mistral_model == "mistral":
        html = adapt_exercise(ex_id=ex_id, pdf_path=None, txt_path=txt_path, 
                              adaptation_type = adaptation_type,
                              mistral_model=mistral_model)
    elif mistral_model == "pixtral":
        pdf_path = f"input/{adaptation_type}/{ex_id}.pdf" # pdf input path
        html = adapt_exercise(ex_id=ex_id, pdf_path=pdf_path, txt_path=txt_path, 
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