import argparse
from pathlib import Path
from collections import defaultdict
import os
import re

from malin_json_to_html import *
from cartable_to_malin import *

# =============== Utils ===============

def normalize_filename(raw_name: str) -> str:
    """
    Convertit un nom de fichier comme 'P9Ex1_i7rg.js' ou 'P7DefiLangue_hq33.js'
    en 'P9Ex1.js' ou 'P7ExDefiLangue.js'
    """
    # The name is already normalized
    match = re.match(r"^(.*?)P(\d+)E[Xx]([A-Za-z0-9]+)\.json$", raw_name)
    if match:
        return raw_name

    pattern = r"^(.*?)P(\d+)(?:E[Xx])([A-Za-z0-9]+)?(_.*)?\.(jso?n?)$"
    match = re.match(pattern, raw_name)
    if not match:
        raise ValueError(f"Nom de fichier inattendu : {raw_name}")
    
    prefix, p, ex, suffix, extension = match.groups()
    print(prefix, p, ex, suffix, extension)
    print(f"{prefix}P{p}Ex{ex}.{extension}")

    
    # # Parse and normalize
    # match = re.match(r"P(\d+)([A-Za-z0-9]+)_.*\.js$", raw_name)
    # if not match:
    #     raise ValueError(f"Unexpected filename : {raw_name}")
    # p, ex = match.groups()
    # if ex.startswith("Ex"): ex = ex[2:]
    # match = re.match(r"P([A-Za-z0-9]+)E[Xx]([A-Za-z0-9]+)_.*\.js$", raw_name)
    # p, ex = match.groups()
    return f"{prefix}P{p}Ex{ex}.{extension}"
    # return f"p{p}_ex{ex}.js"

def extract_page_ex_num(filename: str, exname: bool=False):
    # Return tuple (page_num, ex_num).
    page_match = re.search(r"[Pp](\d+)", filename)
    page_num = int(page_match.group(1)) if page_match else 0
    if exname:
        ex_match = re.search(r"[Ee][Xx](\d+|[A-Za-z0-9]+)", filename)
        ex_num = str(ex_match.group(1)) # For Exercise object
    else:
        ex_match = re.search(r"[Ee][Xx](\d+)", filename)
        ex_num = int(ex_match.group(1)) if ex_match else 0 # For sorting
    return (page_num, ex_num)

# =============== Main ===============

if __name__ == "__main__":

    # Arguments parsing
    parser = argparse.ArgumentParser(description="Convert exercises")
    parser.add_argument("input_path", type=str, help="Repository input path, contains subfolders per textbook")
    parser.add_argument("--input_format", type=str, help="'cartable' or 'malin'", default=None)
    parser.add_argument("--ex_id", type=str, help="Single exercise id to process", default=None)
    args = parser.parse_args()

    input_path = Path(args.input_path)
    input_format = args.input_format.lower() if args.input_format else None
    ex_id = args.ex_id
    assert input_format in ["cartable", "malin", None], "Input format must be 'cartable' or 'malin' or None"


    if input_format is None:
        assert input_path.suffix.lower() == ".html", "If no input format is provided, the input path must be a single HTML textbook file"
        # Crée un répertoire json_malin
        output_path = input_path.parent.joinpath("json_malin")
        exercises = textbook_autonomous_html_file_to_directory(input_path, output_path)
        print(f"\n**** Extracted {len(exercises)} exercises in {output_path}")
        exit(0)

    if input_format == "cartable":
        # Input files : .js files in "json" subfolder of a Cartable format textbook
        assert input_path.joinpath("json").exists(), f"Input path must be a Cartable textbook folder and must contain a 'json' subfolder: {input_path}"
        js_files = list(input_path.glob("json/P*.js"))
        base_output_path = input_path.parent
    elif input_format == "malin":
        assert input_path.joinpath("json_malin").exists(), f"Input path must contain a 'json_malin' subfolder: {input_path}"
        # Input files: .json files in "json_malin" subfolder
        if ex_id is not None:
            js_files = [input_path.joinpath("json_malin", f"{ex_id}.json")]
        else:
            js_files = list(input_path.glob("json_malin/P*.json"))
            js_files = sorted(js_files, key=lambda p: extract_page_ex_num(p.name))
        base_output_path = input_path.parent

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
            if input_format=="cartable": json_output_path = Path(base_output_path, textbook_name, "json_malin", normalized_name.replace(".js", ".json"))
            html_output_path = Path(base_output_path, textbook_name, "html_malin", normalized_name.replace(".json", ".html").replace(".js", ".html"))

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
    print(f"\n**** Converted {len(js_files)-len(errors)} exercises")
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
        # html_global_path = Path(base_output_path, textbook_name, "html_malin", f"{textbook_name}.html")
        html_global_path.parent.mkdir(parents=True, exist_ok=True)
        with html_global_path.open("w", encoding="utf-8") as f:
            f.write(textbook_to_html(textbook))
        print(f"  HTML saved to {html_global_path}")