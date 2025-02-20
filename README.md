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

2. Initial prompts: Save your initial prompts as text files in the ‘prompts’ directory.

3. Run the adaptation script:
```bash
python3 main.py <mistral|pixtral> <adaptation_type> <exercise_id>
```
Examples:
```bash
python3 main.py mistral CacheIntrus adrien_p66ex2

python3 main.py mistral EditPhrase magnardCE2_p25ex5

python3 main.py mistral RCCadre magnardCE2_p51_ex6
```

Available models:
- "mistral": This will automatically call the ‘mistral-small-latest’ model (default).
- "pixtral": This will automatically call the ‘pixtral-12b-2409’ model, which supports multimodal text-image input.

More models: [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)

4. Output data:
- The output is stored in the ‘html_display’ directory. (e.g. ‘magnardCE2_p19ex5.html’)
- Navigate to this directory and open your file in a browser to display the adapted exercise.
