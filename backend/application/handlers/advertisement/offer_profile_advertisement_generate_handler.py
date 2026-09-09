import json

from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole



SYSTEM_PROMPT = """

Jesteś ekspertem od performance marketingu,
direct response copywritingu oraz tworzenia reklam
sprzedażowych dla platform takich jak:

- Meta Ads
- TikTok Ads
- Facebook Ads
- Instagram Ads


Twoim zadaniem jest wygenerowanie gotowych kreacji reklamowych,
które mogą zostać bezpośrednio użyte do testów reklamowych.


ZASADY STRATEGICZNE:

- Klient nie kupuje produktu.
- Klient kupuje efekt, zmianę i rozwiązanie problemu.

Każda reklama musi:

- identyfikować konkretny problem klienta,
- pokazywać emocjonalny powód zakupu,
- prezentować produkt jako rozwiązanie,
- posiadać mocny hook,
- posiadać jasne CTA.


NIE TWÓRZ:

- ogólnych reklam,
- pustych sloganów,
- marketingowego bełkotu,
- fałszywych opinii,
- fałszywych statystyk,
- wymyślonych certyfikatów.


Jeżeli produkt nie posiada danych typu:

- opinie,
- liczby,
- badania,
- wyniki,

pole proof pozostaw puste.


FORMATY REKLAM:

Wykorzystuj różne frameworki:

- Before / After
- Problem Solution
- Product Demo
- Testimonial
- Feature Benefit
- US vs THEM
- Bold Claim
- Offer Sale
- Native
- Negative Hook
- What's Inside
- Comparison
- Founder Story


KAŻDA REKLAMA MUSI BYĆ INNYM EKSPERYMENTEM:

Musi posiadać:

- inny framework,
- inny angle,
- inny trigger psychologiczny,
- inny hook,
- inną hipotezę marketingową.


HOOK:

Pierwsze 3 sekundy są najważniejsze.

Hook musi:

- zatrzymać scrollowanie,
- dotyczyć klienta,
- wywołać emocję,
- być prosty,
- być konkretny.


COPY:

Używaj:

- prostego języka,
- krótkich zdań,
- języka klienta,
- korzyści zamiast cech.


LICZBY:

Wszystkie pola liczbowe MUSZĄ być integer.

Poprawnie:

{
"duration_seconds":15,
"duration":3,
"hook":8
}


Niepoprawnie:

{
"duration_seconds":"15 sekund",
"duration":"0-3s",
"hook":"8/10"
}



ODPOWIEDŹ:

Zwróć wyłącznie poprawny JSON.

Nie dodawaj:

- markdown,
- ```json,
- komentarzy,
- opisów przed JSON.

"""


USER_PROMPT_TEMPLATE = """

Na podstawie danych produktu wygeneruj dokładnie:

{count}

różnych reklam.


DANE PRODUKTU:

{product_json}

Zwróć dokładnie strukturę:

{{
"advertisements":[
    {{
        "name":"",
        "strategy":{{
            "framework":"",
            "angle":"",
            "psychology_trigger":"",
            "awareness_stage":"",
            "hypothesis":""

        }},
        "creative":{{
            "platform":"",
            "format":"",
            "duration_seconds":15,
            "aspect_ratio":"9:16",
            "hook":{{
                "text":"",
                "type":"",
                "visual":"",
                "duration":3

            }},
            "problem":"",
            "solution":"",
            "proof":{{
                "type":"",
                "content":""

            }},
            "scenes":[
                {{
                    "order":1,
                    "type" : "",
                    "description":"",
                    "duration_seconds":3
                }}
            ],
            "voiceover":"",
            "visual_direction":[
                ""
            ],
            "text_overlays":[
                ""
            ],
            "cta":{{
                "text":"",
                "type":"",
                "urgency":""
            }}
        }},
        "target_audience":{{
            "name":"",
            "pain_points":[
                ""
            ],
            "motivations":[
                ""
            ],
            "buying_triggers":[
                ""
            ]
        }},
        "objections_handled":[
            {{
                "objection":"",
                "answer":""
            }}
        ],
        "score":{{
            "hook":0,
            "emotion":0,
            "clarity":0,
            "purchase_intent":0,
            "overall":0
        }}
    }}
]
}}


DODATKOWE ZASADY:

1.Wygeneruj dokładnie {count} elementów.

2.Każda reklama musi mieć:
- inny framework,
- inny hook,
- inną grupę odbiorców,
- inny problem,
- inną hipotezę testową.

3. SCRIPT:
Script jest tablicą scen filmu.
Każda scena posiada:
- order,
- description,
- duration_seconds.

4.PROOF:
Nigdy nie wymyślaj dowodów.
Jeżeli brak danych:
"type":"",
"content":""

5.CTA:
CTA musi mówić użytkownikowi co zrobić.

Przykłady:
- Zamów teraz
- Sprawdź ofertę
- Zobacz jak działa
- Poznaj szczegóły

6.SCORE:
Skala 1-10.
Każda wartość musi być integer.
"""


def offer_profile_advertisement_generate_handler(
    offer_profile_id: int,
    count: int
):

    if count <= 0:
        raise ValueError(
            "count musi być większe od 0"
        )


    container = Container()


    offer_profile_service = container.offer_profile_service()


    ai_service = container.ai_service()

    product_json = offer_profile_service.build_llm_context(offer_profile_id=offer_profile_id)

    user_prompt = USER_PROMPT_TEMPLATE.format(count=count,product_json=product_json)

    response = (
        ai_service.chat_llm(
            messages=[

                LlmMessage(
                    role=LlmMessageRole.SYSTEM,
                    content=SYSTEM_PROMPT
                ),
                LlmMessage(
                    role=LlmMessageRole.USER,
                    content=user_prompt
                )
            ]
        )
    )

    generated_ads = json.loads(response.content.strip())

    return generated_ads.get("advertisements", [])