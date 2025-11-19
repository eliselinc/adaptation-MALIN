# adaptation-MALIN

## Adaptation → [adapt](https://github.com/eliselinc/adaptation-MALIN/tree/main/adapt)

Adaptation d'un exercice de manuel scolaire en sa version adaptée avec les LLM (API Mistral ou Gemini).

## Conversion → [convert](https://github.com/eliselinc/adaptation-MALIN/tree/main/convert)

Conversion d'un exercice adapté d'une version à l'autre.


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
MISTRAL_API_KEY=your_mistral_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```