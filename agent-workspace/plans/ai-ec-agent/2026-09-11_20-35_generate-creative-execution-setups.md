# Goal

Status: IMPLEMENTED (2026-09-11)

Dodać generowanie wielu `CreativeExecutionSetup` przez LLM na podstawie istniejącego łańcucha:

```text
AdStrategy → CreativeStrategy → AdSetup
```

Użytkownik ma podać liczbę różnych konfiguracji, które system powinien przygotować. Wygenerowane rekordy mają korzystać z istniejących katalogów `AdFramework`, `CreativeAngle` i `ExecutionStyle`, pasować do medium/platformy z `AdSetup` oraz od razu pojawić się na istniejącej liście konfiguracji.

# Current State

- `CreativeExecutionSetup` jest dziś tworzony wyłącznie ręcznie przez `POST /ad-setup/{ad_setup_id}/creative-execution-setups/create`.
- Formularz ręczny w `frontend/src/pages/ResourcePages.tsx` pozwala wybrać nazwę, długość/liczbę slajdów, framework, angle, execution style i dodatkowe instrukcje.
- Model przechowuje dokładnie pola potrzebne do generowania: `name`, `duration_seconds`, `number_of_slides`, `ad_framework_id`, `creative_angle_id`, `execution_style_id`, `additional_instructions` — zmiana schematu bazy nie jest potrzebna.
- Backend ma już serwisy `build_llm_context()` dla `AdStrategy`, `CreativeStrategy` i `AdSetup`.
- Katalogi frameworków, kątów i stylów są statycznymi JSON-ami obsługiwanymi przez istniejące repozytoria i serwisy.
- `GenerateAd` korzysta potem z zapisanej konfiguracji i całego łańcucha upstream, więc wygenerowane setupy będą zgodne z dalszym etapem bez zmiany jego kontraktu.
- Repozytorium `CreativeExecutionSetupRepository.create()` wykonuje osobny commit dla każdego rekordu; generowanie wielu elementów wymaga operacji zbiorczej, aby nie pozostawiać częściowego wyniku.
- Brak automatycznych testów w projekcie; walidacja musi objąć build/lint frontendu, kompilację/import backendu i ręczne wywołania endpointu.

# Product Behavior

Na stronie `/ad-setup/:id/creative-execution-setups` użytkownik otrzyma dwie rozdzielone akcje:

1. `Generuj konfiguracje` — otwiera prawy panel z polem `Liczba konfiguracji`.
2. `Dodaj ręcznie` — zachowuje obecny formularz i pełną kontrolę użytkownika.

Formularz generowania:

- pole liczbowe, domyślnie `3`;
- minimum `1`, maksimum `10`;
- krótkie wyjaśnienie, że konfiguracje zostaną dopasowane do bieżących strategii, medium i platformy;
- przycisk pokazujący stan generowania i blokujący ponowne wysłanie;
- po sukcesie panel się zamyka, cache listy jest unieważniany, a wszystkie nowe rekordy pojawiają się na liście;
- po błędzie panel pozostaje otwarty i wyświetla komunikat.

Limit `10` ogranicza koszt i ryzyko niestabilnej, zbyt długiej odpowiedzi LLM, a nadal pozwala wygenerować sensowny zestaw wariantów w jednym przebiegu.

# API Contract

Dodać endpoint:

```http
POST /ad-setup/{ad_setup_id}/creative-execution-setups/generate
Content-Type: application/json

{
  "count": 3
}
```

Request będzie osobnym modelem Pydantic, np.:

```python
class GenerateCreativeExecutionSetupsRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=10)
```

Response: lista utworzonych `CreativeExecutionSetupDto`, zgodna z istniejącym endpointem listującym:

```json
[
  {
    "id": 101,
    "ad_setup_id": 12,
    "name": "Problem–solution UGC",
    "duration_seconds": 20,
    "number_of_slides": null,
    "ad_framework_id": "problem_solution",
    "creative_angle_id": "relatability",
    "execution_style_id": "ugc_creator",
    "additional_instructions": "...",
    "ad_framework": {},
    "creative_angle": {},
    "execution_style": {}
  }
]
```

Endpoint generuje dodatkowe rekordy. Nie usuwa, nie aktualizuje i nie zastępuje istniejących konfiguracji.

