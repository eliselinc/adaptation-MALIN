# adaptation-MALIN

Adaptation d'un exercice de manuel scolaire en sa version HTML adaptée en utilisant l'API Mistral.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/eliselinc/adaptation-MALIN.git
cd adaptation-MALIN
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Mistral API key:
```bash
nano .env
```
```
MISTRAL_API_KEY=your_api_key_here
```

## Running

**Commande :**
```bash
python3 main.py <mistral|pixtral> <type_adaptation> <output_format> <id_exercice>?
```

**Arguments :**

- Modèle : 
    - `mistral`: appelle le modèle `mistral-small-latest` (par défaut).
    - `pixtral`: appelle le modèle `pixtral-12b-2409` qui permet un input multimodal texte-image.

    Spécifications : [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)

- Type d'adaptation : récupère le prompt spécifique au format et au type d'adaptation demandé : `./prompts_<format>/<type_adaptation>.txt`

- Format de sortie souhaité : `html` ou `json`

- Exercice à donner en entrée (argument facultatif) : 
    - récupère le fichier d'entrée texte `./input/<type_adaptation>/<id_exercice>.txt`
    - si utilisation du modèle vision pixtral, récupère le fichier d'entrée  PDF rogné sur l'exercice `./input/<type_adaptation>/<id_exercice>.pdf`

    Si aucun id n'est spécifié : traite automatiquement tous les exercices du répertoire `./input/<type_adaptation>/` (`*.txt` pour tous, et `*.pdf` si pixtral)

**Sortie :**

Selon le format demandé :
- Sortie HTML : `./output_html/<type_adaptation>/<id_exercice>.html`
- Sortie JSON : `./output_json/<type_adaptation>/<id_exercice>.json`

**Exemples d'exécution :**
```bash
python3 main.py mistral CM json

python3 main.py mistral CacheIntrus html

python3 main.py mistral CacheIntrus html adrien_p66ex2

python3 main.py mistral EditPhrase html magnardCE2_p25ex5

python3 main.py mistral RCCadre html magnardCE2_p51_ex6```
