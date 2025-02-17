# adaptation-MALIN

Adaptation d'un exercice de manuel scolaire en sa version HTML adaptée.

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

1. Input data:
- The input exercises are stored in the ‘input’ directory, organized into subfolders by adaptation type.
- They must be stored in plain text (and cropped PDF for vision-language model).
- The file name must be the exercise identifier. (For example, ‘magnardCE2_p19ex5.pdf’ and ‘magnardCE2_p19ex5.txt’).

1. Run the adaptation script:
```bash
python3 main.py <mistral|pixtral> <adaptation_type> <exercise_id>
```

Available models:
- "mistral": This will automatically call the ‘mistral-small-latest’ model (default).
- "pixtral": This will automatically call the ‘pixtral-12b-2409’ model, which supports multimodal text-image input.

More models: [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)

Currently supported adaptation types:
- CacheIntrus
- EditPhrase
- RCDouble
- RCCadre

3. Output data:
- The output is stored in the ‘html_display’ directory. (e.g. ‘magnardCE2_p19ex5.html’)
- Navigate to this directory and open your file in a browser to display the adapted exercise.