# Goal

Status: IMPLEMENTED (2026-09-11)

Rozbudować desktopowy lewy układ nawigacji tak, aby:

- skrajny lewy `AppSidebar` przełączał się między zwartym paskiem ikon a pełną szerokością z etykietami;
- środkowy `AppContextSidebar` pozostawał stale widoczny i aktywny oraz pozwalał użytkownikowi zmieniać szerokość przez przeciąganie jego prawej krawędzi;
- zachować obecny wygląd aplikacji i potraktować `templates/left-navbar-template.html` wyłącznie jako referencję zachowania;
- współdzielić mechanikę resize z prawym `SidePanel`, bez łączenia różnych modeli interakcji w jeden nadmiernie ogólny komponent.

# Context

Obecny desktopowy layout w `frontend/src/components/AppShell.tsx` renderuje kolejno:

1. `AppSidebar` — stałe `w-56`;
2. `AppContextSidebar` — stałe `w-56`;
3. zawartość strony;
4. niezależny, modalny `SidePanel` otwierany po prawej stronie.

Mock pokazuje dwa sąsiadujące lewe panele: skrajny pasek aplikacji może być zwarty/rozwinięty, a panel kontekstowy pozostaje otwarty. Prawy `SidePanel` ma już poprawnie działający resize przez pointer events, ale jest drawerem modalnym renderowanym w `Sheet`, więc nie powinien stać się bezpośrednią bazą dla stałego panelu layoutowego.

# Current State

- `AppSidebar.tsx` nie ma stanu zwinięcia, przycisku przełączającego ani wariantu ikonowego.
- `AppContextSidebar.tsx` jest zawsze renderowany na desktopie, ale ma sztywną szerokość `w-56` i nie ma uchwytu resize.
- Aktywny link w obu panelach jest już wyznaczany przez `NavLink`; należy zachować tę logikę także w stanie zwiniętym.
- Mobile używa pojedynczego `Sheet`, w którym oba panele renderują wariant `mobile`; desktopowych mechanizmów zwijania i resize nie należy przenosić do tego wariantu.
- `SidePanel.tsx` ma lokalną implementację resize od prawej strony: minimum 320 px, maksimum zależne od viewportu, reset szerokości po double click.
- Brak testów automatycznych; dostępne walidacje frontendu to `npm run lint` i `npm run build`.

# Proposed Approach

## 1. Stan layoutu w `AppShell`

`AppShell` będzie właścicielem desktopowego stanu obu lewych paneli:

- `primaryCollapsed: boolean` — domyślnie zwinięty do ok. 64 px, zgodnie z zachowaniem mocka;
- `contextWidth: number` — domyślnie zachowujący obecną szerokość ok. 224 px;
- oba ustawienia zapisane w `localStorage`, aby układ nie przeskakiwał do wartości domyślnych po odświeżeniu.

Stan i callbacki zostaną przekazane jawnie jako props. Nie ma potrzeby tworzenia nowego globalnego contextu, ponieważ korzystają z nich wyłącznie bezpośrednie dzieci `AppShell`.

## 2. Zwijany `AppSidebar`

Rozszerzyć API desktopowego wariantu o:

- `collapsed`;
- `onCollapsedChange` lub prosty `onToggle`.

Zachowanie:

- stan zwinięty: ikony wyśrodkowane, stała wąska szerokość, ukryte etykiety i nazwa aplikacji;
- stan rozwinięty: obecna szerokość i obecne etykiety;
- przełącznik dostępny w nagłówku/pobliżu krawędzi panelu;
- aktywny element zachowuje istniejące wyróżnienie `NavLink` w obu stanach;
- w stanie zwiniętym każdy link ma `aria-label` i natywny `title` albo istniejący komponent tooltipu, jeśli podczas implementacji okaże się już dostępny i stosowany;
- płynna animacja szerokości i widoczności tekstu bez zmiany stylistyki na mockową.

Wariant `mobile` pozostaje pełny i nie korzysta ze stanu `collapsed`.

## 3. Stale aktywny, resizowalny `AppContextSidebar`

