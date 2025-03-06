import argparse
import glob

from pdf2image import convert_from_path

from utils import *
from mistral import *


def adapt_exercise(ex_id:str,
                   adaptation_type:str,
                   mistral_model="mistral") -> str:

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
        initial_prompt_path = f"prompts/{adaptation_type}.txt"
        with open(initial_prompt_path, 'r', encoding='utf-8') as file:
            first_prompt = file.read()

        # Send to mistral or pixtral
        # Use the right prompt according to the adaptation type
        ex_html = process_adaptation(mistral_model=mistral_model,
                                    #  mistral_client=mistral_client,
                                     first_prompt=first_prompt,
                                     ex_image=ex_image, 
                                     ex_text=ex_text)

        title = get_title(ex_id, ex_text, ex_html)
        print("Title:",title)
        id_cahier = get_id_cahier(ex_id=ex_id)
        print("Id cahier:",id_cahier)

        ex_html = wrap_html(ex_html, title, id_cahier)
        
        return ex_html

    except Exception as e:
        raise RuntimeError(f"Processing error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Adapt PDF exercise")
    parser.add_argument("mistral_model", type=str, help="'mistral' (small language model) or 'pixtral' (small vision language model)")
    parser.add_argument("adaptation_type", type=str, help="E.g. CacheIntrus, EditPhrase, RCCadre")
    parser.add_argument("ex_id", type=str, nargs="?", default=None)
    args = parser.parse_args()

    mistral_model = args.mistral_model
    adaptation_type = args.adaptation_type
    ex_id = args.ex_id

    if ex_id is None:
        file_paths = glob.glob("input/CacheIntrus/*.txt")
        ex_ids = [os.path.splitext(os.path.basename(path))[0] for path in file_paths]
        for ex_id in ex_ids:  # Utilise ex_id pour passer chaque identifiant
            html = adapt_exercise(ex_id=ex_id,
                                  adaptation_type = adaptation_type,
                                  mistral_model = mistral_model)
    else:
        html = adapt_exercise(ex_id=ex_id,
                              adaptation_type = adaptation_type,
                              mistral_model = mistral_model)
    # print(html)

    # Save output HTML file
    html_path = f"html_display/{ex_id}.html" # output path
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html)
    print(f"HTML content saved to {html_path}")

if __name__ == "__main__":
    main()