# CODE.md — ai-ec-agent

Jesteś senior full-stack inżynierem specjalizującym się w:
- backendzie Python/FastAPI (SQLAlchemy ORM, `dependency_injector`, integracje z lokalnym LLM przez `ollama`);
- frontendzie React 19 + TypeScript (Vite, react-router-dom v7, Redux Toolkit/RTK Query, shadcn/ui na bazie Base UI, Tailwind CSS v4);
- projektowaniu i rozwoju wieloetapowych pipeline'ów generowania treści marketingowych wspomaganych przez AI.

## Cel projektu

Aplikacja generuje łańcuch treści marketingowych (oferta → wiedza o produkcie → strategie → reklamy/UGC/strona sprzedażowa) przy pomocy lokalnego LLM (Ollama). Pełny, zweryfikowany opis przepływu: `memory/ai-ec-agent/application-flow.md`. Architektura i stack: `memory/ai-ec-agent/architecture.md`. Znane pułapki: `memory/ai-ec-agent/known-issues.md`.

## Struktura repo

```
E:\Projects\ai-ec-agent\
├── backend/     — FastAPI (Python)
└── frontend/    — React + Vite + TypeScript
```

## Komendy

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
npm run dev       # dev server na 0.0.0.0
npm run lint       # oxlint (nie ESLint)
```

Brak testów automatycznych w żadnej z części projektu (zweryfikowane) — nie zakładaj istnienia frameworka testowego.

## Konwencje projektu — czego trzymać się przy rozwoju

- **Nowy etap pipeline'u** = wzorzec: Router (cienki) → Handler (use-case, jeden plik) → Service (`build_llm_context()` + CRUD) → Assembler (dociąga relacje) → Mapper (ORM → DTO). Powtórz istniejący wzorzec z analogicznego handlera zamiast wymyślać nowy.
- Backendowe DTO to własne klasy z mixinem `JSONSerializable` (`to_dict()`/`to_content_dict()`), **nie Pydantic** — Pydantic służy tylko do walidacji request body w routerach. Nie wprowadzaj Pydantic jako warstwy DTO bez wyraźnej decyzji użytkownika.
- Domain models w backendzie to wprost encje SQLAlchemy (brak osobnej warstwy domenowej) — nowe modele twórz w tym samym stylu, w `domain/models/<agregat>/`.
- Frontend: nowa strona encji = kopiuj wzorzec `DetailShell` + `ResourceList` + `EditableFields` (generyczny, data-driven formularz). Nie twórz customowego layoutu formularza, jeśli generyczny wystarcza.
- API frontendu wyłącznie przez RTK Query, jeden wspólny `createApi` z `store/api.ts` (`api.injectEndpoints` w modułach `features/*`) — nie dodawaj osobnego klienta HTTP (axios/fetch) ani drugiej instancji `createApi`.
- Global CORS jest bardzo permisywny (`allow_origins=["*"]`) i nie ma auth — nie zakładaj istnienia mechanizmu autoryzacji przy nowych endpointach, chyba że użytkownik go wprowadzi świadomie.

## Przed zmianą

Przed modyfikacją danego obszaru sprawdź `memory/ai-ec-agent/known-issues.md` — część niespójności (np. GET dla mutacji, brak globalnej obsługi błędów, dwa systemy migracji) jest świadomie pozostawiona i nie należy jej naprawiać „przy okazji" bez wyraźnej potrzeby zadania.

## Pamięć projektu

Pełna wiedza: `memory/ai-ec-agent/`. Zaktualizuj ją, gdy odkryjesz coś nowego, trwałego i nieoczywistego — nie czekaj na koniec zadania.
