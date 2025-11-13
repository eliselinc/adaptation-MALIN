"""
Convertit les fichiers JSON du Cartable en JSON format de Patty

##### Exécution #####

cd ~/Documents/malin/src/Elise/src/adaptation-VJ/Patty/backend
source venv/bin/activate
python3 -m generated.convert_to_patty_json

##### Données #####

Adaptations du Cartable : 
    Elise/data/adaptations_cartable/<id_textbook>/*.html
    Elise/data/adaptations_cartable/<id_textbook>/json/*.js
Adaptations du Cartable réduites en un HTML minimal (NON UTILISE) :
    Elise/data/adaptations_cartable/minimal_html/<id_textbook>/*.html
Adaptations du Cartable converties au format Patty : 
    Elise/data/adaptations_cartable/<id_textbook>/json_patty/*.json
    Elise/data/adaptations_cartable/<id_textbook>/html_patty/*.html    # POUR VISUALISATION
Adaptations générées par Patty : 
    Elise/data/adaptations_patty/<id_textbook>/json_patty/*.json
    Elise/data/adaptations_patty/<id_textbook>/html_patty/*.html    # POUR VISUALISATION
"""

import glob
import json
import re
from collections import defaultdict
from pathlib import Path
from patty_json_to_html_v2 import exercise_to_html, textbook_to_html #json_to_html
from patty_json_to_html_v2 import *
# import (
#     BaseModel, Exercise, Pages, Text, Whitespace, 
#     EditableTextInput, 
#     InstructionLine, InstructionPage, StatementLine, StatementPage, StatementPages,
#     InstructionComponent, ExampleComponent, HintComponent, StatementComponent, ReferenceComponent
# )

# =============== Constants ===============

COLOR_MAP = {
    11: "#000000",
    0: "#ffff00",
    4: "#FFC0CB",
    7: "#bbbbff",
    8: "#bbffbb",
    5: "#bbbbbb",
    2: "#ff8084"
}

# =============== Parsing functions ===============

def parse_text_with_spaces(tokens: list, style=None, colors=None) -> list:
    components = []
    for token in tokens:
        if isinstance(token, str):
            if token.strip() == "":
                components.append(Whitespace(kind="whitespace"))
            elif token == "&rarr;":
                components.append(Arrow(kind="arrow"))
            else:
                if style and colors and style.startswith("sel") and style[3:].isdigit():
                    idx = int(style.replace("sel", "")) - 1
                    color = colors[idx] if idx < len(colors) else "#ffff00"
                    components.append(Text(kind="text", text=token, highlighted=color))
                else:
                    components.append(Text(kind="text", text=token))
    return components

