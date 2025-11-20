# Adapdation

Adaptation d'un exercice de manuel scolaire en sa version adaptée selon sa catégorie d'adaptation, avec les LLM (API Gemini ou Mistral).

Deux formats d'adaptation :
- HTML (ancienne version Les Cahiers Fantastiques) 
- JSON (nouvelle version MALIN)

Mode :
- Few-shot si des exercices "exemples" sont saisis dans `adapt/prompts_json/examples.json`
- Sinon zero-shot (ou one-shot avec un exemple intégré au prompt)

## Running

**Commande**
Dans `adaptation-MALIN` :
```bash
python3 adapt/main.py <model> <adaptation_type> <output_format> --ex_path <ex_path>? --ex_id <ex_id>?
```

**Arguments**

- Modèle : 
    - `mistral` : appelle le modèle `mistral-small-latest` (par défaut)
    - `pixtral` : appelle le modèle `pixtral-12b-2409` qui permet un input multimodal texte-image

    Spécifications : [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)
    - `gemini` : (et autres) *en cours d'implémentation*

- Type d'adaptation : récupère le prompt spécifique au format et au type d'adaptation demandé : `adapt/prompts_<format>/<adaptation_type>.txt` ainsi que les exemples dans la clé associée dans `adapt/prompts_json/examples.json`

- Format de sortie souhaité : `html` ou `json`

- Exercice à donner en entrée (argument facultatif) : 
    - récupère le fichier d'entrée texte `<ex_path>/<adaptation_type>/<ex_id>.txt`
    - si utilisation du modèle vision pixtral, récupère le fichier d'entrée  PDF rogné sur l'exercice `<ex_path>/<adaptation_type>/<ex_id>.pdf`

    Si aucun id n'est spécifié : traite automatiquement tous les exercices du répertoire `<ex_path>/<adaptation_type>` (fichiers `*.txt` ; et `*.pdf` si modèle multimodal)

**Sortie**

Selon le format demandé :
- Sortie HTML : `<ex_path>/<adaptation_type>/html/<ex_id>.html`
- Sortie JSON : `<ex_path>/<adaptation_type>/json/<ex_id>.json`

**Exemples d'exécution**

```bash
python3 adapt/main.py mistral CM json                             # Traite tous les exercices dans exercices/CM en adaptation JSON avec Mistral

python3 adapt/main.py mistral CM html --ex_path exos              # Traite tous les exercices dans exos/CM en adaptation HTML avec Mistral

python3 adapt/main.py mistral CacheIntrus html --ex_id A_P66Ex2   # Traite un exercice précis : exercices/CacheIntrus/A_P66Ex2.txt
```

**Organisation d'un répertoire (1 répertoire = 1 manuel)**

Données :
```yaml
exercices            # Répertoire global (par défaut 'exercices' à la racine de adaptation-MALIN)
|
├── CacheIntrus      # 1 répertoire = 1 type d'adaptation
|   ├── *.txt        # Exercices individuels au format TXT
|   ├── *.pdf        # Exercices individuels au format PDF (pas nécessaire sauf si modèle multimodal comme Pixtral)
|   ├── json/*.json  # Répertoire contenant les fichiers adaptés en JSON MALIN
|   ├── html/*.html  # Répertoire contenant les fichiers adaptés en HTML MALIN
|   └── cartable/*.html  # Répertoire contenant les fichiers adaptés en HTML (Cahiers Fantastiques)
├── CM
└── ... (autres types d'adaptations)
```

Prompts :
```yaml
adapt
|
└── prompts_json         # 1 répertoire = 1 type d'adaptation
    ├── CM.txt           # Prompt pour la catégorie CM
    ├── examplesCM.json  # Exemples pour few-shot learning pour la catégorie CM
    ├── CacheIntrus.txt
    ├── examplesCacheIntrus.json
    └── ... (autres prompts pour les autres catégories)
```