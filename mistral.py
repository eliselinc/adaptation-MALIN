import os

from dotenv import load_dotenv
from mistralai import Mistral
from pydantic import BaseModel
from PIL import Image

load_dotenv()
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

class AdaptationResponse(BaseModel):
    html_content: str

def process_adaptation(mistral_model: str,
                       first_prompt: str,
                       ex_image: Image.Image, 
                       ex_text: str,
                       format: str) -> str:

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
        user_prompt_text = "Adapt this exercise into clean, raw HTML content."
    elif format == "json":
        user_prompt_text = "Adapt this exercise into clean, raw JSON content."

    # Automate the adaptation of the exercice using Mistral small language model (text-only)
    if mistral_model == "mistral":

        messages = [first_message,
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""{user_prompt_text}
                                {ex_text}"""
                            },
                            # TODO tester si l'envoi de l'exercice en 2e input texte a une influence
                            # {
                            #     "type": "text",
                            #     "text": ex_text
                            # }
                        ]
                    }
                   ]

        response = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            max_tokens=4000
        )
    
    # Automate the adaptation of the exercice using small Pixtral vision model
    elif mistral_model == "pixtral":
    
        messages = [first_message,
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""{user_prompt_text}
                                {ex_text}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{ex_image}"
                            },
                        ]
                    }
                   ]
        
        response = mistral_client.chat.complete(
            model="pixtral-12b-2409",
            messages=messages,
            max_tokens=4000
        )
    
    return response.choices[0].message.content