def parse_styles(item, colors):
    styles_dict = item[2] if len(item) > 2 else {}
    styles_content = item[1]
    style = styles_dict.get("style")
    boxed = style == "boite"
    underlined = style == "stu"

    # Cas spécial : "styles" contenant un unique "coche" pour une phrase
    if (len(styles_content) == 1 and isinstance(styles_content[0], list) and styles_content[0][0] == "coche"):
        # print("DEBUG UNIQUE COCHE")
        coche_item = styles_content[0]
        return parse_coche_entry(coche_item, colors, boxed=boxed)
        # coche_item = styles_content[0]
        # boxed = boxed
        # ncolors_coche = coche_item[2].get("ncolors") if len(coche_item) > 2 and isinstance(coche_item[2], dict) else 1
        # colors_coche = colors[:ncolors_coche]
        # return [
        #     SelectableInput(
        #         kind="selectableInput",
        #         boxed=boxed,
        #         colors=colors_coche,
        #         contents=parse_text_with_spaces(coche_item[1], colors=colors_coche)
        #     )
        # ]
    # Cas "boite", "stu" ou "selX" : encapsule tout le groupe dans un seul formatted
    if boxed or underlined or (style and style.startswith("sel")):
        formatted = {
            "kind": "formatted",
            "bold": False,
            "italic": False,
            "underlined": underlined,
            "boxed": boxed,
            "highlighted": None,
            "contents": []
        }
        if style and style.startswith("sel") and colors:
            sel_suffix = style.replace("sel", "")
            if style == "selc":
                formatted["highlighted"] = None
            elif sel_suffix.isdigit():
                idx = int(sel_suffix) - 1
                formatted["highlighted"] = colors[idx] if idx < len(colors) else "#ffff00"
            else:
                formatted["highlighted"] = "#ffff00" # is default color useful or default is None ? #TODO
        specialcontents = [] # Separate list for special contents like echange, coche, etc.
        for token in styles_content:
            if isinstance(token, list) and token[0] == "styles":
                formatted["contents"].extend(parse_styles(token, colors))
            elif isinstance(token, list) and token[0] == "echange":
                specialcontents.append(parse_echange(token, colors))
            elif isinstance(token, list) and token[0] == "coche":
                specialcontents.extend(parse_coche_entry(token, colors, boxed))
            elif isinstance(token, list) and token[0] == "clavier":
                specialcontents.extend(parse_clavier(token, colors))
            elif isinstance(token, str):
                formatted["contents"].extend(parse_text_with_spaces([token], style=style, colors=colors))
            else:
                raise ValueError(f"Token inattendu dans styles_content: {token}")
        # Si specialcontents contient un SwappableInput, on imbrique les éléments formattés dans le SwappableInput et non l'inverse
        if specialcontents and isinstance(specialcontents[0], SwappableInput):
            for obj in specialcontents:
                if getattr(obj, "kind", None) == "swappableInput":
                    formatted_obj = Formatted(**formatted)
                    formatted_obj.contents.extend(obj.contents) # ajout du contenu du swappable dans le formatted
                    obj.contents = [formatted_obj] # ajout du formatted dans le swappable
                    return [obj]
            # Si pas de swappableInput, comportement normal
            formatted["contents"].extend(specialcontents)
            return [Formatted(**formatted)]
        else:
            return [Formatted(**formatted)]
        return result
    # Cas général
    return parse_text_with_spaces(styles_content, style=style, colors=colors)

def parse_instr_qcm(item) -> list:
    choices = item[1]
    components = []
    for i, choice in enumerate(choices):
        components.append(
            Choice(
                kind="choice",
                contents=parse_text_with_spaces([choice])
            )
        )
        if i < len(choices) - 1:
            components.append(Whitespace(kind="whitespace"))
    return components

def parse_qcm(item, html_colors=None, show_choices_by_default=False) -> list: #TODO show_choices_by_default doit être déterminé dynamiquement
    choices = item[1]
    return [
        MultipleChoicesInput(
            kind="multipleChoicesInput",
            choices=[
                FormattedTextContainer(
                    contents=parse_text_with_spaces([choice])
                )
                for choice in choices
            ],
            showChoicesByDefault=show_choices_by_default
        )
    ]

def parse_clavier(item, html_colors=None) -> list:
    text = item[1][0].strip()  # Souvent une chaîne vide
    return [
        EditableTextInput(
            kind="editableTextInput",
            contents=[Text(kind="text", text=text)],
            showOriginalText=False
        )
    ]

def is_trait_like_coche(content_list):
    return (
        any(isinstance(item, list) and item[0] == "coche" for item in content_list)
        and any(isinstance(item, str) and len(item) == 1 and item.isalpha() for item in content_list)
    )

def parse_trait_like_coche(content_list, html_colors=None):
    """
    Regroupe toutes les lettres et coches en un seul mot/phrase,
    et retourne un unique EditableTextInput pour toute la ligne.
    """
    word = ""
    for item in content_list:
        if isinstance(item, str):
            if item.strip() == "" or item == "◆":
                continue  # Ignore les espaces et séparateurs
            else:
                word += item
        elif isinstance(item, list) and item[0] == "coche":
            continue  # Ignore les coches, elles servent juste de séparateur
        else:
            pass  # Ignore tout le reste

    # Crée un unique EditableTextInput pour toute la ligne
    return [
        EditableTextInput(
            kind="editableTextInput",
            contents=[Text(kind="text", text=word)],
            showOriginalText=False,
            increaseHorizontalSpace=True
        )
    ]

