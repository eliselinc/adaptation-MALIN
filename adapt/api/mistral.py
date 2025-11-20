import os
from dotenv import load_dotenv
from mistralai import Mistral
from pydantic import BaseModel
from PIL import Image

load_dotenv()

# class AdaptationResponse(BaseModel):
#     html_content: str

class MistralAPI:
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("Missing MISTRAL_API_KEY in environment.")
        self.client = Mistral(api_key=api_key)

    def process_adaptation(
            self,
            model: str,
            first_prompt: str,
            input_image: Image.Image, 
            input_text: str,
            format: str,
            examples: list[tuple[str, str]] | None = None,
    ) -> str:

        # SYSTEM MESSAGE
        first_message = {
                            "role": "system",
                            "content": [
                                {
                                    "type": "text",
                                    "text": first_prompt
                                }
                            ]
                        }

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
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"{user_prompt_text}{input}"}
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": f"{output}"}
                        ],
                    }
                ])

        # USER MESSAGE
        target_user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"{user_prompt_text}{input_text}" 
                    # TODO tester si l'envoi de l'exercice en 2e input texte a une influence
                }
            ]
        }

        # If vision model, attach image
        if model == "pixtral":
            # encode image ?
            target_user_message["content"].append(
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{input_image}"
                }
            )
        
        # MESSAGE SEQUENCE
        messages = [first_message] + fewshot_messages + [target_user_message]

        # CALL MODEL
        if model == "mistral":
            response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                # max_tokens=4000
            )
        elif model == "pixtral":
            response = self.client.chat.complete(
                model="pixtral-12b-2409",
                messages=messages,
            )
        else:
            raise ValueError(f"Unknown model: {model} ; must be 'mistral' or 'pixtral'.")
        
        return response.choices[0].message.content