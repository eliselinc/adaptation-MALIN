# Adapdation

Adaptation d'un exercice de manuel scolaire en sa version adaptée selon sa catégorie d'adaptation, avec les LLM (API Gemini ou Mistral).

Deux formats d'adaptation :
- HTML (ancienne version Les Cahiers Fantastiques du Cartable Fantastique)
- JSON (nouvelle version MALIN)

Mode :
- Few-shot si des exercices "exemples" sont saisis dans `adapt/prompts_json/examples<categorie_d_adaptation>.json`
- Sinon zero-shot (ou one-shot avec un exemple intégré au prompt)

## Running

**Commande**
Dans `adaptation-MALIN` :
```bash
python3 adapt/main.py <model> <adaptation_type> <output_format> --ex_id <ex_id>? --ex_path <ex_path>? 
```

**Arguments**

- Modèle : 
    - `mistral` : appelle le modèle `mistral-small-latest`
    - `pixtral` : appelle le modèle `pixtral-12b-2409` qui permet un input multimodal texte-image

    Spécifications : [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)
    - `gemini` : appelle le modèle `gemini-2.5-flash`
- Format de sortie souhaité : `html` ou `json`
- Type d'adaptation : récupère le prompt spécifique au format et au type d'adaptation demandé : `adapt/prompts_<format>/<adaptation_type>.txt` ainsi que les exemples dans la clé associée dans `adapt/prompts_json/examples.json`
- Exercice à donner en entrée (argument facultatif) : 
    - récupère le fichier d'entrée texte `<ex_path>/<adaptation_type>/<ex_id>.txt` (par défaut `ex_path=='./exercices'`)
    - si utilisation du modèle vision pixtral, récupère le fichier d'entrée  PDF rogné sur l'exercice `<ex_path>/<adaptation_type>/<ex_id>.pdf`

    Si aucun id n'est spécifié : traite automatiquement tous les exercices du répertoire `<ex_path>/<adaptation_type>` (fichiers `*.txt` ; et `*.pdf` si modèle multimodal)

**Sortie**

Selon le format demandé :
- Arg `html` : Sortie HTML Cartable : `<ex_path>/<adaptation_type>/html/<ex_id>.html`
- Arg `json` : Sortie JSON MALIN : `<ex_path>/<adaptation_type>/json_malin/<ex_id>.json` puis converti en HTML MALIN dans `<ex_path>/<adaptation_type>/html_malin/<ex_id>.html`

**Exemples d'exécution**

```bash
python3 adapt/main.py gemini CM json                              # Traite tous les exercices dans exercices/CM en adaptation JSON MALIN avec Gemini

python3 adapt/main.py mistral CM json --ex_path exos              # Traite tous les exercices dans exos/CM en adaptation JSON MALIN avec Mistral

python3 adapt/main.py mistral CacheIntrus html                    # Traite tous les exercices dans exercices/CacheIntrus en adaptation HTML Cartable avec mistral

python3 adapt/main.py mistral CacheIntrus html --ex_id A_P66Ex2   # Traite l'exercice précis : exercices/CacheIntrus/A_P66Ex2.txt
```

**Organisation des répertoires**

Données :
```yaml
exercices                      # Répertoire global (par défaut 'exercices' à la racine de adaptation-MALIN)
├── CacheIntrus                # 1 répertoire = 1 type d'adaptation
|   ├── *.txt                  # Exercices individuels au format TXT
|   ├── *.pdf                  # Exercices individuels au format PDF (pas nécessaire sauf si modèle multimodal comme Pixtral)
|   ├── json_malin/*.json      # Répertoire contenant les fichiers adaptés en JSON MALIN
|   ├── html_malin/*.html      # Répertoire contenant les fichiers adaptés en HTML MALIN
|   └── html_cartable/*.html   # Répertoire contenant les fichiers adaptés en HTML (Cahiers Fantastiques)
├── CM
└── ... (autres types d'adaptations)
```

Prompts :
```yaml
adapt
└── prompts_json               # 1 répertoire = 1 type d'adaptation
    ├── CM.txt                 # Prompt pour la catégorie CM
    ├── examplesCM.json        # Exemples pour few-shot learning pour la catégorie CM
    ├── CacheIntrus.txt
    ├── examplesCacheIntrus.json
    └── ... (autres prompts pour les autres catégories)
```