def parse_coche_entry(item, html_colors=None, boxed=False):
    """
    Parse une entrée 'coche' de type:
    ["coche", [["styles", ["mot"], {"style":"boite"}]], {"ncolors":2}]
    ["coche", ["En"], {"ncolors":2}]
    Retourne une liste de blocs Patty (SelectableInput ou SwappableInput).
    """
    ncolors = item[2].get("ncolors") if len(item) > 2 and isinstance(item[2], dict) else 1
    colors = html_colors[:ncolors-1]
    mots = item[1]
    # print("DEBUG COLORS COCHE",colors)
    # print("DEBUG COLORS COCHE",html_colors)
    if colors == []: 
        colors=[html_colors[0]] # Si aucune couleur n'est précisée, on prend la première couleur par défaut

    def contains_echange(block):
        if isinstance(block, list):
            if block and block[0] == "echange":
                return True
            if block and block[0] == "styles":
                return any(contains_echange(sub) for sub in block[1])
            return any(contains_echange(sub) for sub in block)
        return False
    
    def contains_coche(block):
        if isinstance(block, list):
            if block and block[0] == "coche":
                return True
            if block and block[0] == "styles":
                return any(contains_coche(sub) for sub in block[1])
            return any(contains_coche(sub) for sub in block)
        return False

    # Cas particulier SwappableInput
    if any(isinstance(m, list) and contains_echange(m) for m in mots):
        contents = []
        for mot in mots:
            if isinstance(mot, list) and mot[0] == "styles":
                styles_content = mot[1]
                for sub in styles_content:
                    if isinstance(sub, list) and sub[0] == "echange":
                        contents.append(parse_echange(sub))
                    else:
                        contents.extend(parse_text_with_spaces([sub]))
            elif isinstance(mot, str):
                contents.extend(parse_text_with_spaces([mot], colors=colors))
            else:
                raise ValueError(f"Unexpected type in mots: {type(mot)}")
        return contents

    # Cas coche imbriqué
    if any(isinstance(m, list) and contains_coche(m) for m in mots):
        print("DEBUG COCHE IMBRIQUE") # TODO mais pas implémenté dans Patty
        # raise ValueError("Coche imbriqué non géré dans parse_coche_entry")
        return []
        # coche_contents = []
        # for mot in mots:
        #     if isinstance(mot, list) and mot[0] == "coche":
        #         # Récupère le ncolors propre à ce coche imbriqué
        #         ncolors_sub = mot[2].get("ncolors") if len(mot) > 2 and isinstance(mot[2], dict) else 1
        #         colors_sub = html_colors[:ncolors_sub-1]
        #         sub_coche = parse_coche_entry(mot, html_colors)
        #         print("SUB_COCHE:", sub_coche)
        #         coche_contents.extend(sub_coche)  # <-- Ajoute le composant entier
        #     elif isinstance(mot, str):
        #         coche_contents.extend(parse_text_with_spaces([mot]))
        # return [
        #     SelectableInput(
        #         kind="selectableInput",
        #         boxed=False,
        #         colors=colors,
        #         contents=coche_contents
        #     )
        # ]

    # Cas simple : liste de str (mot ou phrase)
    if all(isinstance(mot, str) for mot in mots):
        coche_contents = parse_text_with_spaces(mots, colors=colors)
        return [
            SelectableInput(
                kind="selectableInput",
                boxed=boxed,
                colors=colors,
                contents=coche_contents
            )
        ]

    # Cas "styles"
    coche_contents = []
    for mot in mots:
        if isinstance(mot, str):
            coche_contents.extend(parse_text_with_spaces([mot], colors=colors))
        elif isinstance(mot, list) and mot[0] == "styles":
            coche_contents.extend(parse_styles(mot, colors))
    if coche_contents:
        return [
            SelectableInput(
                kind="selectableInput",
                boxed=boxed,
                colors=colors,
                contents=coche_contents
            )
        ]
    return []

def parse_coche_lettres(item, html_colors=None):
    """
    Parse une entrée 'coche lettres' de type:
    ['coche lettres', [mot, ncolors]]
    Retourne une liste de SelectableInput (un par lettre du mot).
    """
    mot = item[1][0]
    ncolors = item[1][1]
    colors = html_colors[:ncolors-1]
    return [
        SelectableInput(
            kind="selectableInput",
            boxed=True,
            colors=colors,
            contents=[Text(kind="text", text=lettre)]
        )
        for lettre in mot
    ]

