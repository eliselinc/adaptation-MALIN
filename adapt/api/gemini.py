import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from PIL import Image

load_dotenv()

class GeminiAPI:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment.")
        self.client = genai.Client(api_key=api_key)

    def process_adaptation(
            self,
            model: str,
            first_prompt: str,
            input_image: Image.Image = None, 
            input_text: str = "",
            format: str = "html",
            examples: list[tuple[str, str]] | None = None,
    ) -> str:

        # SYSTEM MESSAGE 
        first_message = types.Content(
            role="user", #! "system" n'existe pas dans cette version
            parts=[types.Part(text=first_prompt)]
        )

        if format == "html":
            user_prompt_text = "Adapt this exercise into clean, raw HTML content:\n"
            user_prompt_text = "Adapte cet exercice en contenu HTML brut et propre suivant les instructions:\n"
        elif format == "json":
            user_prompt_text = "Adapt this exercise into clean, raw JSON content:\n"
            user_prompt_text = "Adapte cet exercice en contenu JSON brut et propre suivant les instructions:\n"
        else:
            raise ValueError(f"Unknown format: {format} ; must be 'html' or 'json'.")

        # FEW-SHOT CONSTRUCTION
        fewshot_messages = []
        if examples:
            for input, output in examples:
                fewshot_messages.extend([
                    types.Content(
                        role="user",
                        parts=[types.Part(text=f"{user_prompt_text}{input}")]
                    ),
                    types.Content(
                        role="model",
                        parts=[types.Part(text=json.dumps(output, ensure_ascii=False))]
                    )
                ])

        #TODO vision model ?

        # MESSAGE SEQUENCE
        messages = [first_message] + fewshot_messages

        # CALL MODEL
        chat = self.client.chats.create(
            model="gemini-2.5-flash",
            history=messages,
        )
        response = chat.send_message(f"{user_prompt_text}{input_text}")

        return response.text