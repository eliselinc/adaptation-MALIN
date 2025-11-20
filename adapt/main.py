import argparse
import ast
import glob
import json
import sys, os
import shutil

from pdf2image import convert_from_path

from utils import *

from api.gemini import *
from api.mistral import *

parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent)
from convert.malin_json_to_html import *

def get_api_client(api_name: str):
    if api_name in ["mistral","pixtral"]:
        return MistralAPI()
    elif api_name == "gemini":
        return GeminiAPI()
    else:
        raise ValueError(f"Unknown API: {api_name}")

def adapt_exercise(txt_path:str,
                   adaptation_type:str,
                   model="mistral",
                   format="html") -> str:
    
    # API CLIENT
    api_client = get_api_client(model)

    try:
        # if model == "pixtral":
        #     # Read input exercise PDF file + convert to image
        #     pdf_path = f"input/{adaptation_type}/{ex_id}.pdf"
        #     input_images = convert_from_path(pdf_path, dpi=100, thread_count=4)
        #     if not input_images:
        #         raise ValueError("No images extracted from PDF")
        #     input_image = input_images[0]
        #     input_image = image_to_base64(input_image)
        # else:
        input_image = None

        # Read input exercise txt file
        with open(txt_path, 'r', encoding='utf-8') as file:
            input_text = file.read()

        # READ SYSTEM MESSAGE according to the adaptation type
        if format == "html":
            initial_prompt_path = f"adapt/prompts_html/{adaptation_type}.txt"
        elif format == "json":
            initial_prompt_path = f"adapt/prompts_json/{adaptation_type}.txt"
        with open(initial_prompt_path, 'r', encoding='utf-8') as file:
            first_prompt = file.read()

        # EXAMPLES FOR FEW-SHOT LEARNING according to the adaptation type
        with open(f"adapt/prompts_json/examples{adaptation_type}.json", 'r', encoding='utf-8') as file:
            # List of tuples (input, output)
            examples = [(e['input'], e["output"]) for e in json.load(file)[adaptation_type]]
            #TODO e["output"] doit être lu comme string

        # SEND TO LLM
        adaptated_ex = api_client.process_adaptation(model=model,
                                                     first_prompt=first_prompt,
                                                     input_image=input_image, 
                                                     input_text=input_text,
                                                     format=format,
                                                     examples=examples,
                                                    )

        if format=="html":
            pass
            # title = get_title(ex_id, input_text, adaptated_ex)
            # # print("Title:",title)
            # id_cahier = get_id_cahier(ex_id=ex_id)
            # print("Id cahier:",id_cahier)
            # adaptated_ex = wrap_html(adaptated_ex, title, id_cahier)
        
        return adaptated_ex

    except Exception as e:
        raise RuntimeError(f"Processing error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Adapt PDF exercise")
    parser.add_argument("model", type=str, help="'mistral' (small language model) or 'pixtral' (small vision language model) or 'gemini' (flash 2.5)")
    parser.add_argument("adaptation_type", type=str, help="E.g. CacheIntrus, CM, EditPhrase, RCCadre")
    parser.add_argument("format", type=str, default="json")
    parser.add_argument("--ex_path", type=str, nargs="?", default="exercices")
    parser.add_argument("--ex_id", type=str, nargs="?", default=None)
    args = parser.parse_args()

    model = args.model
    adaptation_type = args.adaptation_type
    format = args.format.lower()
    if format not in ["json", "html"]:
        raise ValueError(f"Invalid format: '{format}'. Supported formats are 'json' and 'html'.")
    ex_path = args.ex_path
    ex_id = args.ex_id

    # CREATE OUTPUT DIRECTORY
    if format == "html":
        output_dir = f"{ex_path}/{adaptation_type}/html"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            #TODO shutil.copytree(f"{ex_path}/html/communs/", os.path.join(output_dir, "communs"))
    elif format == "json":
        output_dir = f"{ex_path}/{adaptation_type}/json"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        html_dir = f"{ex_path}/{adaptation_type}/html"
        if not os.path.exists(html_dir):
            os.makedirs(html_dir, exist_ok=True)

    # INPUT EXERCISE(S)
    if ex_id is None:
        # All exercises in the adaptation type folder
        file_paths = glob.glob(f"{ex_path}/{adaptation_type}/*.txt")
        print(f"Processing {len(file_paths)} exercises: {file_paths}")
    else:
        # Single exercise
        file_paths = [f"{ex_path}/{adaptation_type}/{ex_id}.txt"]
        print("Processing 1 exercise:", file_paths)

    # ADAPT EXERCISE(S)
    for path in file_paths:
        adaptation_json = adapt_exercise(txt_path=path,
                                    adaptation_type=adaptation_type,
                                    model=model,
                                    format=format)
        file_id = os.path.splitext(os.path.basename(path))[0] # Get ex id
        if format=="html":
            html_path = f"{output_dir}/{file_id}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(adaptation_json)
            print(f"HTML content saved to {html_path}")
        elif format=="json":
            if model=="gemini":
                adaptation_json = parse_json_response(adaptation_json)
            else:
                # print(repr(adaptation_json[:200]))
                adaptation_json = ast.literal_eval(adaptation_json)
                # print(type(adaptation_json))
                # print(adaptation_json.keys())
                # adaptation_json = json.loads(adaptation_json)
            json_path = f"{output_dir}/{file_id}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(adaptation_json, f, ensure_ascii=False, indent=2, separators=(",", ":"))
            print(f"JSON content saved to {json_path}")

            # Convert to HTML
            html_path = f"{html_dir}/{file_id}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                adaptation_html = exercise_to_html(adaptation_json)
                f.write(adaptation_html)
            print(f"HTML content saved to {html_path}")

if __name__ == "__main__":
    main()