# Backend Design

## Handler

Dodać `application/handlers/creative_execution_setup/generate_creative_execution_setups_handler.py` zgodnie z istniejącym wzorcem handlerów generujących.

Handler:

1. Pobiera `AdSetup` po `ad_setup_id`.
2. Przez `ad_setup.creative_strategy_id` pobiera `CreativeStrategy`.
3. Przez `creative_strategy.ad_strategy_id` pobiera `AdStrategy`.
4. Buduje trzy jawnie oznaczone sekcje kontekstu z istniejących `build_llm_context()`.
5. Pobiera komplet katalogów frameworków, creative angles i execution styles.
6. Filtruje frameworki do pozycji zgodnych z `ad_setup.creative_type`; katalogi medium-agnostic przekazuje w całości.
7. Pobiera istniejące `CreativeExecutionSetup` dla danego `AdSetup` i przekazuje ich zwięzłe kombinacje do promptu jako listę antyduplikacyjną.
8. Wywołuje LLM dokładnie raz z żądaną liczbą konfiguracji.
9. Parsuje odpowiedź JSON, waliduje cały wynik, a dopiero potem zapisuje wszystkie rekordy atomowo.
10. Zwraca kompletne DTO z rozwiniętymi referencjami katalogowymi.

Nie należy wciągać całego wcześniejszego łańcucha oferty/marketingu do tego promptu. `AdStrategy` i `CreativeStrategy` są już zawężonym źródłem decyzji strategicznych, a użytkownik wskazał dokładnie te trzy poziomy. Ogranicza to tokeny i ryzyko ponownego wymyślania strategii.

## Prompt and Output Schema

System prompt powinien definiować rolę planera egzekucji reklamowej i jasno rozdzielać odpowiedzialności:

- `AdStrategy` określa cel, koncepcję i ograniczenia reklamowe;
- `CreativeStrategy` określa wybraną ideę, angle komunikacyjny, hook i przebieg emocji;
- `AdSetup` określa medium (`video`/`image`/`carousel`), platformę i format;
- wygenerowany setup wybiera jedynie sposób wykonania z dozwolonych katalogów, bez przepisywania strategii i bez tworzenia gotowej reklamy.

Wymagany output:

```json
{
  "creative_execution_setups": [
    {
      "name": "",
      "duration_seconds": null,
      "number_of_slides": null,
      "ad_framework_id": "",
      "creative_angle_id": "",
      "execution_style_id": "",
      "additional_instructions": ""
    }
  ]
}
```

Reguły promptu:

- zwróć dokładnie `count` elementów;
- konfiguracje mają być realnie różne pod względem kombinacji framework + angle + style i sposobu wykonania, nie tylko nazwy;
- nie duplikuj już istniejących konfiguracji;
- używaj wyłącznie identyfikatorów przekazanych w katalogach;
- framework musi być kompatybilny z `AdSetup.creative_type`;
- dla `video`: `duration_seconds` ma być sensowną dodatnią liczbą, `number_of_slides = null`;
- dla `carousel`: `number_of_slides` ma być sensowną dodatnią liczbą, `duration_seconds = null`;
- dla `image`: oba pola mają być `null`;
- `additional_instructions` ma opisywać różnicującą egzekucję, ale nie może wymyślać faktów, claims, cen, proof ani parametrów produktu;
- nazwa ma krótko identyfikować wariant;
- odpowiedź ma zawierać wyłącznie JSON.

## Validation Before Save

Backend nie może ufać samemu promptowi. Przed zapisem sprawdzić:

- root jest obiektem, a `creative_execution_setups` listą;
- liczba elementów jest dokładnie równa `count`;
- każdy element jest obiektem i ma niepustą nazwę;
- wszystkie identyfikatory istnieją w odpowiednich katalogach;
- wybrany framework jest zgodny z creative type;
- pola `duration_seconds`/`number_of_slides` odpowiadają medium;
- wartości liczbowe mieszczą się w rozsądnych granicach (propozycja: video 5–120 s, carousel 2–20 slajdów);
- nie ma duplikatów w obrębie odpowiedzi ani względem istniejących setupów według klucza `(ad_framework_id, creative_angle_id, execution_style_id, duration_seconds, number_of_slides)`.

