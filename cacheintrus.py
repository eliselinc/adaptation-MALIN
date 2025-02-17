# HTML - exercice utilisé comme référence : adrien_p16_ex2

from PIL import Image

def process_cacheintrus(mistral_model: str, # mistral ou pixtral
                        mistral_client,
                        exercise_image: Image.Image, 
                        exercise_text: str) -> str:
    
    first_message = {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are a textbook exercise adaptation assistant. Your task is to:
                                1. Carefully identify the elements in the exercise.
                                2. Convert the exercise to its adapted HTML version. The adaptation consists of a "find the odd one out" exercise, where all items are presented within frames. The student must identify the word that does not belong and click on it to turn it black.
                                3. Use approriate educational content:
                                    - Rephrase the instruction according to the example and the new interaction process.
                                    - Do NOT modify the items in the exercice statement. One item in the list may contain multiple words (eg "la fleur", "il mange une pomme" are single items). 
                                    - Process all lists, 1 list corresponds to 1 HTML page.
                                    - Do NOT solve the exercise.
                                4. The format must be similar to this adapted exercise:
                                    "<div id="enonce" data-classes="lc" class="lc exo0">
                                        <span class="mot lc">Dans</span><span class='space'>  </span><span class="mot lc">chaque</span><span class='space'>  </span><span class="mot lc">liste,</span><span class='space'>  </span><span class="mot lc">un</span><span class='space'>  </span><span class="mot lc">mot</span><span class='space'>  </span><span class="mot lc">n’est</span><span class='space'>  </span><span class="mot lc">pas</span><span class='space'>  </span><span class="mot lc">un</span><span class='space'>  </span><span class="mot lc">verbe.</span><span class='space'>  </span><span class="mot lc">Cache</span><span class='space'>  </span><span class="mot lc">le.</span>
                                    </div>
                                    <div id="toutes_pages">
                                        <div class="page id_Exo_mots_a_cocher exo0 " id="p1" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="148436"/>
                                            <div class="contenu_page">
                                                <span data-mvt="coche" class="coche 2colors managed_var" id="ix0-1"><span class="mot lc">a.</span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-2"><span class="ctn fond_couleur boite"><span class="mot lc">parler</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-3"><span class="ctn fond_couleur boite"><span class="mot lc">voir</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-4"><span class="ctn fond_couleur boite"><span class="mot lc">poirier</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-5"><span class="ctn fond_couleur boite"><span class="mot lc">dire</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-6"><span class="ctn fond_couleur boite"><span class="mot lc">saluer</span></span></span>
                                            </div>
                                        </div>
                                        <div class="page id_Exo_mots_a_cocher exo0 " id="p2" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="148436"/>
                                            <div class="contenu_page">
                                                <span data-mvt="coche" class="coche 2colors managed_var" id="ix0-7"><span class="mot lc">b.</span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-8"><span class="ctn fond_couleur boite"><span class="mot lc">finir</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-9"><span class="ctn fond_couleur boite"><span class="mot lc">finale</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-10"><span class="ctn fond_couleur boite"><span class="mot lc">parier</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-11"><span class="ctn fond_couleur boite"><span class="mot lc">cuire</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-12"><span class="ctn fond_couleur boite"><span class="mot lc">aller</span></span></span>
                                            </div>
                                        </div>
                                        <div class="page id_Exo_mots_a_cocher exo0 " id="p3" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="148436"/>
                                            <div class="contenu_page">
                                                <span data-mvt="coche" class="coche 2colors managed_var" id="ix0-13"><span class="mot lc">c.</span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-14"><span class="ctn fond_couleur boite"><span class="mot lc">courir</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-15"><span class="ctn fond_couleur boite"><span class="mot lc">entendre</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-16"><span class="ctn fond_couleur boite"><span class="mot lc">revoir</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-17"><span class="ctn fond_couleur boite"><span class="mot lc">suivre</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-18"><span class="ctn fond_couleur boite"><span class="mot lc">arrosoir</span></span></span>
                                            </div>
                                        </div>
                                        <div class="page id_Exo_mots_a_cocher exo0 " id="p4" data-exo="0">
                                            <input type="hidden" name="id_exo_db" class="id_exo_db" value="148436"/>
                                            <div class="contenu_page">
                                                <span data-mvt="coche" class="coche 2colors managed_var" id="ix0-19"><span class="mot lc">d.</span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-20"><span class="ctn fond_couleur boite"><span class="mot lc">verre</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-21"><span class="ctn fond_couleur boite"><span class="mot lc">dormir</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-22"><span class="ctn fond_couleur boite"><span class="mot lc">changer</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-23"><span class="ctn fond_couleur boite"><span class="mot lc">mettre</span></span></span><span class='space'>  </span><span data-mvt="coche" class="coche 2colors managed_var" id="ix0-24"><span class="ctn fond_couleur boite"><span class="mot lc">cirer</span></span></span>
                                            </div>
                                        </div>
                                    </div>"
                                5. Use appropriate HTML syntax:
                                    - Do NOT modify attributes.
                                    - Do NOT modify class ids.
                                    - Attributes must be strings separated by spaces, not lists.
                                    - Every div tag must be closed.
                                    - It must contain 2 full <div> tags.
                                6. Return ONLY the raw HTML content without any formatting markers or metadata.
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
                            # TODO tester si l'envoi de l'exercice en 2e input texte a une influence
                            # {
                            #     "type": "text",
                            #     "text": exercise_text
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