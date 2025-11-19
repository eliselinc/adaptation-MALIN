import base64
import io
import re
from bs4 import BeautifulSoup, NavigableString
from PIL import Image

# from mistral import get_stars

def image_to_base64(image:Image.Image, max_size:tuple=(600,800)) -> str:
    """Optimized image processing with efficient resizing and compression"""
    width, height = image.size
    aspect_ratio = width / height
    
    # Calculate target dimensions
    if width > max_size[0] or height > max_size[1]:
        if aspect_ratio > 1:
            new_width = min(width, max_size[0])
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(height, max_size[1])
            new_width = int(new_height * aspect_ratio)
        
        image = image.resize((new_width, new_height), Image.Resampling.BILINEAR)
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=75, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode()


def custom_pretty_print(soup, indent_level=3, indent_size=4):
    """Custom pretty print function to format HTML with specific rules for <div> tags."""
    indent = ' ' * (indent_level * indent_size)
    formatted_html = ''
    first_not_div = True
    void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    for child in soup.contents:
        if isinstance(child, NavigableString):
            # Add text content without additional indentation
            formatted_html += child.rstrip()
        elif child.name == 'div':
            # Check for the special attribute
            if child.get('data-mvt') == 'champ': # RCCadre champ sur la même ligne
                # Handle <div> with data-mvt="champ" without new line
                formatted_html += f'<{child.name}'
                for attr, value in child.attrs.items():
                    if isinstance(value, list):
                        formatted_html += f' {attr}="{" ".join(value)}"'
                    else:
                        formatted_html += f' {attr}="{value}"'
                formatted_html += '>'

                # Check if the div has only text content and no children tags
                if len(child.contents) == 1 and isinstance(child.contents[0], NavigableString):
                    formatted_html += child.contents[0].strip()
                    formatted_html += f'</{child.name}>'
                else:
                    formatted_html += custom_pretty_print(child, indent_level, indent_size)
                    formatted_html += f'</{child.name}>'
            else:
                # Add opening <div> tag with indentation
                formatted_html += f'\n{indent}<{child.name}'
                for attr, value in child.attrs.items():
                    if isinstance(value, list):
                        # Join list values into a space-separated string
                        formatted_html += f' {attr}="{" ".join(value)}"'
                    else:
                        formatted_html += f' {attr}="{value}"'
                formatted_html += '>'
                # Check if the div has only text content and no children tags
                if len(child.contents) == 1 and isinstance(child.contents[0], NavigableString):
                    formatted_html += child.contents[0].strip()
                    formatted_html += f'</{child.name}>'
                else:
                    # Recursively format child elements with increased indentation
                    formatted_html += custom_pretty_print(child, indent_level + 1, indent_size)
                    formatted_html += f'\n{indent}</{child.name}>'
        elif child.name in void_elements:
            # Handle void elements (self-closing tags)
            formatted_html += f'\n{indent}<{child.name}'
            for attr, value in child.attrs.items():
                if isinstance(value, list):
                    formatted_html += f' {attr}="{" ".join(value)}"'
                else:
                    formatted_html += f' {attr}="{value}"'
            formatted_html += ' />'
        else:
            if first_not_div:
                # First non-div tag goes to a new line
                formatted_html += f'\n{indent}<{child.name}'
                for attr, value in child.attrs.items():
                    if isinstance(value, list):
                        # Join list values into a space-separated string
                        formatted_html += f' {attr}="{" ".join(value)}"'
                    else:
                        formatted_html += f' {attr}="{value}"'
                formatted_html += f'>{child.decode_contents()}</{child.name}>'
                first_not_div = False
            else:
                # Subsequent non-div tags stay on the same line without extra spaces
                formatted_html += f'<{child.name}'
                for attr, value in child.attrs.items():
                    if isinstance(value, list):
                        # Join list values into a space-separated string
                        formatted_html += f' {attr}="{" ".join(value)}"'
                    else:
                        formatted_html += f' {attr}="{value}"'
                formatted_html += f'>{child.decode_contents()}</{child.name}>'

    return formatted_html

def pretty_print_divs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    pretty_html = custom_pretty_print(soup)
    return pretty_html

def get_page_and_exercise_numbers(ex_id:str) -> str:
    pattern = re.compile(r'[Pp](\d+)[Ee][Xx](\d+)', re.IGNORECASE)

    match = pattern.search(ex_id)

    if match:
        page_number = match.group(1)
        exercise_number = match.group(2)
        return page_number, exercise_number
    else:
        print(f"!!! WARNING: Numéros de page et d'exercice non trouvés pour le fichier '{ex_id}'. Renommez le fichier input suivant le format: '<manuel>_p<numero-de-page>ex<numero-d-exercice>.txt'")
        return None, None

def get_id_cahier(ex_id:str) -> str:
    isbn_dict = {
        "magnardce1":"978-2-210-50537-7", "outilspourlefrancaisce1":"978-2-210-50537-7",
        "magnardce2":"978-2-210-50538-4", "outilspourlefrancaisce2":"978-2-210-50538-4",
        "magnardcm1":"978-2-210-50535-3", "outilspourlefrancaiscm1":"978-2-210-50535-3",
        "magnardcm2":"978-2-210-50536-0", "outilspourlefrancaiscm2":"978-2-210-50536-0",
        "adrien":"978-2-210-50208-6", "adrian":"978-2-210-50208-6",
        "hachettece2":"2016272090", "aporteedemotsce2":"2016272090",
    }

    try:
        isbn = isbn_dict[re.sub(r'[^a-z0-9]', '', ex_id.split("_")[0].lower())]
    except KeyError:
        isbn = ""
        print(f"!!! WARNING: ISBN non trouvé pour le fichier '{ex_id}'. Renommez le fichier input suivant le format: '<manuel>_p<numero-de-page>ex<numero-d-exercice>.txt'")

    page_number, ex_number = get_page_and_exercise_numbers(ex_id)
    
    return f"{isbn}_P{page_number}Ex{ex_number}"

