# Adapdation

Adaptation d'un exercice de manuel scolaire en sa version adaptée avec les LLM (API Mistral ou Gemini).

Deux formats d'adaptation :
- HTML (ancienne version Les Cahiers Fantastiques) 
- JSON (nouvelle version MALIN)

Deux modes :
- One shot
- Few-shot (*en cours d'implémentation*)

## Running

**Commande**
Dans `adaptation-MALIN` :
```bash
python3 adapt/main.py <mistral|pixtral> <type_adaptation> <output_format> <id_exercice>?
```

**Arguments**

- Modèle : 
    - `mistral`: appelle le modèle `mistral-small-latest` (par défaut).
    - `pixtral`: appelle le modèle `pixtral-12b-2409` qui permet un input multimodal texte-image.

    Spécifications : [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)
    - `gemini` (et autres) *en cours d'implémentation*

- Type d'adaptation : récupère le prompt spécifique au format et au type d'adaptation demandé : `adapt/prompts_<format>/<type_adaptation>.txt`

- Format de sortie souhaité : `html` ou `json`

- Exercice à donner en entrée (argument facultatif) : 
    - récupère le fichier d'entrée texte `adapt/input/<type_adaptation>/<id_exercice>.txt`
    - si utilisation du modèle vision pixtral, récupère le fichier d'entrée  PDF rogné sur l'exercice `adapt/input/<type_adaptation>/<id_exercice>.pdf`

    Si aucun id n'est spécifié : traite automatiquement tous les exercices du répertoire `adapt/input/<type_adaptation>/` (`*.txt` pour tous, et `*.pdf` si pixtral)

**Sortie**

Selon le format demandé :
- Sortie HTML : `adapt/output_html/<type_adaptation>/<id_exercice>.html`
- Sortie JSON : `adapt/output_json/<type_adaptation>/<id_exercice>.json`

**Exemples d'exécution**

```bash
python3 adapt/main.py mistral CM json

python3 adapt/main.py mistral CacheIntrus html

python3 adapt/main.py mistral CacheIntrus html adrien_p66ex2

python3 adapt/main.py mistral EditPhrase html magnardCE2_p25ex5

python3 adapt/main.py mistral RCCadre html magnardCE2_p51_ex6```
