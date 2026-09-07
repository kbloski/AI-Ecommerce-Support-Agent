# Plan działania po audycie kodu i procesu — ai-ec-agent

Data: 2026-09-07, 10:08, Europe/Warsaw (UTC+02:00).  
Status: **audyt zakończony; proponowane zmiany nie zostały wdrożone**.  
Projekt: `E:/Projects/_/ai-ec-agent`.  
Badany commit: `7a085c1a365d9c1b7d71ad9a417aeb299ab032d1`. Stan śledzonych plików przed audytem: czysty.  
Właściciel realizacji: do przypisania przy rozpoczęciu prac.  
Podstawa: prośba użytkownika o przeczytanie ROOT_PROMPT i zależności, sprawdzenie kodu oraz zapisanie propozycji jako planu.

## Cel i najważniejsze wnioski

Najpierw usunąć ryzyko utraty lub nadpisania danych, następnie uporządkować kontrakty API/LLM i walidację, a potem poprawić powtarzalność pracy agenta oraz jakość generowania. Zachować obecną architekturę warstwową i RTK Query; audyt nie uzasadnia przepisania całej aplikacji.

Potwierdzono m.in. utratę starych sekcji po błędzie zapisu nowych, brak klucza obcego w istniejącej bazie, możliwość wysłania pól poprzedniej encji przez formularz, niespójny cache ustawień Ollama oraz zapisywanie niepoprawnych struktur wygenerowanych przez LLM. Build frontendu i zgodność pakietów Pythona przechodzą, więc same te kontrole nie chronią przed opisanymi błędami.

Priorytety: **P1** — pierwsza kolejność, integralność danych lub istotna awaria; **P2** — następna kolejność, poprawność i utrzymanie; **P3** — rozwój po stabilizacji. Poziom `high` z npm jest oceną zgłoszenia pakietu, nie automatycznie priorytetem ani dowodem podatności tej aplikacji.

## Zakres i zależności dokumentów

Przeczytano cały `agent-workspace/ROOT_PROMPT.md` — 2255 linii — oraz wszystkie 20 pozostałych plików Markdown znajdujących się w jego workspace przed audytem:

- README workspace i README katalogów `project`, `prompts`, `rules`, `memory`, `plans`, `decisions`, `references`, `templates`, `output`, `scratch`;
- `project/PROJECTS.md`;
- `prompts/ai-ec-agent/CODE.md`;
- `memory/ai-ec-agent/{project-understanding,architecture,application-flow,known-issues}.md`;
- oba plany z 2026-09-04 dotyczące `/pipeline/path` i przycisku pobierania;
- `references/ai-ec-agent/example-ad-generation-chain.md`.

Dodatkowo sprawdzono README repo, backendu i frontendu, oba istotne `.gitignore`, manifesty i lockfile, instrukcje generatora w `backend/infrastructure/ai/rules/output.rules.md`, routing, konfigurację, modele i repozytoria danych, reprezentatywne handlery generowania, formularze, cache i eksport pipeline. Przegląd kodu obejmował ważne ścieżki działania; nie był liniowym przeczytaniem każdego pliku źródłowego ani oceną każdej odpowiedzi rzeczywistego modelu.

Stwierdzone braki i rozbieżności:

| Odwołanie | Stan |
| --- | --- |
| ROOT → `projects/PROJECTS.md` | Brak; istnieje `project/PROJECTS.md`, zawierający opis `../../` bez jednoznacznej bazy ścieżki. |
| README repo → `APPLICATION_FLOW.md` | Plik nie istnieje; aktualny opis jest w pamięci workspace. |
| `templates/PLAN.md` | Brak, dozwolony przez ROOT; użyto struktury dostosowanej do audytu. |
| `rules/ai-ec-agent`, decyzje projektu | Brak; katalogi nadrzędne zawierają README. |
| `AGENTS.md` | Nie znaleziono w badanym projekcie i workspace. |
| Alembic | Pakiet i polecenia w README są obecne; brak konfiguracji i rewizji w repo oraz brak `alembic_version` w sprawdzonej bazie. |

Projekt wybrano na podstawie lokalizacji wskazanego dokumentu, konfiguracji i pamięci. Bieżący katalog sesji w FreeSale nie jest celem tego planu. Polecenia w analizowanych materiałach, historycznych planach i promptach aplikacji potraktowano jako przedmiot przeglądu. Nie wykonywano zapisanych tam zadań ani automatycznej reorganizacji dokumentacji.

## Co rzeczywiście zweryfikowano