def get_title(ex_id: str, ex_text:str, ex_html:str) -> str:

    page_number, ex_number = get_page_and_exercise_numbers(ex_id)
    return f"P{page_number}Ex{ex_number}"
    # TODO : ajouter les étoiles
    stars = get_stars(ex_html=ex_html,
                      ex_text=ex_text)
    return f"P{page_number}Ex{ex_number}{stars}"

def wrap_html(content:str, title:str, id_cahier:str) -> str:
    if content.startswith("```html") and content.endswith("```"):
        content = content[7:-3].strip()
    if content.startswith("```") and content.endswith("```"):
        content = content[3:-3].strip()
    if not content.startswith("<div"):
        print("ERREUR DEBUT DU CODE HTML utils.wrap_html")
    if not content.rstrip().endswith("</div>"):
        print("ERREUR FIN DU CODE HTML utils.wrap_html")

    soup = BeautifulSoup(content, 'html.parser')
    nb_derniere_page = len(soup.find('div', id='toutes_pages').find_all('div', recursive=False)) if soup.find('div', id='toutes_pages') else 1

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>{title}</title> 
    <script src="communs/jquery.js" type="text/javascript" language="javascript"></script>
    <link rel="stylesheet" href="communs/classe_cahier.css" />
    <script type="text/javascript" language="javascript"> var id_cahier = "{id_cahier}";</script>
    <script src="communs/jquery.textnodes.js" type="text/javascript" language="javascript"></script>
    <script src="communs/reglages_locaux.js" type="text/javascript" language="javascript"></script>
    <script src="communs/classe_cahier.js" type="text/javascript" language="javascript"></script>
    <link rel="stylesheet" href="communs/classe_exercice.css" />
    <script src="communs/jquery.selection.js" type="text/javascript" language="javascript"></script>
    <script src="communs/classe_exercice.js" type="text/javascript" language="javascript"></script>
    <style type="text/css" title="text/css">.exo0 .sel1{{ background:#000000; }}#print .exo0 .sel1{{ border-color:#000000; }}.exo0 .sel2{{ background:#FFC0CB; }}#print .exo0 .sel2{{ border-color:#FFC0CB; }}.exo0 .sel3{{ background:#bbbbff; }}#print .exo0 .sel3{{ border-color:#bbbbff; }}.exo0 .sel4{{ background:#bbffbb; }}#print .exo0 .sel4{{ border-color:#bbffbb; }}.exo0 .sel5{{ background:#bbbbbb; }}#print .exo0 .sel5{{ border-color:#bbbbbb; }}</style>
    <script type="text/javascript" language="javascript"> liste_exercices[0] = {{ id_exo: "exo0", id_type: "id_Exo_mots_a_cocher", couleurs: [11,4,7,8,5], appliquer_couleur_texte: 1, print: 1 }};</script>
    <link rel="stylesheet" href="communs/reglages_locaux.css" type="text/css" media="all">
</head>
<body>
    <input type="hidden" name="id_cahier_db" class="id_cahier_db" value="96065"/>
	<div id="page_exo">
		<div id="cleft"><button id="bleft">&lt;</button></div>
		<div id="cright"><button id="bright">&gt;</button></div>
		<!-- BLOC CENTRAL -->
		<div id="bloc_central">
{pretty_print_divs(content).rstrip().rstrip('</div>')}
				<!-- DERNIÈRE PAGE -->
				<div class="page pagefin" id="p{nb_derniere_page+1}">
					<div style="display:none;" class="enonce"></div>
					<div><button class="cahier_bouton_fin" id="cahier_bouton_imprimer" type="button">Imprimer</button></div>
					<div id="print"></div>
					<div><button class="cahier_bouton_fin" id="cahier_bouton_fermer" type="button">Quitter l'exercice</button></div>
					<div><button class="cahier_bouton_fin" id="cahier_bouton_revenir" type="button">Revenir au début de l'exercice</button></div>
					<div><button class="cahier_bouton_fin" id="cahier_bouton_reset" type="button">Effacer mes réponses</button></div>
					<div id="debug"></div>
					<div id="mention_developpe_footnote">Exercices réalisés avec la plateforme des cahiers intéractifs du Cartable Fantastique (laboratoire INSERM/CEA Unicog, www.cartablefantastique.fr).<br/>Ces adaptations ont été approuvées par l'équipe du Cartable Fantastique.</div>
				</div>
			</div>
			<!-- FIN TOUTES PAGES -->
			<div id="bottom">
				<button id="fleche"><img src="communs/fleche-jaune.png" /></button>
				<button id="oups" title="effacer mes modifications" onclick="reset_cette_page()">OUPS</button>
			</div>
		</div><!-- fin bloc central -->

	</div><!-- fin de page_exo -->
		
	<div id="outer" style="display:none;"></div>
	<div id="loading"><img src="communs/loading-large.gif" /></div>
</body>
</html>
"""