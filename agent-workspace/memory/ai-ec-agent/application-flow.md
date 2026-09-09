# Application Flow — ai-ec-agent

Zweryfikowane w kodzie 2026-09-03 (commit `b942f16`, branch `main`). Nie opiera się na `CODE_PROMPT.md` ani żadnym wcześniejszym `APPLICATION_FLOW.md` — wyłącznie na analizie backendu (`backend/`) i frontendu (`frontend/`).

## Przegląd

Aplikacja to generator treści marketingowych oparty o lokalny LLM (Ollama). Użytkownik startuje od ręcznie wprowadzonej **Oferty** i przez kolejne kliknięcia „Generuj” w UI przechodzi łańcuch AI-generowanych artefaktów, aż do gotowych reklam, treści UGC lub kopii strony sprzedażowej. Każdy etap to osobna encja w bazie (SQLite przez SQLAlchemy), trwale zapisana, z własnym CRUD-em REST.

Claim z `backend/README.md` „offer→knowledge→strategy→ads/page” jest kierunkowo poprawny, ale rzeczywisty łańcuch ma znacznie więcej kroków i rozgałęzia się na 3 niezależne ścieżki po `message_strategy`.

## Pełny łańcuch (backend generation chain = frontend user flow)

```
Offer (ręczne, brak AI)                                    /offers/:id
  │  [opcjonalnie: OfferInsight — AI-wzbogacenie oferty]
  └─▶ Knowledge                                             /knowledges/:id
        │  [równolegle: Analysis → Checklist — weryfikacja jakości wiedzy, opcjonalne]
        │  [równolegle: TargetAudience — segmenty odbiorców, opcjonalne]
        └─▶ BrandMarketing                                  /brand-marketing/:id
              └─▶ MarketingStrategy                         /marketing-strategy/:id
                    └─▶ OfferStrategy                        /offer-strategy/:id
                          └─▶ MessageStrategy  ◀── HUB       /message-strategy/:id
                                │
                                ├─▶ [gałąź ADS]
                                │     AdStrategy → CreativeStrategy
                                │       → AdExecution (CRUD, bez AI)
                                │         → CreativeExecution  (AI, liść)
                                │
                                ├─▶ [gałąź UGC]
                                │     UgcCreative  (AI, liść, jeden krok)
                                │
                                └─▶ [gałąź PAGE]
                                      PageStrategy
                                        → PageRequirements (CRUD, bez AI — sekcje strony)
                                          → PageBlueprint (AI)
                                            → PageContentPlan (AI)
                                              → PageCopy (AI, liść — finalny tekst strony)
```

Każdy krok z „AI” generuje treść wołając Ollama; kroki oznaczone „CRUD, bez AI” (`AdExecution`, `PageRequirements`) to zwykłe tworzenie rekordu-kontenera bez wywołania LLM.

## Backend — jak wygląda pojedynczy krok generowania

Wzorzec identyczny dla ~20 etapów (przykład: `application/handlers/knowledges/knowledge_generate.py:48`):

1. **Router** (`api/routes/general_routes.py`) — cienki, deleguje do handlera. Uwaga: generowanie i CRUD idą przez `GET` (oznaczone komentarzem `# POST in future`), usuwanie też przez `GET .../delete`.
2. **Handler** (`application/handlers/<encja>/*_handler.py`) — jeden plik = jeden use-case. Tworzy własną instancję `Container()` (DI), pobiera `*_service`.
3. **build_llm_context()** (`application/services/*_service.py`) — serializuje bieżącą encję + wszystkich przodków w łańcuchu do bloków `<tag>...</tag>` (przez `JSONSerializable.to_content_dict()`, który usuwa `id`/`*_id`, żeby nie zaśmiecać promptu). Wyjątek: `OfferProfileService` przed serializacją pomija nieprzejrzane (`is_reviewed=False`) `TargetAudience` i `OfferProfileElement`, aby nie trafiały do kontekstu LLM.
4. **ai_service.chat_llm()** (`application/services/ai_service.py:25-48`) → `ollama_service` → Ollama, z dołączonym globalnym promptem `infrastructure/ai/rules/output.rules.md` jako dodatkowa wiadomość systemowa.
5. Parsowanie odpowiedzi jako JSON (`json.loads`) — **przeważnie bez try/except**, więc zły JSON z modelu = surowy HTTP 500.
6. Zapis nowej encji + powiązanych rekordów przez repository (`infrastructure/repositories/*_repository.py`), commit sesji SQLAlchemy.
7. **Assembler** dociąga powiązane kolekcje, **Mapper** zamienia encję ORM → DTO, DTO wraca w response.

**Kluczowa właściwość:** kontekst nie jest cache'owany — każde kolejne wywołanie generowania odtwarza cały łańcuch wstecz (nawet 7 warstw przy `page_copy`) i wysyła go od nowa do LLM. Stąd wymagany duży `OLLAMA_CONTEXT_LENGTH` (domyślnie 131072, `core/settings.py:26`).