| Kontrola | Wynik i ograniczenia |
| --- | --- |
| Parsowanie AST backendu | 329 plików Python, 0 błędów składni. Nie zastępuje wykonania ani testów zachowania. |
| Lokalny Python | `backend/venv/Scripts/python.exe`: **3.10.0**; README deklaruje **3.14**. To rozbieżność środowiska, nie dowód niezgodności aplikacji z 3.14. |
| `python -m pip check` | PASS; wszystkie wersje z `requirements.txt` zgodne z lokalnie zainstalowanymi. Nie jest to skan podatności pakietów Python. |
| DOCX | Zainstalowane `docx==0.2.4` i `python-docx==1.2.0`; lokalne `from docx import Document` działa i wskazuje pakiet `python-docx`. Konflikt importu nie został odtworzony. |
| `npm ls --depth=0`, manifest ↔ lockfile | PASS, bez brakujących/invalid pakietów i bez rozbieżności deklaracji root. |
| `npm run lint` | PASS, 1 ostrzeżenie `react/only-export-components` w `src/components/ui/button.tsx:59`. |
| `npm run build` | PASS, obejmuje `tsc -b` i Vite. Główny JS 699,83 kB, gzip 208,91 kB; ostrzeżenie o chunku >500 kB. |
| `npm audit --json` oraz `--omit=dev` | Oba: kod wyjścia 1; **13 pozycji pakietów: 9 high, 4 moderate, 0 critical**. Szczegóły i kontekst poniżej. |
| Zastąpienie sekcji wymagań strony | Prawdziwe repozytorium SQLAlchemy, SQLite w pamięci: wymuszony błąd INSERT usuwa poprzedni zestaw mimo rollbacku. |
| Handlery LLM z atrapą modelu | Blueprint zapisuje `sections=[123]`; Page Copy dla `NOT JSON` zwraca słownik błędu serializowany jako HTTP 200. |
| Sondy rzeczywistego kodu frontendu | Odtworzono błąd `currentTarget`, stare wartości `EditableFields` i niespójność RTK cache ustawień. Kontrolowane zależności/hooki, bez przeglądarki. |
| Schemat istniejącego `backend/app.db` | SQLite URI `mode=ro` i `query_only`: brak FK `page_blueprint.page_requirements_id`; nie wyświetlano danych biznesowych rekordów. |
| Rejestracja routera/OpenAPI | `Routes(app)` i ponowne `register()`: 122 ostrzeżenia `Duplicate Operation ID`, 120 ścieżek OpenAPI. Bez importowania `main.py` i bez zapisu do DB. |
| Wejściowe modele API | Akceptują m.in. `position=2**100`, dowolny typ sekcji oraz ustawienia `ollama_timeout='bad'` i ujemny kontekst. |

Nie uruchamiano rzeczywistego LLM, aplikacji na danych użytkownika, przeglądarkowych E2E, migracji ani instalacji/aktualizacji pakietów. Nie wykonano audytu CVE całego środowiska Python ani testu wydajności/ekspozycji sieciowej. Build wytworzył zwykłe ignorowane artefakty `dist` i cache TypeScript; kod źródłowy pozostał bez zmian.

## Kolejność realizacji

| Pakiet prac | Zadania | Warunek zakończenia |
| --- | --- | --- |
| 1. Ochrona danych i pilne błędy UI | Z01, Z02, Z03, Z04; równolegle Z08 i Z10 | Regresje danych/formularzy przechodzą; migracja sprawdzona na kopii; projekt daje się jednoznacznie zlokalizować. |
| 2. Kontrakty i powtarzalne sprawdzanie | Z05, Z06, Z07, Z09, Z13 | Niepoprawne wejście/wyjście nie trafia do DB; API ma określone statusy; CI odtwarza testy i build. |
| 3. Proces i codzienna użyteczność | Z11, Z12, Z14, Z15 | Dokumenty są spójne, plany mają statusy, listy i cache pokazują poprawne dane; uzgodniona polityka faktów. |
| 4. Kontrolowany rozwój generowania | Z16, Z17, Z18 | Mierzalna jakość, ślad generacji, wznawianie i optymalizacje oparte na pomiarze. |

Test regresji dla danego defektu powstaje razem z jego poprawką; nie należy czekać z nim na rozbudowanie całego CI. Z09 dotyczące dostępu do aplikacji ma pierwszeństwo przed udostępnieniem jej poza zaufane środowisko lokalne. Każdy poniższy checkbox oznacza przyszłą pracę, a nie wykonaną poprawkę.

## Zadania — integralność danych i działanie aplikacji

### Z01 — P1: atomowe operacje i deterministyczny cykl sesji

- [ ] Naprawić zastępowanie sekcji w jednej transakcji, a następnie objąć tą zasadą złożone operacje tworzenia analizy/checklisty i przypinania relacji.

**Dowód:** `backend/infrastructure/repositories/page_section_requirements_repository.py:52` usuwa sekcje, linia 54 wykonuje commit, linia 56 osobno zapisuje nowe. Dla pozycji `2**100` INSERT kończy się `OverflowError`: przed próbą 1 sekcja, po błędzie i rollbacku 0. Analogiczna sekwencja wielu commitów występuje w `application/handlers/analysis/create_analysis_for_knowledge_handler.py:14` i `application/handlers/checklist/create_checklist_for_analysis_handler.py:15`.

**Zmiana:** jedna granica transakcji na operację biznesową; repozytoria używają `flush`, a commit/rollback/close kontroluje use case lub jednostka pracy. Najpierw poprawić zagrożone operacje, później migrować wzorzec stopniowo. `di/container.py:87` ma singleton sesji na instancję kontenera, a nie jedną globalną sesję wszystkich requestów; problemem jest brak jawnego kończenia jej życia. Generator `infrastructure/database/db.py:37` jest punktem odniesienia. Kontekstowe zarządzanie transakcją i sesją opisuje [SQLAlchemy Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html).

