import argparse
import glob
import os
import shutil

from pdf2image import convert_from_path

from utils import *
from mistral import *


def adapt_exercise(ex_id:str,
                   adaptation_type:str,
                   mistral_model="mistral",
                   format="html") -> str:

    try:
        if mistral_model == "pixtral":
            # Read input exercise PDF file + convert to image
            pdf_path = f"input/{adaptation_type}/{ex_id}.pdf"
            ex_images = convert_from_path(pdf_path, dpi=100, thread_count=4)
            if not ex_images:
                raise ValueError("No images extracted from PDF")
            ex_image = ex_images[0]
            ex_image = image_to_base64(ex_image)
        else:
            ex_image = None

        # Read input exercise txt file
        txt_path = f"input/{adaptation_type}/{ex_id}.txt"
        with open(txt_path, 'r', encoding='utf-8') as file:
            ex_text = file.read()

        # Read initial prompt txt file
        if format == "html":
            initial_prompt_path = f"prompts_html/{adaptation_type}.txt"
        elif format == "json":
            initial_prompt_path = f"prompts_json/{adaptation_type}.txt"
        with open(initial_prompt_path, 'r', encoding='utf-8') as file:
            first_prompt = file.read()

        # Send to mistral or pixtral
        # Use the right prompt according to the adaptation type
        adaptated_ex = process_adaptation(mistral_model=mistral_model,
                                          first_prompt=first_prompt,
                                          ex_image=ex_image, 
                                          ex_text=ex_text,
                                          format=format)

        if format=="html":
            title = get_title(ex_id, ex_text, adaptated_ex)
            # print("Title:",title)
            id_cahier = get_id_cahier(ex_id=ex_id)
            print("Id cahier:",id_cahier)
            adaptated_ex = wrap_html(adaptated_ex, title, id_cahier)
        elif format=="json":
            print(adaptated_ex)
        
        return adaptated_ex

    except Exception as e:
        raise RuntimeError(f"Processing error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Adapt PDF exercise")
    parser.add_argument("mistral_model", type=str, help="'mistral' (small language model) or 'pixtral' (small vision language model)")
    parser.add_argument("adaptation_type", type=str, help="E.g. CacheIntrus, CM, EditPhrase, RCCadre")
    parser.add_argument("format", type=str, default="json")
    parser.add_argument("ex_id", type=str, nargs="?", default=None)
    args = parser.parse_args()

    mistral_model = args.mistral_model
    adaptation_type = args.adaptation_type
    format = args.format.lower()
    if format not in ["json", "html"]:
        raise ValueError(f"Invalid format: '{format}'. Supported formats are 'json' and 'html'.")
    ex_id = args.ex_id

    # Create output directory
    if format == "html":
        output_dir = f"output_html/{adaptation_type}/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            shutil.copytree("output_html/communs/", os.path.join(output_dir, "communs"))
    elif format == "json":
        output_dir = f"output_json/{adaptation_type}/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    if ex_id is None:
        file_paths = glob.glob(f"input/{adaptation_type}/*.txt")
        print(file_paths)
        ex_ids = [os.path.splitext(os.path.basename(path))[0] for path in file_paths]
        for ex_id in ex_ids:

            adapted_ex = adapt_exercise(ex_id=ex_id,
                                        adaptation_type = adaptation_type,
                                        mistral_model = mistral_model,
                                        format = format)
            if format=="html":
                html_path = f"{output_dir}{ex_id}.html"
                with open(html_path, 'w', encoding='utf-8') as file:
                    file.write(adapted_ex)
                print(f"HTML content saved to {html_path}")
            elif format=="json":
                json_path = f"{output_dir}{ex_id}.json"
                with open(json_path, 'w', encoding='utf-8') as file:
                    file.write(adapted_ex)
                print(f"JSON content saved to {json_path}")
    else:
        adapted_ex = adapt_exercise(ex_id=ex_id,
                                    adaptation_type = adaptation_type,
                                    mistral_model = mistral_model,
                                    format = format)
        if format == "html":
            html_path = f"{output_dir}{ex_id}.html"
            with open(html_path, 'w', encoding='utf-8') as file:
                file.write(adapted_ex)
            print(f"HTML content saved to {html_path}")
        elif format=="json":
            json_path = f"{output_dir}{ex_id}.json"
            with open(json_path, 'w', encoding='utf-8') as file:
                file.write(adapted_ex)
            print(f"JSON content saved to {json_path}")

if __name__ == "__main__":
    main()