**Human-in-the-loop (deklaratywny, niewymuszony):** insighty i target audience mają pola `fact_status`/`review_status` (workflow weryfikacji AI-generowanych faktów przez człowieka), ale kolejne etapy pipeline'u **nie sprawdzają** tych statusów przed użyciem danych jako kontekstu — weryfikacja jest tylko sugestią UI, nie twardą bramką.

## Frontend — jak wygląda pojedynczy krok w UI

Wzorzec identyczny na każdej stronie detali (`DetailShell` + `ResourceList`, np. `pages/KnowledgeDetailPage.tsx`, `pages/PageStrategyDetailPage.tsx`):

1. Widok szczegółów bieżącej encji — edytowalne pola (generyczny, data-driven formularz `EditableFields.tsx`) + surowy JSON w collapsible.
2. Lista(y) dzieci następnego etapu z przyciskiem **„Generuj”** → mutacja RTK Query → `GET/POST .../generate` na backendzie.
3. Po sukcesie: nawigacja do strony szczegółów nowo utworzonego obiektu — i tak dalej wzdłuż łańcucha.

`AppContextSidebar.tsx:23-46` pokazuje użytkownikowi aktualny etap i link do kolejnego kroku procesu, niezależnie od głównego menu.

Cała warstwa API frontendu to RTK Query (`src/store/api.ts`, jeden wspólny `createApi`), moduły w `features/*/*.ts` (26 modułów, po jednym na encję) dodają endpointy przez `api.injectEndpoints`. Brak silnie typowanych DTO — wszystko traktowane jako `Entity = {id: number, [key: string]: unknown}` (`src/types.ts`).

> ⚠️ **Ta tabela jest częściowo nieaktualna (stan na 2026-09-03).** Weryfikacja 2026-09-09 (patrz `known-issues.md`) potwierdziła, że `OfferInsight`/`OfferInsightType`/`Knowledge` zostały **usunięte z kodu** (retirement udokumentowany w `infrastructure/database/init_db.py`) i zastąpione encją `OfferProfile` (generowaną z `Offer` przez `POST /offers/{id}/offer-profiles/generate`, wraz z jej dziećmi `OfferProfileElement` w jednym wywołaniu — patrz `offer_profile_generate.py`). Poniższa tabela wymaga pełnej weryfikacji od nowa (nie zrobiono tego przy okazji, żeby nie rozszerzać niepowiązanego zadania) — nie ufać jej bezkrytycznie, zwłaszcza wierszom `OfferInsight`/`Knowledge`.

## Nowe/potwierdzone endpointy generujące (dodane/zweryfikowane 2026-09-09)

| Etap | Endpoint | AI? | Uwagi |
|---|---|---|---|
| OfferProfile (+ jej `OfferProfileElement`) | `POST /offers/{id}/offer-profiles/generate` | tak | Generuje `OfferProfile` i od razu komplet `OfferProfileElement` (typy z `OfferProfileElementType`) w jednym wywołaniu LLM — patrz `offer_profile_generate.py`. |
| OfferProfileElement (dogenerowanie wybranych typów) | `POST /offer-profiles/{offer_profile_id}/elements/generate` (body: `{"element_types": [...]}`, min. 1) | tak | Dodane 2026-09-09 na życzenie użytkownika — generuje **dodatkowe** elementy tylko dla wybranych typów (nie dotyka istniejących/innych typów), bez modyfikowania samego `OfferProfile`. Handler: `application/handlers/offer_profiles/generate_offer_profile_elements_handler.py`. Definicje typów (do promptu) trzymane w `OFFER_PROFILE_ELEMENT_TYPE_DEFINITIONS` w tym samym pliku — jedyne miejsce w kodzie z opisami znaczenia poszczególnych `OfferProfileElementType`. Frontend: przycisk „Generuj elementy” na `/offer-profiles/{id}/elements` otwiera drawer z `MultiToggle` (pierwsze użycie tego dotąd nieużywanego komponentu) do wyboru typów. |

## Endpointy generujące (kolejność w łańcuchu, ⚠️ nieaktualne — patrz ostrzeżenie wyżej)