**Odbiór:** wymuszony błąd drugiego zapisu zachowuje stary zestaw i cofa pierwszy zapis; nieistniejący rodzic nie pozostawia osieroconej analizy/checklisty; po udanych i nieudanych requestach połączenia są zwalniane. Nie trzymać otwartej transakcji zapisu przez czas generacji LLM.

### Z02 — P1: wersjonowane migracje i naprawa brakującego FK

- [ ] Wybrać i wdrożyć jedno wykonywalne źródło migracji; proponowany Alembic, ponieważ zależność już istnieje. Dodać brakujące środowisko/revizje zamiast zakładać, że README opisuje gotową konfigurację.

**Dowód:** `backend/infrastructure/database/init_db.py:47` dodaje `page_requirements_id INTEGER` bez FK; `domain/models/page_blueprint/page_blueprint.py:24` deklaruje `ON DELETE CASCADE`. Odczyt istniejącej bazy potwierdza FK tylko do `page_strategy`, więc usunięcie wymagań może pozostawić blueprinty. Dodatkowo `backend/main.py:17` zmienia schemat podczas importu; `scripts/` zawiera osobne ręczne migracje.

**Zmiana:** inwentaryzacja schematu, kopia zapasowa i próba migracji na kopii, wykrycie istniejących osieroconych relacji, jawna polityka ich naprawy, odbudowa tabeli SQLite z wymaganym FK. Oddzielić utworzenie świeżej bazy od aktualizacji istniejącej; przenieść migrację poza import aplikacji. Procedura i rewizje mają być zapisane w repo; [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) opisuje wymagane środowisko migracyjne.

**Odbiór:** świeża i zmigrowana baza mają te same constraints; `PRAGMA foreign_key_check` jest puste; kasowanie PageRequirements obejmuje właściwą gałąź; ponowne uruchomienie nie zmienia schematu; sprawdzona procedura odtworzenia kopii. Nie kasować automatycznie wykrytych sierot.

### Z03 — P1: formularze nie mogą nadpisywać innego rekordu

- [ ] Naprawić tożsamość i cykl życia formularza oraz reset po utworzeniu oferty.

**Dowody:** `frontend/src/components/EditableFields.tsx:229,246,266` inicjuje `values` tylko przy montowaniu, a `DetailShell.tsx:77` nie wiąże komponentu kluczem z encją. Sonda po zmianie ID1 → ID2 wysłała nazwę i cenę ID1. W `pages/OffersPage.tsx:42` po `await` odczytywany jest już wyzerowany przez React `e.currentTarget`; rzeczywisty handler kończy się `TypeError` po utworzeniu rekordu.

**Zmiana:** stan formularza powiązany z typem i ID encji, zapis dozwolony tylko przy zgodności danych i ID trasy, aktualne dane konkretnego argumentu query. Uzgodnić zachowanie refetchu dla niezapisanych zmian, zamiast nadpisywać je bezwarunkowym efektem. Element formularza zachować przed `await`; blokować ponowny submit w trakcie zapisu.

**Odbiór:** szybkie przejście między dwiema encjami, refetch oraz powrót do edycji nie wysyłają starych danych. Sukces utworzenia zamyka/resetuje formularz, błąd zachowuje wpisane dane, pojedynczy submit daje jeden rekord.

### Z04 — P1/P2: spójny cache po mutacjach

- [ ] Uzupełnić invalidację lub aktualizację cache ustawień oraz relacji rodzic–dziecko.

**Dowody:** `frontend/src/features/settings/settingsApi.ts:45` i `:48` nie wiążą query z zapisem przez tag ani aktualizację cache. Sonda z prawdziwym RTK store: backend timeout=30, cache=20. `pages/SettingsPage.tsx:42,59,79,84` porównuje formularz ze starym wynikiem; powrót do 20 może zostać uznany za brak zmian. `pages/TargetAudienceEditPage.tsx:71` pomija `knowledgeId`, od którego zależy invalidacja rodzica w `features/targetAudiences/targetAudiencesApi.ts:67`.

**Zmiana:** jedna reguła odświeżania ustawień, wykorzystanie pełnej odpowiedzi mutacji lub tagów, poprawna synchronizacja formularza. Parent ID przekazywać jawnie albo wyprowadzać z odpowiedzi. Sprawdzić analogiczny kontrakt `saveOutputPrompt` i cache pozostałych relacji.

**Odbiór:** zmiana timeoutu 20 → 30 → 20 i reset do domyślnych zachowują zgodność formularza, flag override i serwera; zmiana grupy docelowej od razu aktualizuje widok Knowledge bez ręcznego przeładowania.

### Z05 — P1: kontrakt odpowiedzi LLM i poprawne zgłaszanie niepowodzenia

- [ ] Wprowadzić walidację wyniku przed zapisem i jednolitą obsługę błędów generowania, zaczynając od gałęzi Page.

**Dowody:** `backend/application/handlers/page_blueprint/generate_page_blueprint_handler.py:182` sprawdza głównie listę; prawdziwy handler zapisał `sections=[123]` przy wymaganej sekcji `hero`. `page_copy/generate_page_copy_handler.py:167` zwraca słownik błędu, a route `api/routes/general_routes.py:848` przekazuje go jako HTTP 200. Sam `json.loads` w generowaniu wiedzy również nie sprawdza pełnej struktury.

