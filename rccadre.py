# HTML - exercice utilisé comme référence : magnardCE2_p49ex7

from PIL import Image

def process_rccadre(mistral_model: str, # mistral ou pixtral
                    mistral_client,
                    exercise_image: Image.Image, 
                    exercise_text: str) -> str:
    
    first_message = {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are a textbook exercise adaptation assistant. Your task is to adapt a "fill in the sentences" exercise:
                                1. This is a reference example of an adapted exercise in HTML format:
                                    "<div id="enonce" data-classes="lc" class="lc exo0">
                                        <span class="mot lc">Écris</span><span class='space'> </span><span class="mot lc">les</span><span class='space'> </span><span class="mot lc">verbes</span><span class='space'> </span><span class="mot lc">au</span><span class='space'> </span><span class="mot lc">présent.</span><br/>
                                    </div>
                                    <div id="toutes_pages">
                                        <div class="page id_Exo_texte_raccourcis exo0 " id="p1" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="152685"/>
                                            <div class="contenu_page">
                                                <span class="mot lc">a.</span><span class='space'> </span><span class="ctn fond_couleur boite"><span class="mot lc">tester</span></span><br/>
                                                <span class="mot lc">Nous</span><span class='space'> </span><div data-mvt="champ" contentEditable="true" class=" mot champ managed_var lc" id="ix0-1" ></div><span class='space'> </span><span class="mot lc">une</span><span class='space'> </span><span class="mot lc">nouvelle</span><span class='space'> </span><span class="mot lc">formule</span><span class='space'> </span><span class="mot lc">magique.</span>
                                            </div>
                                        </div>
                                        <div class="page id_Exo_texte_raccourcis exo0 " id="p2" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="152685"/>
                                            <div class="contenu_page">
                                                <span class="mot lc">b.</span><span class='space'> </span><span class="ctn fond_couleur boite"><span class="mot lc">fermer</span></span><span class='space'> </span><span class="ctn fond_couleur boite"><span class="mot lc">froncer</span></span><br/>
                                                <span class="mot lc">Nous</span><span class='space'> </span><div data-mvt="champ" contentEditable="true" class=" mot champ managed_var lc" id="ix0-2" ></div><span class='space'> </span><span class="mot lc">les</span><span class='space'> </span><span class="mot lc">yeux</span><span class='space'> </span><span class="mot lc">et</span><span class='space'> </span><div data-mvt="champ" contentEditable="true" class=" mot champ managed_var lc" id="ix0-3" ></div><span class='space'> </span><span class="mot lc">très</span><span class='space'> </span><span class="mot lc">fort</span><span class='space'> </span><span class="mot lc">les</span><span class='space'> </span><span class="mot lc">sourcils.</span>
                                            </div>
                                        </div>
                                        <div class="page id_Exo_texte_raccourcis exo0 " id="p3" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="152685"/>
                                            <div class="contenu_page">
                                                <span class="mot lc">c.</span><span class='space'> </span><span class="ctn fond_couleur boite"><span class="mot lc">chanter</span></span><br/>
                                                <span class="mot lc">Tu</span><span class='space'> </span><div data-mvt="champ" contentEditable="true" class=" mot champ managed_var lc" id="ix0-4" ></div><span class='space'> </span><span class="mot lc">le</span><span class='space'> </span><span class="mot lc">mot</span><span class='space'> </span><span class="mot lc">magique</span><span class='space'> </span><span class="mot lc">«</span><span class='space'> </span><span class="mot lc">papla-ouva</span><span class='space'> </span><span class="mot lc">».</span>
                                            </div>
                                        </div>
                                        <div class="page id_Exo_texte_raccourcis exo0 " id="p4" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="152685"/>
                                            <div class="contenu_page">
                                                <span class="mot lc">d.</span><span class='space'> </span><span class="ctn fond_couleur boite"><span class="mot lc">murmurer</span></span><span class='space'> </span><span class="ctn fond_couleur boite"><span class="mot lc">s’user</span></span><br/>
                                                <span class="mot lc">Et</span><span class='space'> </span><span class="mot lc">moi,</span><span class='space'> </span><span class="mot lc">je</span><span class='space'> </span><div data-mvt="champ" contentEditable="true" class=" mot champ managed_var lc" id="ix0-5" ></div><span class='space'> </span><span class="mot lc">:</span><span class='space'> </span><span class="mot lc">«</span><span class='space'> </span><span class="mot lc">Abracadabra</span><span class='space'> </span><span class="mot lc">!</span><span class='space'> </span><span class="mot lc">Que</span><span class='space'> </span><span class="mot lc">les</span><span class='space'> </span><span class="mot lc">sucettes</span><span class='space'> </span><span class="mot lc">ne</span><span class='space'> </span><div data-mvt="champ" contentEditable="true" class=" mot champ managed_var lc" id="ix0-6" ></div><span class='space'> </span><span class="mot lc">plus</span><span class='space'> </span><span class="mot lc">!</span><span class='space'> </span><span class="mot lc">»</span>
                                            </div>
                                        </div>
                                    </div>"
                                2. If the statement consists of a block text, split the exercise into sentences. Else, identify the numbered sentences.
                                3. For each sentence, carefully identify:
                                    - The missing part.
                                    - The item that need to be changed to complete the sentence.
                                    - Sometimes, there are mutiple missing parts but it's explicitly stated in the statement.
                                4. Transform the exercise into its adapted HTML version.
                                    - First, display the ITEM(s) that need to be changed to complete the sentence (<span class="ctn fond_couleur boite">).
                                    - On a new line, display the SENTENCE with the missing part(s) as EDITABLE FRAME(s).
                                5. Rephrase the instruction (div id=enonce) according to the new interaction process. E.g.:
                                    - Do NOT use "mots entre parenthèse".
                                    - Do NOT use "Ecris/Recopie le texte/les phrases".
                                6. Use approriate educational content in the statement:
                                    - Do NOT forget the bullet number/letter if there is one. Do NOT add bullets if the original statement is a block text.
                                    - Do NOT modify the non-editable text, including pronouns and determiners such as "le", "des", "m'" etc.
                                    - Do NOT add new missing parts.
                                    - Do NOT solve the exercise.
                                7. Use appropriate HTML syntax:
                                    - Process all sentences, 1 element corresponds to 1 HTML page.
                                    - Do NOT modify attributes.
                                    - Do NOT modify class ids.
                                    - It must contain 2 full <div> tags.
                                8. Return ONLY the raw HTML content without any formatting markers or metadata.
                                """
                            }
                        ]
                    }
    
    # Automate the adaptation of the exercice using Mistral small language model (text-only)
    if mistral_model == "mistral":
    
        messages = [first_message,
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Adapt this exercise into clean, raw HTML content.
                                {exercise_text}"""
                            },
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
                                "text": f"""Adapt this exercise into clean, raw HTML content.
                                {exercise_text}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{exercise_image}"
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