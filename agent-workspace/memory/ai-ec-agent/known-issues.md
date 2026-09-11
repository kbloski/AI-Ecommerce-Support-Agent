# Known Issues / pułapki — ai-ec-agent

Odkryte podczas pierwszej analizy 2026-09-03 (commit `b942f16`). To obserwacje, nie zadania do wykonania — informować/uwzględniać przy pracy w danym obszarze, nie naprawiać „przy okazji" bez potrzeby związanej z zadaniem.

## Backend

- ~~**`GenerateAd` nie zapisywał się po rozdzieleniu `AdSetup` / `CreativeExecutionSetup`** — stara tabela `generate_ads` zachowywała `ad_setup_id NOT NULL`, podczas gdy model zapisywał już wyłącznie `creative_execution_setup_id`, więc każdy INSERT kończył się naruszeniem `NOT NULL`.~~ Rozwiązane 2026-09-11: `_migrate_creative_execution_setups()` mapuje legacy rows do domyślnego setupu, a następnie przebudowuje tabelę do docelowego schematu z wymaganym `creative_execution_setup_id` i bez `ad_setup_id`. Repozytorium wykonuje rollback po błędzie zapisu.

- **`Container()` tworzony per handler/request**, nie jako jeden obiekt aplikacji (np. `application/handlers/knowledges/knowledge_generate.py:50`). Providery `Singleton` w `di/container.py` są singletonami tylko w obrębie krótkotrwałej instancji — DB session i logger de facto tworzone od nowa za każdym razem. To Service Locator ad-hoc, nie klasyczny DI z jednym kontenerem aplikacji.
- **Mutacje/generowanie idą przez `GET`**, oznaczone komentarzami `# POST in future` / `# DELETE in future` w `api/routes/general_routes.py` — niezgodne z semantyką HTTP, kosztowne operacje LLM wywoływane przez `GET` bez idempotencji.
- **Brak globalnej obsługi błędów** — nieobsłużone wyjątki (np. `json.loads()` na złej odpowiedzi LLM) kończą się surowym HTTP 500 bez czytelnego komunikatu. Tylko pojedyncze handlery (np. `generate_page_copy_handler.py:153-172`) łapią błąd parsowania i zwracają `{"error", "raw_response"}`.
- **`init_db()` woła się przy imporcie `main.py`** (linia 17, poza `if __name__=="__main__"`) — samo zaimportowanie modułu (np. w przyszłych testach) uruchamia tworzenie/migrację tabel na żywej bazie z `.env`.
- **Dwa równoległe systemy migracji**: ręczne „additive migrations” (`ALTER TABLE`) w `infrastructure/database/init_db.py` **oraz** Alembic (skonfigurowany, opisany w README, ale nieużywany na bieżąco). Nie jest jasne, który jest źródłem prawdy — sprawdzić przed jakąkolwiek zmianą schematu.
- **`GET /test`** (`api/routes/test_routes.py` + `application/handlers/test/test.py`) jest zepsuty — odwołuje się do nieistniejącej metody `ai_service.chat_vlm()` i niezaimportowanej klasy `VlmOllamaMessage`. Relikt niedokończonej funkcji VLM.
- **Dwa pakiety DOCX** w `requirements.txt` (`docx` i `python-docx`) — potencjalny konflikt nazw modułu.
- **`.env` jest commitowany** do repo z realną konfiguracją (host/port/baza/model Ollama).
- **Brak cache'owania kontekstu LLM** — każdy krok generowania odtwarza cały łańcuch przodków i wysyła go od nowa (np. `generate_page_copy_handler.py:92-124` odtwarza 7 warstw kontekstu). Stąd wymagany duży `OLLAMA_CONTEXT_LENGTH`.
- **`fact_status`/`review_status`** (workflow weryfikacji AI-generowanych faktów) nie są programowo wymuszane — kolejne etapy pipeline'u używają danych jako kontekstu niezależnie od statusu weryfikacji.
- **Brak testów automatycznych** — brak `pytest` w `requirements.txt`, brak plików `test_*.py`.
- ~~`OLLAMA_TIMEOUT` zdefiniowany w `.env`, ale nieużywany nigdzie w `Settings`/`OllamaService` — martwa zmienna.~~ Rozwiązane 2026-09-03: dodano `Settings.get_ollama_timeout()` i przekazywanie go do `ollama.Client(host=..., timeout=...)`.

