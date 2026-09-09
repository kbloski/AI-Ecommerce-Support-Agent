# Architecture — ai-ec-agent

Zweryfikowane w kodzie 2026-09-03 (commit `b942f16`, branch `main`).

Monorepo: `backend/` (FastAPI, Python) + `frontend/` (React 19 + Vite + TypeScript). Pełny biznesowy flow: patrz `application-flow.md`.

## Backend (`backend/`)

Stack: FastAPI 0.137, Starlette, uvicorn, SQLAlchemy 2.0 (ORM, SQLite domyślnie), `dependency_injector` (DI), `ollama` (klient lokalnego LLM), Pydantic (tylko walidacja request body), `python-docx`/`docx` (parsowanie dokumentów), `tiktoken` (liczenie tokenów).

Struktura:
- `main.py` — punkt wejścia; tworzy `FastAPI()`, rejestruje routery, **woła `init_db.init_db()` na poziomie importu modułu** (main.py:17, poza `if __name__=="__main__"`).
- `api/` — `__routes__.py` (rejestracja routerów + CORS `allow_origins=["*"]`, jedyny middleware, brak auth), `routes/general_routes.py` (właściwe endpointy), `routes/test_routes.py` (zepsuty endpoint deweloperski, patrz known-issues).
- `application/` — warstwa aplikacyjna:
  - `handlers/<encja>/*_handler.py` — jeden plik = jeden use-case (generate/get/update/delete/list); tu żyje logika promptów LLM i parsowania odpowiedzi.
  - `services/*_service.py` — CRUD pomocniczy + `build_llm_context()` (serializacja encji + przodków do promptu).
  - `assemblers/*_assembler.py` — dociąga powiązane kolekcje do DTO.
  - `mappers/*_mapper.py` — encja ORM → DTO.
  - `dtos/` — struktury wyjściowe API (własne klasy, nie Pydantic — patrz niżej).
