# Project Understanding — ai-ec-agent

Status: INITIALIZED

Last full analysis: 2026-09-03 12:00

Project root: `E:\Projects\ai-ec-agent` (lokalizacja wskazana przez `projects/PROJECTS.md`: katalog dwa poziomy wyżej, `../../`)

## Verified Areas

- struktura projektu (monorepo: `backend/` FastAPI + `frontend/` React/Vite/TS)
- stack technologiczny (backend i frontend)
- architektura backendu (warstwy: router → handler → service → repository, DI ad-hoc)
- architektura frontendu (React Router v7, Redux Toolkit + RTK Query, shadcn/ui na Base UI)
- pełny biznesowy pipeline generowania treści (offer → knowledge → strategy → ads/ugc/page), zweryfikowany od zera w kodzie
- konfiguracja (zmienne środowiskowe backend/frontend)
- integracje (Ollama jako jedyny zewnętrzny LLM, SQLite jako baza)
- stan testów (brak testów automatycznych w obu częściach projektu)

## Persistent Context

Utworzono:

- `memory/ai-ec-agent/application-flow.md` — pełny, zweryfikowany flow aplikacji (backend generation chain + frontend user flow)
- `memory/ai-ec-agent/architecture.md` — warstwy, stack, struktura katalogów backend+frontend
- `memory/ai-ec-agent/known-issues.md` — pułapki i niespójności odkryte w kodzie
- `prompts/ai-ec-agent/CODE.md` — rola agenta i stabilne instrukcje pracy nad projektem

Nie utworzono `rules/ai-ec-agent/` — podczas analizy nie zidentyfikowano jeszcze zweryfikowanych, obowiązkowych ograniczeń (odkryte niespójności to konwencje/pułapki, nie reguły narzucone przez użytkownika lub dokumentację projektu). Utworzyć w przyszłości, gdy pojawi się rzeczywista, potwierdzona reguła.

## Known Unknowns

- Który system migracji (Alembic vs ręczne ALTER TABLE w `init_db.py`) jest faktycznym źródłem prawdy — niezweryfikowane, wymaga decyzji użytkownika jeśli temat wypłynie.
- Środowisko produkcyjne / sposób deploymentu — nie analizowano (brak plików CI/CD, Dockerfile w repo w momencie analizy).
- Szczegóły promptów LLM dla każdego etapu (treść promptów jest bardzo obszerna, np. `page_strategy`/`page_copy` — nie kopiowano treści promptów do pamięci, tylko referencje plik:linia).

## Git Verification

Verified commit: `b942f16` (branch `main`)