| Etap | Endpoint | AI? |
|---|---|---|
| Offer | `GET /offers/create` | nie |
| OfferInsight | `POST /offers/{offer_id}/insights/generate` | tak |
| Knowledge | `GET /offers/{id}/knowledges/generate` | tak |
| TargetAudience | `GET /knowledges/{id}/target-audiences/generate` | tak |
| Analysis / Checklist | `GET /knowledges/{id}/analysis/create` + `.../answers/generate`, `.../checklists/create` + `.../generate` | tak (pytania/checklisty) |
| BrandMarketing | `GET /knowledges/{id}/brand-marketing/generate` | tak |
| MarketingStrategy | `GET /brand-marketing/{id}/marketing-strategy/generate` | tak |
| OfferStrategy | `GET /marketing-strategy/{id}/offer-strategy/generate` | tak |
| MessageStrategy | `GET /offer-strategy/{id}/message-strategy/generate` | tak |
| AdStrategy | `GET /message-strategy/{id}/ad-strategy/generate` | tak |
| CreativeStrategy | `GET /ad-strategy/{id}/creative-strategy/generate` | tak |
| AdExecution | `GET /creative-strategy/{id}/ad-execution/create` | nie |
| CreativeExecution | `GET /ad-execution/{id}/creative-execution/generate` | tak |
| UgcCreative | `GET /message-strategy/{id}/ugc-creatives/generate` | tak |
| PageStrategy | `GET /message-strategy/{id}/page-strategy/generate` | tak |
| PageRequirements | `GET /page-strategy/{id}/page-requirements/create` | nie |
| PageBlueprint | `GET /page-requirements/{id}/page-blueprint/generate` | tak |
| PageContentPlan | `GET /page-blueprint/{id}/page-content-plan/generate` | tak |
| PageCopy | `GET /page-content-plan/{id}/page-copy/generate` | tak |

Każda encja ma też pełny CRUD (`get`/`update` przez `POST .../update`/`delete` przez `GET .../delete`).

## Dane wejściowe — z czego dokładnie generuje każdy krok

Mechanizm jest zawsze ten sam: `*_service.build_llm_context(id)` serializuje bieżącą encję **i rekurencyjnie wszystkich jej przodków w łańcuchu** (przez FK, np. `PageStrategy.message_strategy_id → MessageStrategy.offer_strategy_id → ...`) do bloków `<tag>...</tag>` wstawianych do promptu. Nic nie jest cache'owane ani skracane — im głębiej w łańcuchu, tym więcej warstw kontekstu wysyłanych na nowo przy każdym wywołaniu.

| Etap | Dane wejściowe do LLM |
|---|---|
| Offer | brak — wpisywane ręcznie przez użytkownika (formularz) |
| OfferInsight | Offer + wybrane typy insightów (`OfferInsightType[]`) z requestu |
| Knowledge | Offer (cały) |
| TargetAudience | Knowledge + już istniejące TargetAudience tej wiedzy (przez `build_uniqueness_prompt`, żeby LLM nie duplikował segmentów) |
| Analysis / Checklist | Knowledge → pytania weryfikacyjne; odpowiedzi na pytania → checklisty jakości |
| BrandMarketing | Knowledge |
| MarketingStrategy | Knowledge + BrandMarketing |
| OfferStrategy | Knowledge + BrandMarketing + MarketingStrategy |
| MessageStrategy | Knowledge + BrandMarketing + MarketingStrategy + OfferStrategy |
| AdStrategy | cały łańcuch wstecz: Knowledge…MessageStrategy |
| CreativeStrategy | AdStrategy + cały łańcuch wstecz |
| AdExecution | brak LLM — tylko parametry z requestu: `creative_type`, `platform`, `format` (walidowane wg enuma `CreativeTypes`) |
| CreativeExecution | AdExecution + cały łańcuch wstecz + parametry z requestu: `duration_seconds`, `number_of_slides`, `ad_framework_id`, `creative_angle_id`, `execution_style_id` (te trzy ostatnie pobierane ze statycznych słowników JSON w `infrastructure/ads/*.json`) |
| UgcCreative | MessageStrategy + cały łańcuch wstecz, z `build_uniqueness_prompt` (unikanie powtórzeń) |
| PageStrategy | Knowledge + BrandMarketing + MarketingStrategy + OfferStrategy + MessageStrategy (bardzo rozbudowany prompt strategiczny CRO) |
| PageRequirements | brak LLM — lista sekcji strony (`PageSectionRequirement`) wybierana ręcznie ze słownika `infrastructure/pages/page_section_types.json` |
| PageBlueprint | PageRequirements + cały łańcuch wstecz + katalog dostępnych typów sekcji (`page_sections_service`) |
| PageContentPlan | PageBlueprint + cały łańcuch wstecz |
| PageCopy | PageContentPlan + PageBlueprint + PageStrategy + cały łańcuch strategii wstecz + katalog sekcji (`page_sections_service.get_all()`, do walidacji `section_type`) |

Dane wysyłane do promptu to zawsze `to_content_dict()` danej encji (bez `id`/`*_id`) — surowa treść biznesowa, nie identyfikatory. `fact_status`/`review_status` (workflow weryfikacji faktów) **nie filtruje** tego, co trafia do kontekstu — patrz `known-issues.md`.

## Powiązane pliki pamięci

- `architecture.md` — warstwy, stack technologiczny, DI, konfiguracja.
- `known-issues.md` — pułapki i niespójności odkryte podczas analizy.
