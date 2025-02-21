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

Commande :
```bash
python3 main.py <mistral|pixtral> <type_adaptation> <id_exercice>
```

- Exercice à donner en entrée : 
    - fichier texte `./type_adaptation/id_exercice.txt`
    - (+ fichier PDF rogné sur l'exercice `./type_adaptation/id_exercice.pdf` pour l'utilisation du modèle vision pixtral).

- Prompt spécifique au type d'adaptation : `./prompts/type_adaptation.txt`

- Sortie HTML : `./html_display/id_exercice.html`

- Modèle : 
    - `mistral`: appelle le modèle `mistral-small-latest` (par défaut).
    - `pixtral`: appelle le modèle `pixtral-12b-2409` qui permet un input multimodal texte-image.
    - Spécifications : [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)

Exemples d'exécution :
```bash
python3 main.py mistral CacheIntrus adrien_p66ex2

python3 main.py mistral EditPhrase magnardCE2_p25ex5

python3 main.py mistral RCCadre magnardCE2_p51_ex6
```