## Frontend

- **`src/lib/apiError.ts` to martwy kod** — zduplikowana logika z `apiErrorMiddleware.ts` (`stringifyDetail`/`getApiErrorMessage`), nigdzie nieimportowany.
- **`src/types.ts` praktycznie pusty** (`Entity = {id: number, [key: string]: unknown}`) — brak silnie typowanego kontraktu z backendem, wszystko przez rzutowania `as string`/`as number`. Zmiany pól backendu nie są wykrywane przez kompilator.
- **Heurystyka wykrywania relacji** (`lib/entityFields.ts:26-32`) uznaje pole za relację tylko jeśli tablica obiektów ma elementy z `id` — pusta tablica dzieci zostanie potraktowana jak zwykłe pole edytowalne, chyba że strona jawnie definiuje `itemActions`/`itemLinks`.
- **`SettingsPage`** — pole „Base output prompt” i przycisk „Zapisz” są zawsze `disabled` (`pages/SettingsPage.tsx:54,60`) — funkcjonalność widoczna w UI, ale wyłączona.
- **`DashboardPage`** to pusty placeholder — brak realnego widoku startowego.
- **Brak testów automatycznych** — brak frameworka testowego (vitest/jest), brak skryptu `test` w `package.json`.
- Formularz pól (`EditableFields.tsx`) dla wartości nieprymitywnych wymaga ręcznego wpisania poprawnego JSON-a w textarea — brak walidacji struktury.
- **Gwiazdka „ulubione” na listach frontendu (usunięta 2026-09-09)** była zaimplementowana wyłącznie w `localStorage` (per przeglądarka, klucz `aiec:favorites:${pathname}`) i **nie miała nic wspólnego** z realną kolumną `is_favorite` opisaną niżej.
- **Backend ma martwą infrastrukturę pod „ulubione” (`is_favorite`)**: każda encja z `domain/models/favorites_registry.py` (m.in. `Offer`, `OfferProfile`, `TargetAudience` i wszystkie etapy strategii/stron) ma w bazie kolumnę `is_favorite` (dodawaną addytywną migracją w `init_db.py`), ale **żaden route w `general_routes.py` jej nie czyta/nie zapisuje celowo** — da się ją ustawić tylko przez generyczny `POST .../update` (bo handlery robią `setattr` dla dowolnego klucza z `fields`), nic w UI tego nie robi. Jeśli temat "ulubione" wróci, dowiązać do tej kolumny zamiast localStorage.

## Ważne: `application-flow.md` jest częściowo nieaktualny (odkryte 2026-09-09)

`OfferInsight`/`OfferInsightType`/`Knowledge` (opisane w `application-flow.md` jako część łańcucha) **zostały usunięte z kodu** — potwierdzone `git grep` (zero wyników poza skompilowanymi `.pyc`) i jawnym komentarzem w `infrastructure/database/init_db.py`: *"Offer items, insights, and pricing are intentionally removed with this feature"* (dropuje tabele `offer_items`, `offer_insights`, `knowledge_insights`, `offer_profile_insights`, zmienia nazwę `offers` → `offers_raw`). Ich rolę przejęła encja `OfferProfile` (generowana bezpośrednio z `Offer` przez `POST /offers/{id}/offer-profiles/generate`, razem z jej dziećmi `OfferProfileElement` w jednym wywołaniu LLM). `application-flow.md` nie został jeszcze w pełni zweryfikowany po tej zmianie — traktować tabelę „Endpointy generujące" tam jako punkt startowy do weryfikacji, nie jako pewnik.

## Do zweryfikowania w przyszłości

- Który system migracji (Alembic vs ręczne ALTER TABLE) jest faktycznie używany w praktyce/produkcji — zapytać użytkownika, jeśli temat wypłynie przy pracy nad schematem danych.