**Zmiana:** wspólna obsługa parse/validate, schematy wyników kolejnych etapów, walidacja elementów i wymaganych pól przed rozpoczęciem zapisu. Stosować `format` z JSON Schema w obsługiwanym lokalnym Ollama oraz nadal walidować po stronie aplikacji; mechanizm opisuje [Ollama Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs). Modele walidacyjne na granicy LLM nie wymagają przepisywania istniejących DTO. Reguły `required/excluded/position` wdrożyć jako jawną zmianę semantyki procesu, a nie tylko kosmetyczną poprawkę parsera.

**Odbiór:** zły JSON, lista liczb zamiast sekcji, brak wymaganych pól i niedozwolone typy nie tworzą rekordów. Błąd dostawcy daje określony status błędu, np. 502, i komunikat UI o niepowodzeniu. Rozróżnić błąd danych wejściowych, odpowiedzi modelu i zapisu. Ewentualna pojedyncza próba naprawy odpowiedzi ma limit i nie dubluje zapisu. Testy używają atrapy LLM.

### Z06 — P1/P2: walidacja wejścia, brakujących rekordów i pochodzenia danych

- [ ] Zastąpić dowolne słowniki edycji walidowanymi polami oraz sprawdzać zgodność relacji przed generowaniem.

**Dowody:** `backend/api/routes/general_routes.py:138` przyjmuje `fields: Dict[str, Any]`; np. `application/handlers/offers/update_offer_handler.py:14` nie sprawdza braku rekordu, a linia 18 używa `setattr` poza krótką denylistą. Literówka może dać sukces bez utrwalenia pola, a zły typ lub nieistniejące ID — 500. Modele ustawień dopuszczają tekstowy timeout i ujemny kontekst. `marketing_strategy/generate_marketing_strategy_handler.py:23,26,57` łączy niezależne `knowledge_id` i `brand_markeging_id`, nie sprawdzając wspólnej gałęzi.

**Zmiana:** jawne modele częściowych aktualizacji i listy dozwolonych pól, odrzucanie nadmiarowych kluczy, kontrola typów/range/null, jednolite 404 i walidacja relacji. ID przodków wyprowadzać z rekordu dziecka. Dla ustawień sprawdzać URL HTTP(S), dodatni timeout/kontekst i parametry modelu. `list_ollama_models_handler.py:21` powinien mieć jawny timeout; skonfigurowany timeout chat nie obejmuje tej osobnej instancji klienta.

**Odbiór:** literówka/zły typ → 422; brak ID → 404; błędna kombinacja wiedzy i marki zostaje odrzucona przed LLM; brak częściowego zapisu. Niedozwolona sekcja i pozycja spoza ustalonego zakresu nie docierają do repozytorium. Poprawna aktualizacja zachowuje pominięte pola.

### Z07 — P2: metody HTTP, uruchamianie i kontrakt API

- [ ] Zmienić mutujące GET na POST/DELETE/PATCH, ujednolicić błędy i zarejestrować router jeden raz.

**Dowody:** `backend/api/routes/general_routes.py:216,244,300` tworzy, usuwa i generuje przez GET; analogicznie kolejne etapy. `api/__routes__.py:14` rejestruje router w konstruktorze, po czym `main.py:15` powtarza operację — odtworzono 122 ostrzeżenia OpenAPI. Publicznie rejestrowany `/test` wywołuje nieistniejące API VLM w `application/handlers/test/test.py`.

**Zmiana:** frontend i backend zmieniać w jednej spójnej partii z testami kontraktu. Stare mutujące GET wyłączyć lub zakończyć czytelnym 405/410; nie pozostawiać aktywnych jako nieograniczonej kompatybilności. Ustalić semantykę retry i idempotencji generowania. Dodać fabrykę aplikacji bez inicjalizacji DB przy imporcie, osobną konfigurację dev/reload i diagnostyczny endpoint zdrowia/wersji. Usunąć lub odizolować zepsuty endpoint testowy.

