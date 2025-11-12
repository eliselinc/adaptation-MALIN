# Conversion

Convert adapted exercises or textbooks

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

## Running

**Commande :**
```bash
python3 convert/convert.py <input_repository> <input_format>
```

**Arguments :**

- Input repository : one textbook repository
- Input format : `cartable` or `patty`

If `cartable`, the input folder contains a `json` subfolder with Cartable .js exercises ; else if `patty`, the input folder contains a `json_patty` folder with Patty .json exercises

**Output :**

For each input textbook:
- Individual Patty JSON files: `./<textbook>/json_patty/*.json` (if input_format = `cartable`)
- Individual Patty HTML files: `./<textbook>/html_patty/*.html`
- Global textbook HTML file:`./<textbook>/html_patty/<textbook>.html`

**Exemple d'exécution :**

```bash
python3 convert/convert.py ../data/manuel_CM1_francais cartable
```
