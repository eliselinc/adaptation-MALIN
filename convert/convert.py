import argparse
from pathlib import Path
from collections import defaultdict
import os
import re

from patty_json_to_html_v2 import *
from cartable_to_patty import *

# =============== Utils ===============

def normalize_filename(raw_name: str) -> str:
    """
    Convertit un nom de fichier comme 'P9Ex1_i7rg.js' ou 'P7DefiLangue_hq33.js'
    en 'P9Ex1.js' ou 'P7ExDefiLangue.js'
    """
    # The name is already normalized
    match = re.match(r"P(\d+)Ex([A-Za-z0-9]+)\.json$", raw_name)
    if match:
        return raw_name
    
    # # Parse and normalize
    # match = re.match(r"P(\d+)([A-Za-z0-9]+)_.*\.js$", raw_name)
    # if not match:
    #     raise ValueError(f"Unexpected filename : {raw_name}")
    # p, ex = match.groups()
    # if ex.startswith("Ex"): ex = ex[2:]
    match = re.match(r"P([A-Za-z0-9]+)Ex([A-Za-z0-9]+)_.*\.js$", raw_name)
    p, ex = match.groups()
    return f"P{p}Ex{ex}.js"
    # return f"p{p}_ex{ex}.js"

def extract_page_ex_num(filename: str, exname: bool=False):
    # Return tuple (page_num, ex_num).
    page_match = re.search(r"[Pp](\d+)", filename)
    page_num = int(page_match.group(1)) if page_match else 0
    if exname:
        ex_match = re.search(r"[Ee]x(\d+|[A-Za-z0-9]+)", filename)
        ex_num = str(ex_match.group(1)) # For Exercise object
    else:
        ex_match = re.search(r"[Ee]x(\d+)", filename)
        ex_num = int(ex_match.group(1)) if ex_match else 0 # For sorting
    return (page_num, ex_num)

# =============== Main ===============

if __name__ == "__main__":

    # Arguments parsing
    parser = argparse.ArgumentParser(description="Convert exercises")
    parser.add_argument("input_path", type=str, help="Repository input path, contains subfolders per textbook")
    parser.add_argument("--input_format", type=str, help="'cartable' or 'patty'", default=None)
    args = parser.parse_args()

    input_path = Path(args.input_path)
    input_format = args.input_format.lower() if args.input_format else None
    assert input_format in ["cartable", "patty", None], "Input format must be 'cartable' or 'patty' or None"


    if input_format is None:
        assert input_path.suffix.lower() == ".html", "If no input format is provided, the input path must be a single HTML textbook file"
        # Crée un répertoire json_patty
        output_path = input_path.parent.joinpath("json_patty")
        textbook_autonomous_html_file_to_directory(input_path, output_path)
        print(f"\n**** Extracted exercises in {output_path} ****")
        exit(0)

    if input_format == "cartable":
        # Input files : .js files in subdirectories in the json subfolders of Cartable format textbooks
        assert input_path.joinpath("json").exists(), f"Input path must be a Cartable textbook folder and must contain a 'json' subfolder: {input_path}"
        # if input_path.joinpath("json").exists():  # Process a single textbook
        js_files = list(input_path.glob("json/P*.js"))
        base_output_path = input_path.parent
        # else: # Process all textbooks (subdirectories)
        #     js_files = list(input_path.glob("*/json/P*.js"))
        #     base_output_path = input_path
    elif input_format == "patty":
        assert input_path.joinpath("json_patty").exists(), f"Input path must contain a 'json_patty' subfolder: {input_path}"
        # Input files: .json files in "json_patty" subfolders of textbooks
        # if input_path.joinpath("json_patty").exists():  # Process a single textbook
        js_files = list(input_path.glob("json_patty/p*.json")) + list(input_path.glob("json_patty/P*.json"))
        base_output_path = input_path.parent
    # js_files = sorted(js_files, key=lambda p: int(re.search(r"P|p(\d+)", p.name).group(1)) if re.search(r"P|p(\d+)", p.name) else 0) # Odre croissant par numéro de page
    js_files = sorted(js_files, key=lambda p: extract_page_ex_num(p.name))

    textbooks = defaultdict(list)  # Group exercises by textbook name
    errors = []
    for input_file_str in js_files:
        print(f"\nProcessing {input_file_str}")
        try:
            input_path = Path(input_file_str).resolve()
            textbook_name = input_path.parts[-3]  # e.g., manuel_CM1_francais_Adrian
            raw_filename = input_path.name  # e.g., P9Ex1_i7rg.js

            try:
                normalized_name = normalize_filename(raw_filename)
            except AttributeError as ve:
                raise ValueError(f"Filename error, must be P<num>Ex<num/name>.json/js: {raw_filename}")
            if input_format=="cartable": json_output_path = Path(base_output_path, textbook_name, "json_patty", normalized_name.replace(".js", ".json"))
            html_output_path = Path(base_output_path, textbook_name, "html_patty", normalized_name.replace(".json", ".html").replace(".js", ".html"))

            if input_format=="cartable": exercise = convert_file(input_path)  # Convert Cartable to Exercise object (JSON Patty)
            else: exercise = load_exercise(input_path)  # Load Patty JSON to Exercise object
            html_exercise = exercise_to_html(exercise)  # Convert Exercise object to HTML

            # Individual saves
            if input_format=="cartable":
                json_output_path.parent.mkdir(parents=True, exist_ok=True)
                with json_output_path.open("w", encoding="utf-8") as f:
                    json.dump(exercise.model_dump(mode="json"), f, ensure_ascii=False, indent=2, separators=(",", ":"))
                print(f"  JSON saved to {json_output_path}")
            html_output_path.parent.mkdir(parents=True, exist_ok=True)
            with html_output_path.open("w", encoding="utf-8") as f:
                f.write(html_exercise)
            print(f"  HTML saved to {html_output_path}")

            # Extract page number and exercise number/name from input file name
            page, number = extract_page_ex_num(normalized_name, exname=True)
            # match = re.match(r"p(\d+)_ex(.+)\.js", normalized_name)
            # if not match:
            #     raise ValueError(f"Unexpected file name: {normalized_name} / {raw_filename}")
            # page = int(match.group(1))
            # number = match.group(2)

            # Create TextbookExercise object
            textbook_exercise = TextbookExercise(page=page, number=number, exercise=exercise)
            textbooks[textbook_name].append(textbook_exercise)
        except ValueError as ve:
            errors.append(input_file_str)
            print(f"  !!! Skipping file due to error: {ve}")
    print(f"\n**** Converted {len(js_files)-len(errors)} exercises ****")
    print(f"**** {len(errors)} errors: {errors}")

    # Generate unique HTML for each textbook
    for textbook_name, exercises in textbooks.items():
        print(f"\nProcessing full textbook: {textbook_name}")
        textbook = Textbook(  # Create Textbook object
            title=textbook_name,
            chapters=[],  # If you want to group by chapter, adapt here
            exercises=exercises
        )
        html_global_path = Path(base_output_path, textbook_name, f"{textbook_name}.html")
        # html_global_path = Path(base_output_path, textbook_name, "html_patty", f"{textbook_name}.html")
        html_global_path.parent.mkdir(parents=True, exist_ok=True)
        with html_global_path.open("w", encoding="utf-8") as f:
            f.write(textbook_to_html(textbook))
        print(f"  HTML saved to {html_global_path}")