**Odbiór:** żaden GET nie zmienia danych; powtórzenie generowania ma określony skutek; OpenAPI nie zgłasza duplikatów; import aplikacji nie wykonuje DDL. Zachować poprawne synchroniczne `def` tam, gdzie używane są synchroniczne biblioteki — samo zastąpienie ich `async def` nie rozwiązuje długich operacji; [FastAPI opisuje wykonanie zwykłych handlerów w puli wątków](https://fastapi.tiangolo.com/async/).

## Zadania — zależności, środowisko i dostęp

### Z08 — P2: uporządkować zależności i rozpatrzyć zgłoszenia npm

- [ ] Wykonać ocenę zastosowania zgłoszeń, kontrolowane aktualizacje lockfile oraz skan podatności Pythona w odtwarzalnym środowisku.

Wynik npm z 2026-09-07 obejmuje następujące pakiety; severity jest wartością narzędzia:

| Severity | Pakiety zgłoszone przez npm |
| --- | --- |
| high | `brace-expansion`, `browserslist`, `fast-uri`, `ip-address`, `js-yaml`, `nanoid`, `react-router`, `react-router-dom`, `undici` |
| moderate | `@hono/node-server`, `hono`, `postcss`, `qs` |

**Kontekst:** `frontend/package.json:29` zawiera `shadcn` w dependencies. `npm ls` pokazuje przez niego m.in. `@modelcontextprotocol/sdk → @hono/node-server/hono/ajv/fast-uri` i `undici`. Obecność tych pakietów w drzewie produkcyjnym npm nie dowodzi obecności ich kodu serwerowego w statycznym bundle przeglądarki. Przejście `shadcn` do devDependencies, jeżeli potwierdzi to użycie, poprawi klasyfikację, ale nie usunie konieczności audytu narzędzi.

`react-router-dom/react-router` mają 7.18.1. Zgłoszenie [GHSA-qwww-vcr4-c8h2 autorów React Router](https://github.com/remix-run/react-router/security/advisories/GHSA-qwww-vcr4-c8h2) dotyczy niestabilnych API RSC i wskazuje poprawioną wersję 7.18.2 w linii 7. Kod `frontend/src/main.tsx:12` używa BrowserRouter; nie znaleziono RSC, więc nie potwierdzono osiągalności tego scenariusza w aplikacji. Zaplanować zgodną aktualizację linii 7 i lockfile, a pozostałe zgłoszenia sklasyfikować według rzeczywistego użycia, zamiast wykonywać zbiorcze `audit fix --force`.

Backend: `requirements.txt:10,24` zawiera dwa pakiety DOCX. Kod parsera potrzebuje `from docx import Document`, API udokumentowanego przez [python-docx](https://pypi.org/project/python-docx/). Po teście parsowania pozostawić jedną potrzebną dystrybucję; [docx 0.2.4](https://pypi.org/project/docx/) jest osobną starą dystrybucją. Lokalny import obecnie działa — to porządkowanie i ograniczenie ryzyka, nie odtworzona awaria.

**Odbiór:** aktualizacje nie łamią lint/build i regresji; każdy pozostawiony alert ma uzasadnienie, zakres i termin ponownego sprawdzenia. `npm audit` obejmuje także dev tools, raport Python jest zapisany; nie utożsamiać `pip check` z brakiem CVE. Oddzielić zależności bezpośrednie od wygenerowanego zestawu wersji i nie podnosić zbiorczo majorów bez potrzeby.

### Z09 — P1 przed udostępnieniem: konfiguracja, dane lokalne i dostęp do API

- [ ] Ustalić tryb użytkowania i dostosować do niego konfigurację sieci oraz zasady przechowywania danych.

**Dowody:** `backend/core/settings.py:12` domyślnie binduje `0.0.0.0`; `api/__routes__.py:25` ustawia CORS `*` i credentials; brak mechanizmu auth dla usuwania, ustawień i generowania. `settings/list_ollama_models_handler.py:10` przyjmuje adres docelowy od klienta. `git ls-files` potwierdza śledzenie `backend/.env` i `backend/app.db`; `.gitignore:3,9` ma zakomentowane reguły dla bazy i env. Nie stwierdzono ujawnienia kluczy ani publicznej dostępności repo/usługi.

**Zmiana:** dla osobistego narzędzia lokalnego proponowany domyślny localhost i jawne dozwolone originy; dla LAN/zespołu dodać uwierzytelnianie i kontrolę dostępu, zwłaszcza do ustawień adresu modelu. Zachować możliwość świadomego skonfigurowania lokalnego/remote Ollama. Wprowadzić `.env.example`, dane przykładowe i politykę kopii bazy. Przyszłe wyłączenie plików z Git ma zachować lokalne pliki i dane. Zmiana ignore sama nie usuwa plików już śledzonych ani ich historii.

**Odbiór:** tryb lokalny i ewentualny współdzielony mają opisane i sprawdzone granice dostępu; konfiguracja instancji nie trafia do nowych commitów; świeży klon uruchamia się z dokumentacji i przykładowych danych. Ewentualne czyszczenie historii rozpatrzyć osobno po ocenie zawartości, bez zakładania wycieku.

## Zadania — proces pracy agenta i dokumentacja

### Z10 — P1: jedna poprawna ścieżka konfiguracji projektów

- [ ] Ujednolicić nazwę `projects/PROJECTS.md` we wszystkich dokumentach i fizycznej strukturze albo świadomie wybrać obecną nazwę `project/PROJECTS.md`.

**Dowody:** `agent-workspace/ROOT_PROMPT.md:22,140,1157` wskazuje brakujący katalog; rzeczywisty `project/PROJECTS.md:1` zawiera prozę. `output/README.md:28` kieruje kod do `../project`, czyli katalogu konfiguracji; `README.md:7` repo odsyła do nieistniejącego flow. `project/README.md` tej kopii używa `PROJECTS.md`, nie `PROJECT.md`.

**Zmiana:** rekomendowana nazwa zgodna z ROOT: `projects/PROJECTS.md`, stabilny identyfikator projektu oraz ścieżka absolutna lub względna z jawną bazą. Dla obecnego położenia zapisać np. `../../` z jednoznacznym stwierdzeniem „względem katalogu zawierającego PROJECTS.md”. Poprawić link do pamięci flow, wskazówki umieszczania kodu, uszkodzone fence w ROOT:87 i `project/README.md:17` oraz pozostałość dialogu w tym README:60.

**Odbiór:** ten sam root projektu rozwiązuje się niezależnie od cwd sesji; wszystkie aktywne lokalne odwołania istnieją; katalog konfiguracji nie jest mylony z kodem. Dodać mały walidator linków/ścieżek, z rozróżnieniem rzeczywistych odwołań od ilustracyjnych przykładów.

### Z11 — P2: skrócić ROOT i doprecyzować zakres instrukcji

- [ ] Zastąpić powtórzenia krótkim punktem wejścia i procedurami ładowanymi zależnie od zadania.

**Dowody:** ROOT ma 2255 linii, wiele wersji workflow (`:1140,1173,1213,2092,2136`) i dwie hierarchie (`:1348,1971`). Sekcje `:514,531,675` deklarują szerokie uprawnienia do zmiany/usuwania dokumentów; priorytety pomijają nadrzędne instrukcje środowiska. `:1365` może kolidować z aktualnym poleceniem zmiany dawnej reguły.

**Zmiana:** jedna hierarchia uwzględniająca instrukcje systemu i środowiska, aktualną prośbę użytkownika i zakres udzielonego upoważnienia. Jawne tryby: przegląd/planowanie/implementacja; przeczytanie dokumentu, referencji lub starego planu nie uruchamia zapisanych działań. ROOT pozostawia wybór projektu, mapę kontekstu, granice zmian i definicję zakończenia; szczegółowy onboarding oraz procedury trafiają do osobnych plików. Dla małego zadania inicjalizacja ma być proporcjonalna.

**Odbiór:** brak sprzecznych hierarchii i powielonych norm; testowe scenariusze „audyt bez implementacji”, „aktualna zmiana starej reguły”, „dwa projekty” oraz „brak ścieżki” prowadzą do jednoznacznego zakresu pracy. Nie usuwać ważnych ograniczeń podczas skracania.

### Z12 — P2: świeża pamięć, zamykane plany i uczciwa polityka Git

- [ ] Zweryfikować i poprawić nieaktualne fakty, nadać planom statusy oraz uzgodnić wersjonowanie kontekstu.

**Dowody:** `memory/ai-ec-agent/project-understanding.md:39` wskazuje `b942f16`. `application-flow.md:48,98` przypisuje usługom rekurencyjne składanie wszystkich przodków, podczas gdy np. `marketing_strategy_service.py:45` serializuje własne DTO, a handler jawnie składa fragmenty. Plan eksportu `2026-09-04_10-35_pipeline-path-download-button.md:14` nadal mówi o braku UI, mimo istniejącego przycisku i sidebaru. README katalogów deklarują lokalność pamięci/planów/referencji, ale wszystkie reguły workspace `.gitignore` są komentarzami i materiały są śledzone.

**Zmiana:** dokumenty otrzymują `verified_at`, commit oraz konkretny zakres źródeł. Start kolejnej pracy sprawdza zmiany tych źródeł i bieżący dirty state; nie podbijać globalnego „verified commit” po drobnym przeglądzie. Plan ma status, checklistę, ostatnią aktualizację, wynik kontroli i pozostałe prace. Eksport oznaczyć jako zaimplementowany w kodzie, a niewykonanej walidacji przeglądarkowej nie dopisywać jako sukcesu.

Wersjonować uzgodnioną wiedzę, reguły i szablony; jawnie określić prywatne materiały i scratch. Ograniczenia w `CODE.md:42,45` mają mieć pochodzenie: obserwowany wzorzec jest domyślną konwencją, nie nową regułą użytkownika. Dopiero rzeczywiste obowiązkowe ograniczenia przenosić do `rules/`. Nie oznaczać jako nadal zepsutego timeoutu chatu, który obecny `OllamaService` już przekazuje do klienta.

**Odbiór:** opis tworzenia kontekstu zgadza się z kodem, stare plany nie sugerują ponownej implementacji gotowego eksportu, `git ls-files`/`git check-ignore` zgadzają się z README. Brak nadpisanej historii decyzji lub przypisanych użytkownikowi nieistniejących zakazów.

### Z13 — P1/P2: odtwarzalne uruchamianie i testy zachowania

- [ ] Ustalić wersję runtime, wspólny runbook Windows/POSIX i minimalne CI dla ryzyk wykrytych w audycie.

**Dowody:** `backend/README.md:4` mówi Python 3.14, venv działa na 3.10.0; `CODE.md:23` daje głównie komendy bash; brak test suites i CI. Historyczny plan proponuje `npx tsc --noEmit`, choć `frontend/tsconfig.json` ma `files: []` i references, a właściwy skrypt już wykonuje `tsc -b`. Import `main` zmienia DB.

**Zmiana:** sprawdzić kompatybilność i zadeklarować wspierany Python oraz Node w plikach konfiguracyjnych i README. Dokumentować bezpośrednie wywołanie `backend/venv/Scripts/python.exe` na Windows oraz odpowiednik POSIX. W odtwarzalnej instalacji frontendu używać lockfile (`npm ci`). Rozdzielić testy z atrapą modelu od małego, jawnie uruchamianego smoke testu prawdziwego Ollama.

**Minimalny zestaw:** regresje Z01–Z06; API success/error/not-found i metody HTTP; test migracji świeżej/starej bazy; frontend tworzenie/edycja/cache; eksport pipeline dla ADS, UGC, PAGE i starego blueprintu bez `page_requirements_id`. W procesie CI uruchamiać backend tests, `pip check`, frontend lint/build/tests i audyty zależności. Nie wprowadzać arbitralnego progu pokrycia, który nagradza testy powtarzające implementację.

**Odbiór:** czysty checkout daje powtarzalne wyniki na deklarowanym środowisku; testy nie wymagają prywatnego `.env`, realnych ID, działającego modelu ani zapisu do `app.db`. Procesy testowe mają rozpoznawalny PID/port/wersję, a sprzątanie obejmuje tylko zasoby danego uruchomienia.

## Zadania — użyteczność i jakość procesu generowania

### Z14 — P2: listy, edycja i obsługa nieudanych operacji

- [ ] Naprawić poniższe potwierdzone statycznie przypadki i dodać po jednym odpowiednim scenariuszu regresji.

| Problem / lokalizacja | Zmiana | Odbiór |
| --- | --- | --- |
| `frontend/src/pages/OffersPage.tsx:19`, `features/offers/offersApi.ts:31`, backend `offers_repository.py:23` — zawsze strona 1 z limitem 20 | Paginacja w URL, `total_items`, stabilne `ORDER BY` backendu | 21+ ofert dostępnych; usunięcie ostatniej pozycji strony nie pozostawia bezużytecznej pustej strony. |
| `pages/AdExecutionDetailPage.tsx:31,65,69` usuwa `video` również z danych formularza | Formatowanie tylko prezentacji, zapis zmienionych pól | Edycja nazwy nie zmienia `video 9:16` w `9:16`. |
| `pages/OfferDetailPage.tsx:132` nawiguje po `.then` mutacji również dla wyniku z błędem | `unwrap()` i nawigacja po sukcesie | HTTP 500 pozostawia szczegóły; sukces wraca do listy. |
| `components/EntityList.tsx:47,63,78` klucz ulubionych oparty tylko o pathname/ID | Typ encji i stabilny zakres w kluczu; ustalona rola istniejącego `is_favorite` backendu | Analiza #1 i Brand marketing #1 nie nadpisują swoich oznaczeń. |

### Z15 — P2: jawna polityka faktów i ręcznej akceptacji

- [ ] Uzgodnić i wdrożyć znaczenie `fact_status` oraz `review_status` w przechodzeniu do kolejnych etapów.

**Dowód:** `backend/application/services/knowledge_service.py:45` serializuje całe assembled DTO, a `application/dtos/knowledge/knowledge_dto.py:40` i `knowledge_insight_dto.py:35` przekazują także statusy, bez filtrowania. Niezweryfikowane, sporne i odrzucone treści mogą zostać kontekstem następnego kroku. To istniejące zachowanie; wybór blokady jest decyzją produktową, nie dotąd potwierdzonym wymaganiem.

**Propozycja:** pozwolić na robocze generowanie z jawnie oznaczonymi hipotezami, a dla treści przeznaczonych do publikacji wymagać uzgodnionej akceptacji. Wykluczenie `rejected/disputed` powinno być świadomą polityką z komunikatem o brakach. Dodać źródło dowodu dla twierdzenia, osobę/czas weryfikacji oraz rozróżnienie faktu, hipotezy i pomysłu reklamowego. Po zmianie danych źródłowych oznaczać zależne wyniki jako wymagające przeglądu; nie regenerować ich automatycznie kosztem pracy użytkownika.

**Odbiór:** test macierzy statusów pokazuje jednoznacznie, co trafia do kontekstu w trybie roboczym i zatwierdzonym; brak dowodów nie jest zastępowany zmyślonym twierdzeniem; użytkownik widzi przyczynę blokady i zakres nieaktualnych wyników.

### Z16 — P2/P3: historia generacji, budżet kontekstu i pomiar jakości

- [ ] Zapisywać metadane wykonania i odróżnić kontekst historyczny od odtworzonego z aktualnych danych.

**Dowody:** `backend/application/services/ollama_service.py:36,47` zachowuje głównie treść odpowiedzi, tracąc statystyki i parametry wykonania. `page_copy/generate_page_copy_handler.py:92` składa wiele warstw kontekstu bez wspólnego budżetu. `infrastructure/ai/token_counter.py:3,15` liczy dla domyślnego modelu GPT i uruchamia demonstracyjny print; nie stanowi wiarygodnego limitera tokenów aktualnego modelu Ollama. `get_pipeline_path_handler.py:160` odtwarza dane obecne, nie zapisany prompt historycznego wywołania.

**Zmiana:** rekord generacji z identyfikatorem, etapem, wersją/hash promptów, modelem i dostępną rewizją, parametrami, ID/wersjami źródeł, czasem, wynikiem walidacji i wynikiem operacji. Statystyki tokenów/czasów czerpać z dostępnej odpowiedzi serwera — [Ollama Chat API](https://docs.ollama.com/api/chat). Zakres przechowywania pełnych promptów/odpowiedzi i retencję ustalić osobno; same hashe nie odtwarzają usuniętych danych. Eksport oznaczyć jako bieżący albo historyczny, z czasem i wersją formatu.

Wprowadzić budżet wejścia z rezerwą na wyjście i jasną strategią redukcji; nie obcinać po cichu faktów/wymagań. Mierzyć powtarzane zapytania i fragmenty przed cache'owaniem. Ewentualny cache kluczować wersją danych i promptu. Dla stałego małego zbioru referencyjnych ofert porównywać walidowalność, zgodność sekcji, poparcie twierdzeń, liczbę ponowień, czas i zużycie tokenów; nie oceniać jakości wyłącznie długością promptu lub subiektywną oceną tekstu.

**Odbiór:** wiadomo, z jakich danych i ustawień powstał konkretny wynik; eksport nie udaje historycznego dowodu, jeśli rekonstruuje aktualny stan; za duży kontekst ma przewidywalną obsługę. Zmiana promptu/modelu ma raport na tym samym zbiorze przypadków.

### Z17 — P3: długie zadania, retry i wznowienie

- [ ] Po ustabilizowaniu Z01/Z05/Z07 wprowadzić rejestrowane zadania generowania z postępem, anulowaniem i polityką retry.

**Uzasadnienie:** obecne generowanie działa wewnątrz żądania HTTP i może trwać do timeoutu modelu. Przerwanie widoku lub powtórzenie żądania nie stanowi trwałego protokołu sterowania. Wyczerpania puli ani opóźnień pod obciążeniem nie mierzono, dlatego dobór mechanizmu wykonawczego wymaga pomiaru.

**Propozycja:** POST zwraca ID zadania; stany queued/running/succeeded/failed/cancelled; frontend odczytuje status. Idempotency key dotyczy tej samej próby, a jawne „wygeneruj nowy wariant” tworzy nową próbę. Ograniczyć równoległość do możliwości modelu; zdefiniować wznowienie po restarcie i uniknąć transakcji DB otwartej przez całe wywołanie LLM. Nie wybierać Redis/Celery ani mikroserwisów bez wykazanej potrzeby.

**Odbiór:** odświeżenie UI nie gubi zadania; ponowienie tego samego żądania nie dubluje zapisu; restart daje znany status i możliwość bezpiecznego wznowienia. Limit równoległości i anulowanie mają testowane znaczenie.

### Z18 — P2/P3: mniejsze defekty i stopniowe ograniczenie długu technicznego

- [ ] Poprawić małe defekty kontraktu, a refaktoryzacje wykonywać po dodaniu ochrony dla ich zachowania.

**P2:** `backend/application/handlers/checklist/create_checklist_for_analysis_handler.py:21` zwraca `AnalysisMapper.to_dto(checklist_dto)` zamiast checklisty — odpowiedź powinna zachować m.in. `name`. `infrastructure/repositories/knowledge_analysis_repository.py:28` odwołuje się przy ponownym upsert do nieistniejących `content/updated_at`; dwukrotne przypięcie tej samej pary ma zachować poprawną istniejącą relację.

**P3:** wprowadzać typowane kontrakty frontend/API i `strict` modułami, zaczynając od edycji i generowania; nie masowo dodawać rzutowań. Rozdzielić rozbudowany router na moduły domenowe po ustabilizowaniu OpenAPI. Ładowanie tras na żądanie rozważyć po pomiarze czasu startu, mając obecne ostrzeżenie bundle jako punkt wyjścia. Usunąć potwierdzony martwy kod i demonstracyjne import-time efekty, poprawić komunikaty pustych widoków, 404 i powrót do rodzica. Nie uznawać rozmiaru pliku lub braku dashboardu za ważniejszy problem niż integralność danych.

**Odbiór:** kontrakt checklisty jest właściwy; dwukrotny upsert nie podnosi wyjątku; typy wykrywają zmianę pola API; optymalizacje mają porównanie przed/po i nie pogarszają nawigacji.

## Decyzje potrzebne przy realizacji, bez blokowania obecnego planu

1. Czy aplikacja pozostaje osobistym narzędziem lokalnym, czy będzie udostępniana w LAN/zespołowi? To określa wariant Z09.
2. Jaka jest polityka zachowania danych po usunięciu rodzica i naprawy już osieroconych rekordów? Obecne modele sugerują kaskadę; potwierdzić przed Z02 na rzeczywistej bazie.
3. Które statusy faktów/akceptacji dopuszczają generację roboczą i publikacyjną? Ustalić przed Z15.
4. Czy pełne prompty/odpowiedzi i materiały biznesowe mają być utrwalane, przez jaki czas i w jakim miejscu? Dotyczy Z09/Z12/Z16.

## Warunki zamknięcia planu

- [ ] Każde rozpoczęte zadanie ma właściciela, wynik i dowody walidacji; pozostały backlog jest jawnie oznaczony.
- [ ] Poprawki P1 mają regresje odtwarzające konkretne scenariusze z audytu.
- [ ] Migracje zweryfikowano na kopii i świeżej bazie, a procedurę odtworzenia sprawdzono przed zmianą danych użytkownika.
- [ ] API, frontend i raporty zależności są zgodne; nieudane generowanie nie jest raportowane jako sukces.
- [ ] README, konfiguracja projektów, pamięć i historyczne plany opisują rzeczywisty stan oraz granice wykonanej walidacji.

Ten dokument jest wynikiem audytu i propozycją kolejnych prac. Jego zapis nie oznacza wykonania ani zatwierdzenia wszystkich proponowanych zmian produktu i architektury.
