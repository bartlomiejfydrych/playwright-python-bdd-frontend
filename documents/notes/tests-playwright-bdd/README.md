# 🎭Playwright, testy i BDD – Notatki

# 📑Spis treści

- [START – rozpoczęcie pisania testów](#start--rozpoczęcie-pisania-testów)
    - [Struktura projektu – wstępna](#struktura-projektu--wstępna)
    - [pytest.ini – Czym jest](#pytestini--czym-jest)
    - [Base Page – src/pages/base_page.py](#base-page--srcpagesbase_pagepy)
    - [Home Page – src/pages/home_page.py](#home-page--srcpageshome_pagepy)
    - [Home Feature – tests/features/home.feature](#home-feature--testsfeatureshomefeature)
    - [Test Home – tests/steps/test_home.py](#test-home--testsstepstest_homepy)
    - [Uruchomienie testu](#uruchomienie-testu)
- [PROBLEM: Nietypowa ścieżka projektu](#problem-nietypowa-ścieżka-projektu)
- [PROBLEM: Brak logów kroków BDD w konsoli](#problem-brak-logów-kroków-bdd-w-konsoli)
- [PROBLEM: Brak SZCZEGÓŁOWYCH logów kroków BDD w konsoli](#problem-brak-szczegółowych-logów-kroków-bdd-w-konsoli)

---

# 📄START – rozpoczęcie pisania testów

## Struktura projektu – wstępna

```
├───src
│   │   __init__.py
│   │   
│   └───pages
│           __init__.py
│           
├───tests
│   │   __init__.py
│   │   
│   ├───features
│   │       __init__.py
│   │       
│   └───steps
│           __init__.py
```

- `src` – Kod aplikacji testowej
    - `pages` – Pliki, które zawierają lokatory i metody danej pod-strony
- `tests` – Testy i scenariusze testowe
    - `features` – Miejsce na "historyjki" zapisane w **BDD**
    - `steps` – Testy łączące i realizujące założenia "historyjek"

## pytest.ini – Czym jest

To plik konfiguracyjny dla frameworka `pytest` — jeden z kilku możliwych formatów (alternatywy to `pyproject.toml`
z sekcją `[tool.pytest.ini_options]` albo `setup.cfg`). Pytest szuka go automatycznie w katalogu głównym projektu
i na jego podstawie ustawia swoje zachowanie, zanim jeszcze zacznie zbierać testy.

**Dlaczego go dodajemy:**

1. `pythonpath = .` — dodaje katalog główny repo do ścieżki importów Pythona. Dzięki temu
   `from src.pages.home_page import HomePage` działa bez błędu `ModuleNotFoundError`, mimo że nie instalujesz projektu
   jako pakietu (`pip install -e .`) ani nie kombinujesz z `sys.path.append(...)` w każdym pliku.
2. `bdd_features_base_dir = tests/features` — to ustawienie pluginu `pytest-bdd`. Mówi mu, gdzie domyślnie szukać plików
   `.feature`, żebyś w każdym pliku step-defów nie musiał podawać pełnej ścieżki względnej.
3. `base_url = ...` — to ustawienie pluginu `pytest-base-url` (używanego też przez `pytest-playwright`).
   Pozwala w kodzie robić `page.goto("/login")` zamiast wpisywać pełny adres za każdym razem — Playwright doklei
   `base_url` automatycznie.

Zawartość:

```ini
[pytest]
bdd_features_base_dir = tests/features
pythonpath = .
base_url = https://automationteststore.com/
```

## Base Page – src/pages/base_page.py

Klasa bazowa, po której dziedziczą wszystkie konkretne strony. Trzyma wspólne, powtarzalne akcje (nawigacja, pobranie
tytułu), żeby nie duplikować tego w każdej stronie.

```python
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, path: str = "/"):
        self.page.goto(path)

    def title(self) -> str:
        return self.page.title()
```

## Home Page – src/pages/home_page.py

Konkretna strona, dziedzicząca po `BasePage`. Docelowo tu będą lądować lokatory elementów i metody typu
`click_login_button()`, `fill_search(text)` itd.

```python
from src.pages.base_page import BasePage


class HomePage(BasePage):
    def open(self):
        self.goto("/")
```

## Home Feature – tests/features/home.feature

Plik Gherkin opisujący scenariusz w języku naturalnym (biznesowym). To "kontrakt" — nie zawiera Pythona, tylko kroki,
które później podłączysz do kodu.

```gherkin
Feature: Home page

  Scenario: User opens the home page
    Given the user opens the home page
    Then the page title should be "A place to practice your automation skills!"
```

Jeśli tytuł strony jest długi, to warto:

- Włączyć **DevTools**
- W zakładce `Elements` wcisnąć `Ctrl + F`
- W wyszukiwarce wpisać `title`
- Skopiować

## Test Home – tests/steps/test_home.py

Tu łączysz plik `.feature` z rzeczywistym kodem — każdemu krokowi Gherkina (`Given`/`Then`) odpowiada funkcja Pythona
z dekoratorem `pytest-bdd`.

```python
import pytest
from pytest_bdd import scenarios, given, then, parsers

from src.pages.home_page import HomePage

scenarios("../features/home.feature")


@pytest.fixture
def home_page(page):
    return HomePage(page)


@given("the user opens the home page")
def open_home_page(home_page):
    home_page.open()


@then(parsers.parse('the page title should be "{expected_title}"'))
def check_title(home_page, expected_title):
    assert home_page.title() == expected_title
```

`page` to fixture, którą dostajesz gratis z `pytest-playwright` — otwiera przeglądarkę i stronę przed każdym testem,
zamyka po.

## Uruchomienie testu

```bash
playwright install
pytest --headed
```

`playwright install` ściąga binarki przeglądarek (jednorazowo). `--headed` pokazuje przeglądarkę na żywo, żebyś od razu
zobaczył, czy scenariusz faktycznie się wykonuje.

---

# 📄PROBLEM: Nietypowa ścieżka projektu

## Błąd:

`ERROR: path cannot contain [] parametrization: D:\[1]-Projekty\playwright-python-bdd-frontend`

Świetny trop — to konkretny, znany mechanizm w pytestcie, a nie przypadkowy błąd.

## Skąd się bierze ten błąd

Kiedy uruchamiasz `pytest` **bez podania żadnej ścieżki** (i bez ustawienia `testpaths` w konfiguracji), pytest
domyślnie bierze jako argument katalog, z którego został wywołany — czyli w Twoim przypadku pełną ścieżkę
`D:\[1]-Projekty\playwright-python-bdd-frontend`.

Problem w tym, że pytest ma wbudowaną składnię do wybierania konkretnych, sparametryzowanych testów z linii poleceń,
np.:

```
pytest test_file.py::test_foo[param1]
```

Wszystko po znaku `[` jest interpretowane jako "selection part" (wybór konkretnego wariantu parametryzacji). Skoro Twój
katalog nazywa się `[1]-Projekty`, pytest widzi tam nawias kwadratowy i próbuje go sparsować jako część takiej składni —
i się wykłada, bo to oczywiście nie jest prawidłowy zapis.

To nie jest błąd w Twoim kodzie ani konfiguracji — to kolizja nazwy katalogu ze składnią pytesta.

## Jak to naprawić

**Opcja A (szybka, bez ruszania struktury folderów na dysku)** — powiedz pytestowi wprost, gdzie szukać testów, żeby nie
musiał zgadywać z katalogu wywołania. Dodaj do `pytest.ini`:

```ini
[pytest]
bdd_features_base_dir = tests/features
pythonpath = .
base_url = https://example.com
testpaths = tests
```

`testpaths = tests` sprawia, że gdy odpalisz gołe `pytest` (bez argumentów), użyje relatywnej ścieżki `tests` zamiast
pełnej ścieżki katalogu roboczego — a `tests` nie zawiera nawiasów, więc problem znika. To samo osiągniesz, jawnie
wołając `pytest tests`.

**Opcja B (bardziej fundamentalna)** — usuń `[1]` z nazwy katalogu na dysku (np. `Projekty` zamiast `[1]-Projekty`).
Nawiasy kwadratowe w ścieżkach potrafią sprawiać problemy nie tylko pytestowi, ale też innym narzędziom (część CLI,
niektóre biblioteki glob/regex), więc to rozwiązanie jest "czystsze" na dłuższą metę, ale wymaga przeniesienia repo i
ewentualnej aktualizacji np. skróconych ścieżek w IDE.

Polecam zacząć od **Opcji A** — jest nieinwazyjna i powinna od razu rozwiązać problem. Jeśli używasz np. PyCharm/VS Code
z konfiguracją uruchamiania testów, która sama wstawia pełną ścieżkę jako argument, sprawdź też tam ustawienia — może
być konieczne dodanie `tests` jako working directory / argumentu, zamiast pozwalać IDE użyć ścieżki bezwzględnej.

---

# 📄PROBLEM: Brak logów kroków BDD w konsoli

Tak, to normalne w domyślnej konfiguracji — pytest z pluginem `pytest-bdd` **nie loguje** poszczególnych kroków Gherkina
do konsoli "z automatu". Widzisz tylko standardowy output pytesta (nazwa testu + PASSED/FAILED), a nie np.:

```
Given the user opens the home page ... OK
Then the page title should be "Example Domain" ... OK
```

## Jak zobaczyć kroki w konsoli

`pytest-bdd` ma wbudowany reporter, który to pokazuje — trzeba go tylko włączyć:

```bash
pytest --gherkin-terminal-reporter -v
```

Możesz też dodać to na stałe do `pytest.ini`, żeby nie pisać flagi za każdym razem:

```ini
[pytest]
bdd_features_base_dir = tests/features
pythonpath = .
base_url = https://example.com
testpaths = tests
addopts = --gherkin-terminal-reporter -v
```

`addopts` dokleja te flagi do każdego uruchomienia `pytest`, więc dostaniesz czytelny log krok po kroku bez pamiętania o
dodatkowych opcjach.

## Po co w takim razie te adnotacje BDD, skoro i tak nie widać ich domyślnie?

Adnotacje (`@given`, `@when`, `@then` + plik `.feature`) nie służą przede wszystkim do logowania w konsoli — to efekt
uboczny, który i tak łatwo włączyć. Ich prawdziwy sens to:

1. **Żywa dokumentacja** — plik `.feature` opisuje zachowanie aplikacji w języku naturalnym (Gherkin), zrozumiałym dla
   osób nietechnicznych (PO, QA manualny, biznes). Kod Pythona jest schowany pod spodem.

2. **Rozdzielenie "co" od "jak"** — scenariusz mówi *co* ma się zdarzyć (`Given user is logged in`,
   `When user clicks checkout`), a implementacja w kroku decyduje *jak* to zrobić (klikanie w konkretny selektor,
   wywołanie Page Objectu itd.). Możesz zmieniać implementację, nie ruszając scenariusza.

3. **Reużywalność kroków** — raz zdefiniowany krok (`@given("the user is logged in")`) możesz wykorzystać w wielu
   różnych scenariuszach/feature'ach, bez kopiowania kodu.

4. **Czytelne raporty** (np. z Allure czy właśnie `--gherkin-terminal-reporter`) — pokazują wynik testu w kontekście
   kroków biznesowych, a nie tylko "test_login_flow PASSED".

5. **Współpraca przy specyfikacji** — w podejściu BDD scenariusze pisze się (albo współtworzy) jeszcze przed kodem, jako
   ustalenie "czego oczekujemy od funkcji" — stąd nazwa Behaviour-Driven Development.

Jeśli w Twoim zespole nikt nietechniczny nie czyta plików `.feature`, a raporty w stylu Gherkina nie są potrzebne, to
szczerze — sam framework testowy (bez BDD, samo `pytest` + Page Object) też by wystarczył. BDD ma sens głównie wtedy,
gdy faktycznie chcesz tego mostu między "specyfikacją po angielsku" a kodem. Warto to sobie na starcie przemyśleć, żeby
nie dokładać warstwy, z której nikt nie skorzysta.

---

## 📄PROBLEM: Brak SZCZEGÓŁOWYCH logów kroków BDD w konsoli

Dobre spostrzeżenie — to zależy od poziomu "verbosity" (`-v`).

`--gherkin-terminal-reporter` ma trzy tryby:

- brak `-v` → standardowy output pytesta (kropki/nazwy testów)
- **`-v`** (pojedyncze) → tylko `Feature:` + `Scenario: ... PASSED` (dokładnie to, co widzisz)
- **`-vv`** (podwójne) → dodatkowo wypisuje każdy krok (`Given`/`When`/`Then`) osobno

Czyli żeby zobaczyć poszczególne kroki, potrzebujesz `-vv`, nie `-v`. Zaktualizuj `pytest.ini`:

```ini
[pytest]
bdd_features_base_dir = tests/features
pythonpath = .
base_url = https://example.com
testpaths = tests
addopts = --gherkin-terminal-reporter -vv
```

Po tej zmianie powinieneś zobaczyć coś w stylu:

```
Feature: Home page
    Scenario: User opens the home page
        Given the user opens the home page
        Then the page title should be "A place to practice your automation skills!"
    PASSED
```
