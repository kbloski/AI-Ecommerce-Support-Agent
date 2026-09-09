import base64
from di.container import Container
from domain.models.llm.llm_message import LlmMessage
from domain.enums.llm_message_role import LlmMessageRole


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def test():
    container = Container()
    ai_service = container.ai_service()
    path_service = container.path_service()

    image_path = path_service.UPLOADS_DEV / "products" / "mini_pila_lancuchowa" / "images" / "Screenshot 2026-07-02 225353.png"
    image_b64 = encode_image(image_path)

    # Lista przedmiotów z oferty w języku angielskim (dla stabilności VLM)
    # Mapujemy je słownikiem, żeby potem łatwo połączyć angielski wynik z polską nazwą
    items_to_check = {
        "piła": "chainsaw",
        "ładowarka": "charger",
        "baterie": "batteries",
        "śrubokręt": "screwdriver",
        "łańcuch": "chain",
        "walizka": "suitcase/case"
    }

    vlm_raw_results = []

    # 1. Odpytujemy VLM po angielsku o wygląd każdego elementu osobno
    for pl_name, eng_name in items_to_check.items():
        vlm_messages = [
            VlmOllamaMessage(
                role=LlmMessageRole.USER,
                content=(
                    f"Look at the image. Is there a {eng_name} visible? "
                    f"If yes, describe its visual appearance (color, quantity, location) in ONE short sentence. "
                    f"If no, write '{eng_name}: not visible'. Be extremely concise."
                ),
                images=[image_b64]
            ),
        ]

        try:
            response = ai_service.chat_vlm(vlm_messages)
            # Zapisujemy polską nazwę i angielski opis z modelu VLM
            vlm_raw_results.append(f"- {pl_name}: {response.content.strip()}")
        except Exception as e:
            vlm_raw_results.append(f"- {pl_name}: błąd analizy ({str(e)})")

    # Łączymy zebrane angielskie opisy w jeden tekst
    english_facts = "\n".join(vlm_raw_results)

    # 2. Przekazujemy zebrany tekst do LLM wyłącznie w celu dokładnego tłumaczenia na język polski
    llm_messages = [
        LlmMessage(
            role=LlmMessageRole.USER,
            content=(
                "Przetłumacz poniższe angielskie na język polski: "
                f"{english_facts}\n\n"
            ),
        ),
    ]

    translated = ai_service.chat_llm(llm_messages)

    return {
        "status": "ok",
        "result": {
            "image_path": image_path,
            "message": translated
        }
    }