import os
import sys
import requests
import json
from dotenv import load_dotenv
from pdfminer.high_level import extract_text

# Charger les variables d'environnement
load_dotenv()

# Charger la clé API
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("La clé API MISTRAL n'est pas définie dans les variables d'environnement.")

# Vérifier que l'utilisateur a fourni un argument
if len(sys.argv) < 2:
    raise ValueError("Veuillez fournir le nom du fichier PDF en argument. Exemple : py extraction.py ex.pdf")

# Récupérer le nom du fichier PDF
pdf_name = sys.argv[1]

# Construire les chemins des fichiers
script_dir = os.path.dirname(os.path.abspath(__file__))  # Dossier du script
pdf_file = os.path.join(script_dir, pdf_name)
input_file = os.path.join(script_dir, "input.txt")
prompt_file = os.path.join(script_dir, "prompt.txt")

# Vérifier si le fichier PDF existe
if not os.path.exists(pdf_file):
    raise FileNotFoundError(f"Erreur : le fichier {pdf_name} n'existe pas dans {script_dir}")

# Extraire le texte du PDF
pdf_text = extract_text(pdf_file).strip()

if not pdf_text:
    raise ValueError(f"Erreur : impossible d'extraire du texte depuis {pdf_name}")

# Sauvegarder le texte extrait dans input.txt
with open(input_file, "w", encoding="utf-8") as f:
    f.write(pdf_text)

# Lire le contenu de prompt.txt
try:
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_content = f.read().strip()
except FileNotFoundError:
    raise FileNotFoundError(f"Erreur : le fichier 'prompt.txt' est introuvable dans {script_dir}")

# Préparer le message pour Mistral
messages = [
    {"role": "system", "content": prompt_content},
    {"role": "user", "content": pdf_text}
]

# Définir l'URL de l'API Mistral
API_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"

# Fonction pour envoyer une requête et obtenir une réponse
def get_mistral_response(messages):
    data = {
        "model": "mistral-large-latest",
        "messages": messages
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Vérifie si la requête a échoué
        
        output = response.json()
        return output.get("choices", [{}])[0].get("message", {}).get("content", "Aucune réponse trouvée.")

    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la requête API : {e}"

# Faire trois expériences et stocker les résultats
experiments = [get_mistral_response(messages) for _ in range(3)]

# Préparer un prompt pour l'arbitrage en incluant les instructions originales
arbitrage_prompt = f"""
Voici le prompt d'origine qui définit comment extraire les exercices :

Nous avons obtenu trois extractions différentes à partir du même document. Compare-les et choisis la meilleure en respectant les critères suivants :
- Conformité aux consignes
- Qualité et fidélité du format
- Absence d'erreurs ou d'omissions
- Respect du format JSON strict

Voici les trois versions :

1️⃣ {experiments[0]}

2️⃣ {experiments[1]}

3️⃣ {experiments[2]}

**Donne uniquement la meilleure réponse en respectant le format JSON.** Ne donne pas d'explication.
"""

# Envoyer la requête d'arbitrage
arbitrage_messages = [
    {"role": "system", "content": "Tu es un expert en extraction de texte structuré."},
    {"role": "user", "content": arbitrage_prompt}
]

best_result = get_mistral_response(arbitrage_messages)

print("Meilleure extraction sélectionnée :\n", best_result)
