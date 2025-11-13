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

**Command**
```bash
python3 convert/convert.py <input_repository> <input_format>
```

**Arguments**

- Input repository : one textbook repository or file
- Input format : `cartable` or `patty` or `html`

**Cases**
- If `cartable`: 
  - The input folder contains a `json` subfolder with Cartable .js exercises
  - Outputs:
    - Individual Patty JSON files: `./<textbook>/json_patty/*.json`
    - Individual Patty HTML files: `./<textbook>/html_patty/*.html`
    - Global textbook HTML file:`./<textbook>/html_patty/<textbook>.html`
- If `patty`: 
  - The input folder contains a `json_patty` folder with Patty .json exercises
  - Outputs:
    - Individual Patty HTML files: `./<textbook>/html_patty/*.html`
    - Global textbook HTML file:`./<textbook>/html_patty/<textbook>.html`
- If None: 
  - Input is the independant HTML textbook file in Patty format
  - Output:
    - Individual Patty JSON files: `./<textbook>/json_patty/*.json`

**Example**

```bash
python3 convert/convert.py ../data/manuel_CM1_francais cartable
```

```bash
python3 convert/convert.py ../data/manuel_CM1_francais/textbook.html html
```
