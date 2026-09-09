from enum import Enum


class ContextSectionPurpose(str, Enum):
    OFFER_PROFILE = "Informacje opisujące ofertę, jej odbiorców oraz fakty, możliwości i ograniczenia produktu."
    BRAND_MARKETING = "Informacje o tym, jak marka ma być pozycjonowana, postrzegana i komunikowana."
    MARKETING_STRATEGY = "Informacje o tym, do kogo kierować działania marketingowe, gdzie je prowadzić i jakie cele realizować."
    OFFER_STRATEGY = "Informacje o tym, jak przedstawiać ofertę, jej wartość, korzyści i powody zakupu."

    # Adds
    CREATIVE_STRATEGY = "Informacje o tym, jaki główny kierunek i sposób komunikacji powinny mieć kreacje reklamowe."
    CAMPAIGN = "Informacje o celu, odbiorcy i głównym kierunku konkretnej kampanii."
    AD_FRAMEWORK = "Informacje o tym, z jakich etapów ma składać się reklama i w jakiej kolejności."
    CREATIVE_ANGLE = "Informacje o tym, z jakiej perspektywy należy przedstawić przekaz reklamowy."
    EXECUTION_STYLE = "Informacje o tym, jak kreatywa ma wyglądać i w jaki sposób ma być wykonana."
    PLATFORM = "Informacje o tym, gdzie reklama będzie publikowana i do jakich zasad należy ją dostosować."
    CREATIVE_EXECUTION = "Informacje opisujące konkretną, finalną wersję reklamy."

    # Page
    PAGE_STRATEGY = "Informacje o celu strony, jej odbiorcy oraz sposobie, w jaki ma prowadzić użytkownika do pożądanego działania."
    PAGE_REQUIREMENTS = (
        "Informacje określające wymagania i ograniczenia dotyczące strony, "
        "w tym sekcje obowiązkowe, opcjonalne i wykluczone oraz inne narzucone elementy struktury."
    )
    PAGE_BLUEPRINT = "Informacje o strukturze strony, kolejności sekcji oraz roli każdej z nich w procesie komunikacji i konwersji."
    PAGE_CONTENT_PLAN = "Informacje o tym, jakie treści, argumenty i komunikaty powinny znaleźć się w poszczególnych sekcjach strony."
    PAGE_COPY = "Informacje opisujące konkretną, finalną treść strony, w tym nagłówki, teksty, argumenty i wezwania do działania."