Panel bliżej treści pozostanie zawsze wyrenderowany na desktopie, także gdy dla trasy nie ma sekcji kontekstowej. Nie będzie miał trybu zwiniętego ani zastępczego collapsed bara.

Zmienić jego desktopowe API o `width` i obsługę resize. Szerokość będzie nakładana przez `style={{ width }}` z zachowaniem `shrink-0`.

Na prawej krawędzi panelu dodać separator/uchwyt:

- przeciągnięcie w prawo poszerza panel, w lewo zwęża;
- zakres orientacyjny: 200–420 px, dodatkowo ograniczony dostępną szerokością viewportu;
- podwójne kliknięcie przywraca wartość domyślną;
- semantyka `role="separator"`, `aria-orientation="vertical"`, `aria-valuemin/max/now`;
- obsługa klawiatury: strzałki lewo/prawo zmieniają szerokość małym krokiem, Home/End ustawiają minimum/maksimum;
- podczas resize należy wyłączyć przypadkowe zaznaczanie tekstu i prawidłowo obsłużyć utratę pointer capture.

„Zawsze aktywny” oznacza stale obecny panel kontekstowy; aktywne pozycje nadal wynikają z bieżącego URL. Dla tras bez pasującej sekcji panel zachowuje swoją kolumnę, ale pokazuje tylko dostępne akcje (np. `Wstecz`) zamiast znikać.

## 4. Współdzielenie mechaniki z prawym panelem

Wyodrębnić mały hook, np. `frontend/src/lib/useResizablePanel.ts`, odpowiedzialny za:

- aktualną szerokość i clamp do min/max;
- rozpoczęcie, aktualizację i zakończenie drag;
- kierunek pomiaru (`left` — szerokość rośnie wraz z `clientX`, `right` — szerokość rośnie przy ruchu w lewo);
- reset i sterowanie klawiaturą;
- opcjonalną persystencję pod przekazanym kluczem.

Hook wykorzystają:

- `AppContextSidebar` / `AppShell` dla stałego panelu po lewej;
- istniejący `SidePanel` dla drawera po prawej.

Nie tworzyć jednego komponentu wizualnego `Sidebar`, ponieważ oba przypadki różnią się strukturą, modalnością, focusem, overlayem i cyklem otwierania. Wspólna jest mechanika szerokości, nie cały komponent.

## 5. Responsywność

- Desktopowe dwa panele działają od obecnego breakpointu `md`.
- Na mobile pozostaje obecny `Sheet` z obiema pełnymi sekcjami; nie pokazujemy tam resize ani zwartego paska ikon.
- Maksymalna szerokość panelu kontekstowego musi zostawić sensowną przestrzeń na `<main>`; ograniczenie powinno bazować na viewport i rzeczywistej szerokości pierwszego sidebara, a nie na stałej wartości zaszytej wyłącznie pod jeden ekran.
- Przy zmianie rozmiaru okna zapisana szerokość jest clampowana do aktualnie dopuszczalnego zakresu.

# Implementation Steps

1. Utworzyć `useResizablePanel` i przenieść do niego sprawdzoną obsługę pointer events z `SidePanel.tsx`, rozszerzając ją o oba kierunki, klawiaturę i opcjonalną persystencję.
2. Przepiąć prawy `SidePanel` na hook bez zmiany jego publicznego API i zachowania otwierania/zamykania.
3. Dodać stan zwinięcia głównej nawigacji w `AppShell`, wraz z bezpiecznym odczytem/zapisem `localStorage`.
4. Przerobić `AppSidebar` na desktopowy wariant compact/expanded, zachowując obecne linki, aktywność i dolną sekcję ustawień.
5. Podłączyć resizowalną szerokość do `AppContextSidebar`, dodać uchwyt na prawej krawędzi i utrzymać panel stale w desktopowym layoucie.
6. Sprawdzić wszystkie warianty zwrotne `AppContextSidebar` (`settings`, dopasowana sekcja, brak sekcji), aby każdy korzystał z tego samego wrappera i uchwytu — uniknąć trzech rozjeżdżających się implementacji `<aside>`.
7. Zweryfikować zachowanie dla tras głównych, ustawień, oferty, profilu oferty i głębokiego etapu pipeline'u.
8. Uruchomić lint i pełny build frontendu.