def parse_echange(echange_block, html_colors=None):
    """
    Prend ["echange", [...]] et retourne un dict SwappableInput Pydantic.
    """
    contents = []
    for token in echange_block[1]:
        if isinstance(token, list):
            if token[0] == "styles":
                contents.extend(parse_styles(token, html_colors))
            elif token[0] == "echange": # Cas imbriqué (rare)
                contents.append(parse_echange(token, html_colors))
            else:
                contents.extend(parse_text_with_spaces([token], html_colors))
                raise ValueError(f"DEBUG Unknown token in echange: {token}")
        else:
            contents.extend(parse_text_with_spaces([token]))
    return SwappableInput(
        kind="swappableInput",
        contents=contents
    )

def parse_instruction(enonce: list, html_colors=None) -> InstructionPage:
    lines = []
    contents = []
    for item in enonce:
        if item == "\n":
            if contents:
                lines.append(InstructionLine(contents=contents))
                contents = []
        elif isinstance(item, str):
            contents.extend(parse_text_with_spaces([item]))

        elif isinstance(item, list):
            # MANAGE FORMATTED TEXT AND STYLES SPECIFIC TO THE INSTRUCTION
            if item[0] == "styles":
                contents.extend(parse_styles(item, html_colors))
            # CHOICE OBJECT
            elif item[0] == "qcm_enonce":
                contents.extend(parse_instr_qcm(item))

    if contents:
        lines.append(InstructionLine(contents=contents))
    # print("DEBUG LINES BEFORE FILTER:", lines)
    lines = filter_lines(lines)
    # print("DEBUG LINES AFTER FILTER:", lines)
    return InstructionPage(lines=lines)

def parse_example(example: list) -> ExampleComponent:
    return
# Première page non éditable, cf Adrian p13ex7 
# Première page non éditable, avec "Exemple :" sur une ligne seule cf Adrian p15ex9

def parse_statement(pages_raw: list, html_colors) -> StatementPagesV1:
    pages = []
    for page_index, (_, content_list) in enumerate(pages_raw):
        lines = []
        contents = []
        if is_trait_like_coche(content_list):
            print("DEBUG TRAIT LIKE COCHE")
            trait_contents = parse_trait_like_coche(content_list, html_colors)
            if trait_contents:
                lines.append(StatementLine(contents=trait_contents))
        else:
            # parsing classique
            for item in content_list:
                if item == "\n":
                    if contents:
                        lines.append(StatementLine(contents=contents))
                        contents = []
                elif isinstance(item, str):
                    contents.extend(parse_text_with_spaces([item]))
                elif isinstance(item, list):
                    if item[0] == "styles":
                        # print("DEBUG STYLES")
                        contents.extend(parse_styles(item, html_colors))
                    elif item[0] == "qcm":
                        # print("DEBUG QCM")
                        contents.extend(parse_qcm(item, html_colors))
                    elif item[0] == "clavier":
                        # print("DEBUG CLAVIER")
                        contents.extend(parse_clavier(item, html_colors))
                    elif item[0] == "coche":
                        # print("DEBUG COCHE")
                        contents.extend(parse_coche_entry(item, html_colors))
                    elif item[0] == "echange":
                        # print("DEBUG ECHANGE")
                        contents.append(parse_echange(item, html_colors))
                    elif item[0] == "image":
                        # print("DEBUG IMAGE")
                        pass #TODO
                    elif item[0] == "exposant":
                        contents.extend(parse_exposant(item))
                    elif item[0] == "coche lettres":
                        # print("DEBUG COCHE LETTRES")
                        contents.extend(parse_coche_lettres(item, html_colors))
                    else:
                        raise ValueError(f"DEBUG Unknown item in statement: {item[0]}")
        if contents:
            lines.append(StatementLine(contents=contents))
        # print("DEBUG LINES BEFORE FILTER:", lines)
        lines = filter_lines(lines)
        # print("DEBUG LINES AFTER FILTER:", lines)
        pages.append(StatementPage(lines=lines))
    return StatementPagesV1(pages=pages)

def parse_exposant(item):
    # item = ["exposant", ["^re", "re"]]
    exposant_str = item[1][1] if len(item[1]) > 1 else item[1][0]
    return [Text(kind="text", text=exposant_str)]

# =============== Filtering and cleaning functions ===============