Jeżeli odpowiedź jest błędna, nie zapisywać żadnego rekordu i zwrócić kontrolowany błąd. Nie zwracać surowej odpowiedzi LLM do klienta; można ją zapisać w logu, jeśli obecny logger na to pozwala bez ujawniania danych wrażliwych.

## Atomic Persistence

Rozszerzyć `CreativeExecutionSetupRepository` o `create_many(items)`:

- `add_all`;
- jeden `commit`;
- `rollback` przy wyjątku;
- odświeżenie utworzonych encji po sukcesie.

Handler najpierw waliduje cały payload, potem tworzy encje i zapisuje je jednym wywołaniem. Dzięki temu awaria czwartego rekordu nie pozostawi pierwszych trzech w bazie.

# Frontend Design

## RTK Query

W `features/creativeExecutionSetup/creativeExecutionSetupApi.ts` dodać mutację:

```ts
generateCreativeExecutionSetups: builder.mutation<
  Entity[],
  { adSetupId: number; count: number }
>
```

Po sukcesie unieważnić `listTag('CreativeExecutionSetup', adSetupId)`. Nie trzeba unieważniać rodzica `AdSetup`, ponieważ generowanie go nie zmienia.

## UI

Wydzielić formularze związane z konfiguracjami z rosnącego `ResourcePages.tsx` do pliku feature/component, np.:

```text
frontend/src/features/creativeExecutionSetup/
├── creativeExecutionSetupApi.ts
├── GenerateCreativeExecutionSetupsForm.tsx
└── CreativeExecutionSetupForm.tsx
```

`GenerateCreativeExecutionSetupsForm` zawiera pole count i obsługuje mutację. Obecny ręczny `CreativeExecutionSetupForm` należy przenieść bez zmiany zachowania, aby obie ścieżki były jasno rozdzielone.

Na liście dodać dwie akcje. Najczyściej rozszerzyć `ResourceList` o opcjonalny `additionalActions: ReactNode` (lub ogólnie `actions`) i przekazać go dalej do nagłówka `EntityList`, zamiast tworzyć niestandardowy nagłówek tylko dla jednej strony:

- główna akcja: `Generuj konfiguracje`;
- akcja dodatkowa: `Dodaj ręcznie`.

Nie zastępować manualnego formularza generowaniem, ponieważ ręczna konfiguracja nadal jest potrzebna do precyzyjnych eksperymentów.

# Files / Components Involved

Backend:

- `backend/api/routes/general_routes.py`
- `backend/application/handlers/creative_execution_setup/generate_creative_execution_setups_handler.py` — nowy
- `backend/infrastructure/repositories/creative_execution_setup_repository.py`
- opcjonalnie mały moduł parsera/walidatora obok handlera, jeśli handler zrobi się zbyt długi

Frontend:

- `frontend/src/features/creativeExecutionSetup/creativeExecutionSetupApi.ts`
- `frontend/src/features/creativeExecutionSetup/GenerateCreativeExecutionSetupsForm.tsx` — nowy
- `frontend/src/features/creativeExecutionSetup/CreativeExecutionSetupForm.tsx` — wydzielony z `ResourcePages.tsx`
- `frontend/src/pages/ResourcePages.tsx`
- `frontend/src/components/ResourceList.tsx` — tylko rozszerzenie API nagłówka o dodatkową akcję

Bez zmian:

- modele i DTO `CreativeExecutionSetup`;
- schema bazy i migracje;
- generowanie finalnego `GenerateAd`;
- istniejący endpoint ręcznego tworzenia.

# Implementation Steps

1. Dodać model requestu i trasę `POST .../generate`.
2. Zaimplementować handler: pobranie trzech poziomów, katalogów i istniejących setupów, budowa promptu, jedno wywołanie LLM.
3. Dodać ścisłe parsowanie i walidację odpowiedzi.
4. Dodać atomowy `create_many` i zapisywać dopiero po pełnej walidacji.
5. Dodać mutację RTK Query z prawidłową invalidacją listy.
6. Wydzielić obecny formularz ręczny i utworzyć formularz generowania z count 1–10.
7. Udostępnić na liście osobne akcje „Generuj konfiguracje” i „Dodaj ręcznie”.
8. Zweryfikować sukces, walidację wejścia, błędy LLM, brak duplikatów oraz brak częściowego zapisu.
9. Zaktualizować `memory/ai-ec-agent/application-flow.md` i `architecture.md` po implementacji.