# Files / Components Involved

- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/AppSidebar.tsx`
- `frontend/src/components/AppContextSidebar.tsx`
- `frontend/src/components/SidePanel.tsx`
- `frontend/src/lib/useResizablePanel.ts` — nowy, jeśli proponowane wydzielenie potwierdzi się podczas implementacji
- opcjonalnie `frontend/src/index.css` — tylko jeśli globalne klasy są potrzebne do bezpiecznego `user-select` podczas resize; preferowane są klasy lokalne

# Risks

- Zbyt szeroki panel kontekstowy może ścisnąć główną treść na mniejszych desktopach; potrzebny dynamiczny limit.
- Animowanie szerokości podczas aktywnego drag może powodować opóźnienie; transition powinien działać dla toggle `AppSidebar`, ale nie dla przeciągania `AppContextSidebar`.
- Ukrycie tekstu wyłącznie CSS-em może pozostawić elementy w drzewie dostępności lub powodować skoki layoutu; renderowanie etykiet powinno zależeć od stanu.
- `localStorage` może zawierać stare/niepoprawne wartości; odczyt musi walidować typ i clampować szerokość.
- Refaktoryzacja resize prawego panelu nie może zmienić jego modalności, overlayu, zamykania po zmianie trasy ani wartości domyślnej 544 px.

# Validation

- [x] `npm run lint` w `frontend/` — zakończony powodzeniem; pozostało wcześniejsze ostrzeżenie `react(only-export-components)` w `src/components/ui/button.tsx`.
- [x] `npm run build` w `frontend/` — zakończony powodzeniem; Vite zgłasza wyłącznie ostrzeżenie o rozmiarze głównego chunka.
- Ręczna weryfikacja desktop:
  - toggle głównego sidebara w obie strony;
  - poprawne ikony, etykiety, tooltipy i aktywne linki;
  - resize panelu kontekstowego myszą w obie strony;
  - min/max, double click reset oraz klawiatura;
  - zachowanie ustawień po odświeżeniu;
  - kilka typów tras, w tym trasa bez danych kontekstowych;
  - brak regresji w prawym `SidePanel` (formularz/JSON, resize, zamknięcie, zmiana trasy).
- Ręczna weryfikacja mobile:
  - menu nadal otwiera się jako `Sheet`;
  - oba zestawy linków są pełne;
  - brak desktopowych uchwytów i kontrolek zwijania.

# Open Questions / Assumptions

- Przyjmuję, że „drugi panel zawsze aktywny” oznacza stale widoczny środkowy panel kontekstowy na desktopie, a nie wymuszone zaznaczenie dowolnego linku bez zgodności z URL.
- Przyjmuję domyślnie zwinięty skrajny sidebar (jak w mocku), ale zapamiętuję ostatni wybór użytkownika.
- Przyjmuję, że resize dotyczy wyłącznie prawej krawędzi środkowego panelu; użytkownik może przesuwać ją w lewo i prawo, co odpowiada zmianie szerokości panelu bez przesuwania jego lewej krawędzi.

# Implementation Result

- Dodano `frontend/src/lib/useResizablePanel.ts` jako współdzieloną mechanikę pointer/keyboard resize dla paneli zakotwiczonych z lewej lub prawej strony.
- `AppSidebar` ma desktopowe stany compact/expanded, dostępne etykiety i trwały wybór w `localStorage`.
- `AppContextSidebar` ma jeden wspólny wrapper dla wszystkich wariantów treści i stale obecny desktopowy uchwyt resize; szerokość jest zapamiętywana.
- `SidePanel` używa tego samego hooka bez zmiany swojego publicznego API, modalności ani zachowania przy zmianie trasy.
- Mobilny `Sheet` pozostał niezależny od desktopowego zwijania i resize.