def filter_lines(lines):
    """
    This is to remove empty lines or lines that only contain whitespace.
    Keeps only lines that contain at least one non-empty component such as text, swappableInput, selectableInput, multipleChoicesInput, editableTextInput, formatted, or choice.
    """
    return [
        line for line in lines
        if any(
            (getattr(c, "kind", None) == "text" and getattr(c, "text", "").strip())
            or getattr(c, "kind", None) in [
                "swappableInput",
                "selectableInput",
                "multipleChoicesInput",
                "editableTextInput",
                "formatted",
                "choice"
            ]
            for c in getattr(line, "contents", [])
        )
    ]

def clean_exercise_whitespace(exercise):
    """
    Nettoie récursivement tous les contents de l'exercice :
    - enlève les whitespace au début/fin de chaque contents
    - réduit les whitespace consécutifs à un seul
    - strip tous les éléments à l'intérieur de "text"
    """

    def clean_components(components):
        # Enlève les whitespace au début et à la fin
        while components and getattr(components[0], "kind", None) == "whitespace":
            components.pop(0)
        while components and getattr(components[-1], "kind", None) == "whitespace":
            components.pop()
        # Réduit les whitespace consécutifs à un seul
        cleaned = []
        prev_is_ws = False
        for c in components:
            # Nettoie récursivement tous les attributs de type liste
            for attr in dir(c):
                if attr.startswith("_"):
                    continue
                value = getattr(c, attr, None)
                if isinstance(value, list):
                    setattr(c, attr, clean_components(value))
            # Strip sur les Text
            if getattr(c, "kind", None) == "text":
                c.text = c.text.strip()
            is_ws = getattr(c, "kind", None) == "whitespace"
            if is_ws:
                if not prev_is_ws:
                    cleaned.append(c)
            else:
                cleaned.append(c)
            prev_is_ws = is_ws
        return cleaned

    # Parcours toutes les lines de l'exercice (instruction, statement, example, hint, etc.)
    for attr in ["instruction", "statement", "example", "hint", "reference"]:
        section = getattr(exercise, attr, None)
        if section is None:
            continue
        # statement.pages ou instruction.lines
        lines_list = []
        if hasattr(section, "lines"):
            lines_list = section.lines
        elif hasattr(section, "pages"):
            for page in section.pages:
                lines_list.extend(page.lines)
        for line in lines_list:
            line.contents = clean_components(line.contents)

def simplify_formatted_blocks(exercise):
    """
    Transforme les blocs 'formatted' sans style en simples blocs 'text' si possible.
    """

    def is_plain_formatted(obj):
        # Vérifie si le bloc formatted n'a aucun style et contient un seul text
        if getattr(obj, "kind", None) != "formatted":
            return False
        style_keys = ["bold", "italic", "underlined", "highlighted", "boxed", "superscript", "subscript"]
        if any(getattr(obj, k, None) not in [False, None] for k in style_keys):
            return False
        if len(getattr(obj, "contents", [])) == 1 and getattr(obj.contents[0], "kind", None) == "text":
            return True
        return False

    def simplify(components):
        new_components = []
        for c in components:
            # Récursivement simplifie les sous-composants
            if hasattr(c, "contents") and isinstance(c.contents, list):
                c.contents = simplify(c.contents)
            # Si c'est un formatted sans style, remplace par son unique text
            if is_plain_formatted(c):
                new_components.append(c.contents[0])
            else:
                new_components.append(c)
        return new_components

    # Parcours toutes les lines/pages de l'exercice
    for attr in ["instruction", "statement", "example", "hint", "reference"]:
        section = getattr(exercise, attr, None)
        if section is None:
            continue
        lines_list = []
        if hasattr(section, "lines"):
            lines_list = section.lines
        elif hasattr(section, "pages"):
            for page in section.pages:
                lines_list.extend(page.lines)
        for line in lines_list:
            line.contents = simplify(line.contents)

# =============== Main conversion function ===============

def convert_file(input_path: Path) -> Exercise:
    with input_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    exo = raw_data["exercices"][0]
    html_colors = [COLOR_MAP.get(idx, "#ffff00") for idx in exo.get("couleurs", [])]
    exercise = Exercise(
        format="v1",
        instruction=parse_instruction(exo["enonce"], html_colors=html_colors),
        example=parse_example(exo.get("exemple", [])),
        hint=None,
        statement=parse_statement(raw_data.get("pages", []), html_colors=html_colors),
        reference=None
    )

    clean_exercise_whitespace(exercise)
    simplify_formatted_blocks(exercise)
    return exercise