- `domain/` — `models/` (encje SQLAlchemy pogrupowane per agregat pipeline'u: offers, knowledge, brand_marketing, marketing_strategy, offer_strategy, message_strategy, ad_strategy, creative_strategy, ad_execution, creative_execution, page_strategy, page_requirements, page_blueprint, page_content_plan, page_copy, ugc_creatives, analysis, checklist, audience), `enums/` (słowniki sterujące promptami/walidacją), `analysis/knowledge_analysis_questions.py`.
- `infrastructure/` — `database/` (silnik SQLAlchemy, `init_db`), `repositories/` (proste CRUD-owe query, bez JOIN-ów), `logging/logger.py`, `parsers/` (docx/txt), `ads/` i `pages/` (statyczne słowniki referencyjne JSON: frameworki reklamowe, kąty kreatywne, style egzekucji, platformy, typy sekcji strony), `ai/` (prompt „uniqueness”, `output.rules.md`, `token_counter.py`), `services/path_service.py`.
- `core/settings.py` — konfiguracja ze zmiennych środowiskowych (`HOST`, `PORT`, `OLLAMA_LLM_MODEL`, `OLLAMA_URL`, `OLLAMA_TEMPERATURE`, `OLLAMA_CONTEXT_LENGTH`=131072 domyślnie).
- `di/container.py` — kontener DI (`dependency_injector`) definiujący providers dla repo/assembler/service.
- `common/mixins/json_serializable.py` — `JSONSerializable` (metody `to_dict()`/`to_content_dict()`; ta druga usuwa `id`/`*_id`, żeby nie zaśmiecać promptu LLM).
- `scripts/` — ręczne skrypty migracyjne (poza Alembikiem, mimo że Alembic jest skonfigurowany).

### Warstwy per request (wzorzec)

Router → Handler → `Container()` (tworzony ad-hoc, nie shared) → Service.`build_llm_context()` → `ai_service.chat_llm()` → Ollama → `json.loads()` → zapis (Repository) → Assembler/Mapper → DTO.

DTO **nie są Pydantic** — własne klasy z `JSONSerializable`. Pydantic służy wyłącznie do walidacji request body w routerach.

Domain models = encje ORM SQLAlchemy wprost (brak oddzielenia modelu domenowego od modelu persystencji).

### Konfiguracja Ollama — nadpisania per instancja (dodane 2026-09-03)

`OLLAMA_URL`, `OLLAMA_LLM_MODEL`, `OLLAMA_TIMEOUT`, `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_TEMPERATURE` z `.env` mogą być nadpisane z poziomu UI (`/settings/general`, sekcja „Ollama”) i zapisane trwale w bazie danych tej instancji aplikacji — tabela `app_ollama_settings` (`domain/models/settings/app_ollama_settings.py`, jeden wiersz `id=1`, wszystkie pola nullable; `NULL` = użyj wartości z `.env`).

Merge logiki (baza → fallback `.env`) dzieje się w `OllamaService.__init__` (`application/services/ollama_service.py`), wstrzykiwanym `app_ollama_settings_repository`. Ponieważ `OllamaService`/`Container()` są tworzone od nowa przy każdym requeście (patrz sekcja „Warstwy per request” wyżej), nadpisania działają natychmiast bez restartu procesu.

API: `GET/POST /settings/ollama` (odczyt/zapis, format zgodny z istniejącym wzorcem `UpdateFieldsRequest`: `{"fields": {...}}`, `null` w polu czyści nadpisanie), `GET /settings/ollama/models?url=` (lista modeli z działającej instancji Ollama pod danym/aktualnym adresem, przez `client.list()`).

### Integracje

- **Ollama** (lokalny LLM) — jedyna integracja AI, `application/services/ollama_service.py` + `ai_service.py` (dokleja globalny prompt `output.rules.md` jako dodatkową wiadomość systemową).
- **SQLite** przez SQLAlchemy (`DATABASE_URL` env, fallback `sqlite:///./test.db`, realny plik `app.db` w repo).
- Brak integracji z zewnętrznymi API poza Ollama.

## Frontend (`frontend/`)

Stack: React 19.2, Vite 8, TypeScript ~6.0, react-router-dom v7 (`BrowserRouter`), Redux Toolkit + **RTK Query** (jedyny mechanizm komunikacji z API — nie axios/fetch/react-query), shadcn/ui na bazie **`@base-ui/react`** (nie Radix), Tailwind CSS v4 (`@tailwindcss/vite`, brak osobnego `tailwind.config`), `lucide-react` (ikony), `sonner` (toasty), `zod` (walidacja formularzy), lint: **oxlint** (nie ESLint).

Struktura (`src/`):
- `main.tsx`, `App.tsx` — punkt wejścia i ~40 tras w jednym drzewie `<Routes>` pod wspólnym layoutem `AppShell`.
- `components/` — layout (`AppShell`, `AppSidebar`, `AppContextSidebar`) + generyczne komponenty domenowe reużywane przez wszystkie strony pipeline'u (`DetailShell`, `EditableFields`, `EntityList`, `EntityViewer`, `ResourceList`, `RelationCards`, `SegmentedControl`, `MultiToggle`).
- `components/ui/` — prymitywy shadcn/ui.
- `features/` — 26 modułów RTK Query, po jednym na encję/etap pipeline'u (`api.injectEndpoints`, jeden wspólny `createApi` w `store/api.ts`).
- `pages/` — widoki routowane, głównie „DetailPage” per encja (cienkie spinacze danych RTK Query + `DetailShell`) + strony relacyjne (`EntityRelationPages.tsx`, `ResourcePages.tsx`).
- `store/` — `index.ts` (reducer = tylko `api.reducer`, brak własnych domenowych slice'ów), `api.ts` (baseUrl = `VITE_API_URL` ?? `http://localhost:8002`), `apiErrorMiddleware.ts` (globalne toasty błędów).
- `lib/` — `entityFields.ts` (etykiety pól, heurystyka wykrywania relacji), `tags.ts` (tagi cache RTK Query), `apiError.ts` (martwy kod — patrz known-issues), `utils.ts`.
- `types.ts` — jeden generyczny typ `Entity = {id: number, [key: string]: unknown}` — brak silnie typowanych DTO.

### Wzorzec strony (zaktualizowane 2026-09-09)

`DetailShell` + `ResourceList`: (1) pola bieżącej encji renderowane **tylko do odczytu** (generyczny `EditableFields.tsx` bez `onSave` renderuje `dl`/paragrafy, nie disabled inputy), (2) listy dzieci następnego etapu z przyciskiem „Generuj” (mutacja RTK Query), (3) nawigacja do szczegółów nowego obiektu po sukcesie.

**Edycja = drawer po prawej (`SidePanel`/`useSidePanel`), nigdy inline na stronie.** `DetailShell` przyjmuje prop `editable: {onSave, isSaving}` — gdy podany, renderuje przycisk „Edytuj” otwierający panel z `EditableFields` (onSave zamyka panel po sukcesie). To jedno miejsce obsługuje ~13 stron „DetailPage” automatycznie. Encje z niestandardowym formularzem (Offer, TargetAudience, PageRequirements) mają własny komponent formularza w `features/<encja>/*Form.tsx`, używany identycznie w drawerze (wzorzec: `EditOfferForm`, `EditTargetAudienceForm`, `EditSectionRequirementsForm`). Osobne strony `/*/edit` (jak dawny `TargetAudienceEditPage`) zostały wyeliminowane na rzecz drawera.

Do prostego, jednorazowego wywołania edycji z listy służy hook `lib/useEditEntityPanel.tsx` (`editEntity(title, item, onSave)`), używany m.in. w `ResourcePages.tsx`/`EntityRelationPages.tsx` dla list encji bez własnej strony formularza.

**Listy** — `EntityList`/`ResourceList` (`components/EntityList.tsx`, `components/ResourceList.tsx`) to jedyny, ujednolicony wzorzec listy w całej aplikacji: lp, nazwa, `ID {id}`, akcje ikonowe „otwórz” (`linkTo`), „Edytuj” (`onEdit`, ołówek), „Usuń” (`onDelete`, kosz). Wszystkie strony list (offers, offer-profiles, target-audiences, elementy oferty, wszystkie strony pośrednie łańcucha w `ResourcePages.tsx`) korzystają z tego komponentu — nie tworzyć bespoke markup dla nowych list. Wyjątek: `OfferProfileElementsPage` nie ma `onEdit`/`onDelete`, bo backend nie udostępnia endpointów update/delete dla `OfferProfileElement` (tylko list+create, patrz `known-issues.md`).

Cały stan serwerowy żyje w cache RTK Query; stan UI lokalny to zwykły `useState` w komponentach stron.

## Komendy deweloperskie (z `README.md` projektu)

Backend:
```bash
cd backend
source venv/bin/activate
python main.py
```

Frontend:
```bash
cd frontend
npm install
cp .env.example .env   # ustaw VITE_API_URL
npm run dev
```

Brak testów automatycznych — ani backend, ani frontend nie mają zainstalowanego frameworka testowego (patrz `known-issues.md`).