# Validation

Backend:

- `python -m compileall` dla zmienionych modułów;
- uruchomienie/import aplikacji z uwzględnieniem faktu, że import `main.py` wykonuje `init_db()`;
- requesty z `count`: `0`, `1`, wartość domyślna `3`, `10`, `11`;
- nieistniejący `ad_setup_id`;
- mock/odpowiedź LLM z błędnym JSON-em, złą liczbą elementów, nieznanym ID katalogowym, złą wartością duration/slides i duplikatem;
- potwierdzenie, że przy błędzie liczba rekordów w bazie się nie zmienia;
- poprawna odpowiedź dla `video`, `image` i `carousel`.

Frontend:

- `npm run lint`;
- `npm run build`;
- ręcznie: otwarcie panelu, walidacja 1–10, loading, błąd, sukces, zamknięcie i automatyczne odświeżenie listy;
- ręcznie: działanie niezależnego przycisku „Dodaj ręcznie”.

# Risks and Decisions

- Jedno wywołanie generujące 10 rekordów może zwrócić mniej elementów. Nie dopisywać brakujących automatycznie i nie wykonywać ukrytego retry w pierwszej wersji — cały request kończy się błędem bez zapisu. Retry można dodać później jako świadomą decyzję kosztową.
- Wymóg unikalności jest ograniczony liczbą sensownych kombinacji zgodnych z medium. Jeżeli użytkownik zażąda więcej wariantów niż model potrafi uczciwie zróżnicować, lepszy jest kontrolowany błąd niż pozorne duplikaty.
- `additional_instructions` generowane przez LLM będą instrukcjami wykonawczymi, nie wejściem użytkownika. Prompt i walidacja semantyczna muszą zabraniać dodawania nowych faktów oraz obietnic.
- Nie należy zmieniać istniejących ustawień podczas generowania kolejnej partii; istniejące rekordy służą wyłącznie jako kontekst antyduplikacyjny.

# Assumptions

- „Ile różnych konfiguracji” oznacza liczbę nowych `CreativeExecutionSetup` utworzonych w jednym żądaniu, nie liczbę wszystkich konfiguracji po operacji.
- Generowanie odbywa się z poziomu konkretnego `AdSetup`, więc relacje do `CreativeStrategy` i `AdStrategy` są jednoznacznie wyznaczane przez klucze obce.
- Użytkownik chce zachować możliwość ręcznego tworzenia konfiguracji obok nowej funkcji generowania.

# Implementation Result

- Dodano `POST /ad-setup/{ad_setup_id}/creative-execution-setups/generate` z requestem `count` 1–10.
- Handler pobiera `AdStrategy`, `CreativeStrategy`, `AdSetup`, kompatybilne katalogi oraz istniejące konfiguracje i wykonuje jedno wywołanie LLM.
- Cała odpowiedź jest walidowana przed zapisem; kontrolowane są liczba, katalogowe ID, medium-specific fields oraz duplikaty.
- Repozytorium zapisuje partię przez `create_many()` w jednej transakcji z rollbackiem.
- Frontend ma osobny panel generowania z polem liczby oraz zachowaną akcję „Dodaj ręcznie”.
- `ResourceList` obsługuje teraz opcjonalne dodatkowe akcje nagłówka bez tworzenia niestandardowej listy.

# Completed Validation

- [x] Backend: `venv/Scripts/python.exe -m compileall` dla zmienionych modułów.
- [x] Backend: import handlera oraz modelu requestu.
- [x] Backend: bezpośredni test poprawnego payloadu video i odrzucenia złej liczby rekordów.
- [x] Frontend: `npm run build`.
- [x] Frontend: `npm run lint` — tylko wcześniejsze ostrzeżenie Fast Refresh w `src/components/ui/button.tsx`.
- [ ] Wywołanie z prawdziwym Ollama nie zostało wykonane, aby nie generować danych w lokalnie zmodyfikowanym `backend/app.db`.
