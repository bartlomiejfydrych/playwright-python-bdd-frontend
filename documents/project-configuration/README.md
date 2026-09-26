# 🛠️Konfiguracja projektu – notatki

# 📑Spis treści

1. [🔧Konfiguracja](#konfiguracja)
   - [Python – Instalacja](#python--instalacja)
   - [IDE PyCharm  – Instalacja](#ide-pycharm--instalacja)
   - [GitHub – Tworzenie i klonowanie repozytorium](#github--tworzenie-i-klonowanie-repozytorium)
   - [Dependencies – Instalacja](#dependencies--instalacja)
   - [Dalsze kroki — rozpoczęcie pisania testów](#dalsze-kroki--rozpoczęcie-pisania-testów)
2. [🧩Dodatkowe](#dodatkowe)
   - [Typo — Poprawienie błędów w tekście dla plików (głównie Markdown) pisanych w języku polskim](#typo--poprawienie-błędów-w-tekście-dla-plików-głównie-markdown-pisanych-w-języku-polskim)
   - [Markdown — wyłączenie podkreślania błędów we fragmentach kodu](#markdown--wyłączenie-podkreślania-błędów-we-fragmentach-kodu)
3. [🔌Pluginy do IDE](#pluginy-do-ide)
   - [Rainbow Brackets](#rainbow-brackets)
   - [Allure Report](#allure-report)
4. [📚Dependencies — Opis](#dependencies--opis)
   - [pytest-playwright](#pytest-playwright)
   - [pytest-bdd](#pytest-bdd)
   - [playwright install](#playwright-install)
   - [allure-pytest-bdd](#allure-pytest-bdd)

---

# 🔧Konfiguracja

## Python – Instalacja

1. Wchodzimy na stronę: https://www.python.org/
2. Klikamy `Downloads`
3. Klikamy `Download Python install manager`
4. Po uruchomieniu programu w konsoli na wszystko najlepiej wpisać `y`

## IDE PyCharm  – Instalacja

1. Wchodzimy na stronę: https://www.jetbrains.com/pycharm/
2. Klikamy `Download`
3. Klikamy `Download`
4. Instalujemy, klikając `Dalej`, `Dalej`…
5. Zaznaczamy dodatkowe opcje:
    - `Create Desktop Shortcut`
    - `Update PATH Variable (restart needed)`
    - Create Associations: `.py`

## GitHub – Tworzenie i klonowanie repozytorium

1. Wchodzimy na **GitHub** i dodajemy **nowe repozytorium**:
    - Nazwa
    - Opis
    - Szablon `.gitignore` → Język: Python
    - README.md
2. Kopiujemy **URL** naszego repozytorium
3. Wracamy do IDE i klikamy **klonowanie repozytorium**:
   - Obok `hamburger menu` klikamy na `nazwę projektu`, aby ją rozwinąć
   - W rozwiniętym menu klikamy `Clone Repository...`
4. Tworzymy **pusty katalog** z nazwą repozytorium i do niego **klonujemy**:
   - Po wklejeniu **URL** do `pierwszego pola` powinna się w `ścieżce` dopisać nazwa repo na podstawie której zostanie utworzony katalog
5. W pliku `.gitignore` odkomentować linię z `.idea`
6. Możemy zaczynać pracę od uzupełnienia naszego `README.md`

## Dependencies – Instalacja

### Rozwiązywanie problemów

#### Problem: `python -m venv venv` → „The system cannot find the file ...\WindowsApps\python.exe" (Windows, CMD)

**Przyczyna**
W PATH pierwszy był martwy alias `python.exe` (oraz `python3.exe`) w `%LOCALAPPDATA%\Microsoft\WindowsApps`. Prawdziwy Python 3.14.5 (Python install manager) leżał w `%LOCALAPPDATA%\Python\bin`, ale stał w PATH dalej, więc alias go przesłaniał. Prawdopodobnie alias został po aktualizacji managera (to przypuszczenie, nie potwierdzone).

**Diagnoza**
```
where python
py --version
python --version
py --list
dir %LOCALAPPDATA%\Microsoft\WindowsApps\python*
```
Objaw: `py` działał, `python` nie, a `where python` zwracał najpierw ścieżkę z `WindowsApps`.

**Obejście (działa od ręki)**
```
py -m venv venv
```

**Kroki, które nie rozwiązały problemu**
1. `py install --refresh` i `py install --configure` (bez błędów, ale alias nadal martwy).
2. Wyłączenie aliasów `python.exe` i `python3.exe` w Ustawienia → Aplikacje → Ustawienia zaawansowane aplikacji → Aliasy wykonywania aplikacji. Wyłączenie nie usuwa samych plików, więc `where` nadal je widział.

**Rozwiązanie**
```
del "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
del "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe"
```
Po otwarciu nowego CMD: `where python` zwraca tylko `...\AppData\Local\Python\bin\python.exe`, a `python --version` zwraca `Python 3.14.5`.

**Gdyby wróciło**
Uruchom `py install --refresh`, sprawdź `where python` i w razie potrzeby powtórz usunięcie plików. Do tego czasu `py -m venv venv` działa niezależnie od aliasów.

**Dalsze kroki w projekcie**
```
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install pytest-playwright pytest-bdd
playwright install
```
Dodaj `venv/` do `.gitignore`.

### Kroki

1. Zanim zainstalujemy cokolwiek, warto stworzyć **virtual environment** — izoluje zależności projektu od reszty systemu:
   - Otwieramy konsolę w katalogu z projektem
   - Używamy polecenia:
     ```bash
     python -m venv venv
     ```
   - Powinien po tym zostać utworzony w naszym projekcie katalog `venv`
   - Zgodnie z templatką `.gitignore` dla języka Python powinien on być **ignorowany**
2. Aktywujemy w PyCharm interpreter folderu `venv`:
   - `Hamburger menu` → `Settings...` → `Python` → `Interpreter`
   - Klikamy `Add Interpreter` → `Add Local Interpreter`
   - Zaznaczamy radiobutton `Select Existent`
   - I wybieramy ten, który używa w ścieżce `...\venv\Scripts\...`
3. Ustawiamy by w PyCharm uruchamiał się prawidłowy terminal, w prawidłowej lokalizacji projektu, z prawidłowymi ustawieniami
   i bez błędów:
   - `Hamburger menu` → `Settings...` → `Tools` → `Terminal`
   - `Project Settings` → `Start directory:` *<Tu powinna być ścieżka do naszego projektu>*
   - `Application Settings` → `Shell path:` → Wybieramy z listy: `C:\WINDOWS\system32\cmd.exe`  
     Dlaczego CMD, a nie PowerShell? Bo nie mogłem w nim ustawić ścieżki projektu oraz domyślnie blokuje wiele skryptów.  
     A CMD jest bardziej "otwarte" i po prostu działa.
   - Jeżeli po otwarciu terminalu w PyCharm widzimy coś takiego bez błędów, to znaczy, że jest okej:  
     ```bash
     Microsoft Windows [Version 10.0.26200.8457]
     (c) Microsoft Corporation. Wszelkie prawa zastrzeżone.
     
     (venv) D:\[1]-Projekty\requests-python-api>
     ```
4. Otwieramy prawidłowo już ustawiony **Terminal CMD** w naszym projekcie w PyCharm
5. Aktywujemy **venv** tym poleceniem w naszym Terminalu CMD:
   ```bash
   venv\Scripts\activate.bat
   ```
6. Aktualizujemy **pip**, czyli menadżer pakietów Pythona:  
   `python -m pip install --upgrade pip`  
   Poszczególne części:
   - **`python -m pip`** uruchamia `pip` jako moduł interpretera Pythona, który jest aktualnie aktywny.
     Dzięki temu masz pewność, że pakiety trafią do właściwego środowiska (u Ciebie do `venv`), a nie do innej instalacji Pythona.
     Samo `pip` też zwykle działa, ale przy kilku wersjach Pythona w systemie łatwo o pomyłkę.
   - **`install`** to komenda instalacji pakietów.
   - **`--upgrade`** oznacza, że jeśli pakiet jest już zainstalowany, ma zostać zaktualizowany do nowszej wersji.
   - **`pip`** to nazwa pakietu do zaktualizowania. Tutaj `pip` aktualizuje sam siebie.
   
   Świeżo utworzony `venv` zawiera zwykle wersję `pip` dołączoną do Pythona, która bywa już trochę stara. Nowsza wersja
   lepiej radzi sobie z rozwiązywaniem zależności i pobieraniem gotowych paczek binarnych (wheels).
7. Instalujemy następujące **dependencies**:
   - **pytest-playwright** – To oficjalny plugin. Sam ściąga `playwright` i `pytest` oraz `pytest-base-url`,
     więc nie instalujesz ich osobno. Dostajesz gotowe fixture'y (`page`, `context`, `browser`) i opcje CLI,
     np. `--headed`, `--browser firefox`, `--base-url`, `--tracing`, `--video`.
   - **pytest-bdd** – To obsługa plików `.feature` (Gherkin) w pytest. Kroki możesz pisać jako zwykłe funkcje i wstrzykiwać do nich fixture `page` z Playwrighta.
   - **playwright install** – Pobiera binaria przeglądarek (Chromium, Firefox, WebKit). To osobny krok, bo `pip` ich nie instaluje. Możesz też podać konkretną: `playwright install chromium`.
   - **allure-pytest-bdd** 🔴TODO: Zainstalować w połowie lub na koniec projektu i opisać
8. Po instalacji generujemy plik z zależnościami (To taki odpowiednik `pom.xml` z Javy):
   ```bash
   pip freeze > requirements.txt
   ```
   Dzięki temu ktoś inny (lub CI/CD) instaluje wszystko jedną komendą:
   ```bash
   pip install -r requirements.txt
   ```
9. Dodajemy do Git plik `requirements.txt` i pushujemy
10. Możemy **rozpocząć pisanie testów**

## Dalsze kroki — rozpoczęcie pisania testów

Dalsze kroki opisujące jak rozpocząć pisanie testów znajdują się w:  
📁requests-python-api (główny katalog projektu)  
&emsp;📁documents  
&emsp;&emsp;📁notes  
&emsp;&emsp;&emsp;📂tests-playwright-bdd

---

# 🧩Dodatkowe

## Typo — Poprawienie błędów w tekście dla plików (głównie Markdown) pisanych w języku polskim

1. Klikamy `Hamburger Menu` w lewym, górnym rogu
2. Klikamy `File`
3. Klikamy `Settings`
4. Rozwijamy `Editor`
5. Klikamy `Natural Languages`
6. Klikamy `+`
7. Szukamy na liście `Polski`
8. Klikamy `Apply`
9. Klikamy `OK`

## Markdown — wyłączenie podkreślania błędów we fragmentach kodu

1. Dodajemy blok kodu z błędem np. `print("czesć World")`
2. Najeżdżamy kursorem na podkreślone słowo `czesć`
3. Po najechaniu powinno pojawić się okno z propozycją poprawy
4. Klikamy `More actions...`
5. Klikamy `Hide problems in code fences`  
   Po najechaniu na tę opcję widzimy podpowiedź, że dotyczy to tylko **Markdown**
6. Gdybyśmy chcieli to cofnąć to komunikat podpowie nam takie coś:  
   `Problem highlighting for fenced code blocks in Markdown is disabled. You can enable it in the settings under Languages and Frameworks | Markdown.`
7. Może być tak, że Git będzie chciał dodać i pushnąć plik `markdown.xml`. Dodajemy i pushujemy

---

# 🔌Pluginy do IDE

## Rainbow Brackets

### 🌈 Rainbow Brackets – Wtyczka do podświetlania nawiasów w IDE JetBrains

**Rainbow Brackets** to wtyczka do **IntelliJ IDEA**, **PyCharm**, **WebStorm**, **Android Studio** i innych IDE
z rodziny **JetBrains**, która podświetla nawiasy w różnych kolorach, ułatwiając analizę kodu.

### 📌 Kluczowe funkcje wtyczki Rainbow Brackets
✅ **Kolorowe podświetlanie nawiasów** – różne poziomy zagnieżdżenia otrzymują różne kolory.  
✅ **Obsługa wielu języków programowania** – działa m.in. w **Java, Python, JavaScript, Kotlin, HTML, XML, JSON** i wielu innych.  
✅ **Łatwa identyfikacja błędów** – pomaga znaleźć brakujące lub źle zamknięte nawiasy.  
✅ **Dostosowywanie kolorów** – użytkownik może zmieniać schemat kolorów według własnych preferencji.  
✅ **Wsparcie dla ciemnych i jasnych motywów**.  
✅ **Współpraca z innymi wtyczkami** – działa z **Material Theme UI, Atom Material Icons**, itp.

### 📦 Instalacja
1️⃣ **Otwórz:** `File → Settings → Plugins` (lub `Ctrl + Alt + S`).  
2️⃣ **Wyszukaj:** "Rainbow Brackets" w zakładce **Marketplace**.  
3️⃣ **Kliknij:** **Install**, a następnie **Restart IDE**.

### 🎨 Przykład działania i dostosowanie kolorów

Przed instalacją:
```java
public void exampleMethod() {
    if (condition) {
        while (true) {
            doSomething();
        }
    }
}
```

Po instalacji **Rainbow Brackets**:
- `{ }`, `[ ]`, `( )` będą miały różne kolory, zależnie od poziomu zagnieżdżenia.

Możesz edytować kolory w **File → Settings → Editor → Color Scheme → Rainbow Brackets**.

### 🎯 Dlaczego warto używać Rainbow Brackets?
🔹 Zwiększa **czytelność kodu** w dużych projektach.  
🔹 Pomaga znaleźć **brakujące lub nadmiarowe nawiasy**.  
🔹 Przyspiesza **debugowanie** i **analizę kodu**.  
🔹 Jest **prosta w użyciu** i nie wpływa na wydajność IDE.

## Allure Report

### 📊 Allure Report – Wtyczka

**Allure Report** to **zaawansowane narzędzie do generowania raportów testowych**. Wtyczka **Allure Plugin** dla
IDE JetBrains integruje Allure z IDE, umożliwiając szybkie generowanie, przeglądanie i analizowanie raportów
bez wychodzenia z IDE.

### 📌 Co robi wtyczka Allure Report?
✅ **Integruje raporty Allure z IDE** – pozwala otwierać i analizować wyniki testów bez wychodzenia z IDE.  
✅ **Dodaje nową zakładkę "Allure"**, w której można wizualizować raporty w graficznej formie.  
✅ **Automatycznie wykrywa katalog `allure-results`** i generuje raport jednym kliknięciem.  
✅ **Obsługuje TestNG, JUnit 4/5, Cucumber i inne frameworki** testowe.  
✅ **Pozwala przeglądać szczegóły testów** – błędy, logi, załączniki (np. screenshoty).

### 🔧 Jak zainstalować wtyczkę?
1️⃣ Otwórz **IDE** i przejdź do:
- `File → Settings → Plugins` (Windows/Linux)
- `IDE → Preferences → Plugins` (Mac)  
  2️⃣ Wyszukaj: **"Allure Report"** w zakładce **Marketplace**.  
  3️⃣ Kliknij **Install**, a potem **Restart IDE**.

### 📂 Jak używać wtyczki?
1️⃣ **Uruchom testy**, które zapisują wyniki do `allure-results`.  
2️⃣ W **dolnym panelu IDE** przejdź do zakładki **"Allure"**.  
3️⃣ Kliknij **"Generate Report"**, aby zobaczyć wyniki w IDE.  
4️⃣ Możesz nawigować po testach, sprawdzać błędy i załączniki.

### **📢 Zalety wtyczki Allure Report**
🚀 **Nie trzeba otwierać raportów w przeglądarce** – wszystko działa w IDE.  
🔍 **Szybki podgląd wyników testów** bez dodatkowych poleceń w terminalu.  
📊 **Wizualizacja błędów, logów i statystyk** testów.  
🛠️ **Łatwa integracja z popularnymi frameworkami** testowymi.

Jeśli pracujesz z Allure, ta wtyczka **znacznie ułatwia życie**! 🔥

## 🥒Gherkin

**Gherkin** jako plugin IDE służy do zapewnienia **wsparcia dla języka Gherkin**, używanego m.in. przez `pytest-bdd`.

Sam **Gherkin nie jest frameworkiem testowym**. Jest językiem służącym do opisywania scenariuszy zachowania aplikacji
w czytelnej, strukturalnej formie.

Przykład:

```gherkin
Feature: Login

  Scenario: Successful login
    Given the user is on the login page
    When the user enters valid credentials
    Then the dashboard should be displayed
```

Plugin pozwala IDE rozpoznawać taką składnię i odpowiednio ją obsługiwać.

### 1. Co daje plugin Gherkin?

W zależności od IDE/pluginu może zapewniać m.in.:

* rozpoznawanie plików `.feature`,
* kolorowanie składni Gherkin,
* podpowiedzi dla `Feature`, `Scenario`, `Given`, `When`, `Then` itd.,
* nawigację pomiędzy scenariuszem a implementacją kroku,
* sprawdzanie składni,
* wsparcie dla języka Gherkin podczas edycji.

Czyli zamiast traktować:

```text
login.feature
```

jak zwykły plik tekstowy, IDE rozumie, że jest to **plik zawierający scenariusze BDD**.

### 2. Gherkin a `pytest-bdd`

To bardzo ważne rozróżnienie:

```text
Gherkin
   ↓
język do opisywania zachowania

pytest-bdd
   ↓
framework/plugin umożliwiający wykonywanie
scenariuszy Gherkin jako testów pytest
```

Czyli Gherkin sam w sobie **nie wykonuje testów**.

Na przykład:

```gherkin
Given the user is on the login page
When the user enters valid credentials
Then the dashboard should be displayed
```

to tylko **opis scenariusza**.

Dopiero `pytest-bdd` łączy te kroki z Pythonem:

```python
@given("the user is on the login page")
def open_login_page(page):
    ...
```

### 3. Jak wygląda cały zestaw?

W Twoim przypadku można to przedstawić tak:

```text
Gherkin plugin
      ↓
obsługa plików .feature w IDE
      ↓
Gherkin
      ↓
opis scenariusza BDD
      ↓
pytest-bdd
      ↓
wykonanie scenariusza
      ↓
pytest
```

A jeżeli dodamy wcześniejsze elementy:

```text
Gherkin plugin
      ↓
.feature
      ↓
Gherkin
      ↓
pytest-bdd
      ↓
pytest
      ↓
pytest-playwright
      ↓
Playwright
      ↓
Browser
      ↓
allure-pytest-bdd
      ↓
Allure Report
```

### 4. Czy plugin Gherkin jest potrzebny do działania `pytest-bdd`?

**Nie.**

To istotne.

`pytest-bdd` może działać bez zainstalowanego pluginu Gherkin w IDE.

Plugin Gherkin jest przede wszystkim **narzędziem wspomagającym pracę programisty/testera w IDE**.

Czyli:

```text
pytest-bdd → potrzebny do wykonywania testów BDD
Gherkin plugin → ułatwia tworzenie i edycję plików .feature
```

Możesz więc mieć:

```text
pytest-bdd
pytest-playwright
allure-pytest-bdd
```

i testy będą działały nawet bez pluginu Gherkin.

### 5. Gherkin nie oznacza tylko `Given/When/Then`

Gherkin ma również inne elementy, np.:

```gherkin
Feature:
Background:
Scenario:
Scenario Outline:
Examples:
Given
When
Then
And
But
```

Przykładowo:

```gherkin
Feature: Board management

  Scenario: Create a new board
    Given the user is logged in
    When the user creates a board named "Test Board"
    Then the board should be created successfully
```

Plugin Gherkin pozwala IDE odpowiednio rozpoznawać te konstrukcje.

### Krótka definicja do notatek

> **Gherkin (plugin)** – plugin IDE zapewniający wsparcie dla języka Gherkin, używanego do tworzenia scenariuszy BDD
> w plikach `.feature`. Oferuje m.in. kolorowanie składni, walidację, podpowiedzi i nawigację po krokach
> `Given/When/Then`. Nie wykonuje testów – za wykonywanie scenariuszy Gherkin w Pythonie może odpowiadać np. `pytest-bdd`.

---

# 📚Dependencies — Opis

## 📕pytest-playwright

**pytest-playwright** to oficjalna wtyczka integrująca bibliotekę Playwright z pytest. Udostępnia gotowe fixtures,
dzięki którym można wygodnie tworzyć i uruchamiać **automatyczne testy aplikacji webowych** w przeglądarkach.

Najprościej:

> **Playwright** odpowiada za automatyzację przeglądarki, a **pytest** za organizację i wykonywanie testów.

### Czym jest pytest-playwright?

Bez wtyczki można używać Playwright bezpośrednio:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()

    page = browser.new_page()
    page.goto("https://example.com")

    assert page.title() == "Example Domain"

    browser.close()
```

`pytest-playwright` upraszcza ten kod, ponieważ udostępnia gotowe fixtures, np. `page`:

```python
def test_homepage(page):
    page.goto("https://example.com")

    assert page.title() == "Example Domain"
```

Nie musisz samodzielnie:

* uruchamiać Playwright,
* tworzyć przeglądarki,
* tworzyć strony,
* zamykać przeglądarki.

W dużej mierze zajmuje się tym fixture dostarczony przez plugin.

### Instalacja

Instalacja:

```bash
pip install pytest-playwright
```

Następnie instalacja przeglądarek Playwright:

```bash
playwright install
```

Można też zainstalować konkretną przeglądarkę:

```bash
playwright install chromium
```

### Podstawowy test

```python
def test_login(page):

    page.goto("https://example.com/login")

    page.get_by_label("Username").fill("test_user")
    page.get_by_label("Password").fill("password")

    page.get_by_role("button", name="Login").click()

    assert page.get_by_text("Welcome").is_visible()
```

Tutaj:

* `page.goto()` – otwiera stronę,
* `get_by_label()` – znajduje pole formularza po etykiecie,
* `fill()` – wpisuje tekst,
* `get_by_role()` – znajduje element po roli dostępnościowej,
* `click()` – klika element,
* `is_visible()` – sprawdza widoczność.

### Najważniejsze fixtures

`pytest-playwright` dostarcza kilka istotnych fixtures.

#### `page`

Najczęściej używany.

Reprezentuje pojedynczą kartę/stronę w przeglądarce.

```python
def test_example(page):
    page.goto("https://example.com")
```

#### `browser`

Reprezentuje instancję przeglądarki.

```python
def test_example(browser):
    page = browser.new_page()

    page.goto("https://example.com")
```

#### `context`

Reprezentuje **Browser Context**, czyli izolowane środowisko przeglądarki.

```python
def test_example(context):
    page = context.new_page()

    page.goto("https://example.com")
```

Browser Context może mieć własne:

* cookies,
* local storage,
* session storage,
* ustawienia.

Jest to szczególnie przydatne przy izolowaniu testów.

#### `browser_type`

Pozwala pracować z typem przeglądarki:

```python
def test_example(browser_type):
    browser = browser_type.launch()
```

### Obsługiwane przeglądarki

Playwright obsługuje m.in.:

* Chromium,
* Firefox,
* WebKit.

Można więc uruchamiać ten sam test na różnych silnikach przeglądarek.

Przykładowo:

```bash
pytest --browser chromium
```

```bash
pytest --browser firefox
```

```bash
pytest --browser webkit
```

Można również uruchomić test na kilku przeglądarkach:

```bash
pytest --browser chromium --browser firefox
```

### Headless i headed

Domyślnie testy są uruchamiane **headless**, czyli bez widocznego okna przeglądarki.

```bash
pytest
```

Można uruchomić przeglądarkę z widocznym interfejsem:

```bash
pytest --headed
```

Jest to bardzo przydatne podczas debugowania.

---

### Tryb debugowania

Playwright pozwala również uruchomić test z narzędziami debugowania:

```bash
PWDEBUG=1 pytest
```

Na Windows PowerShell:

```powershell
$env:PWDEBUG=1
pytest
```

Można wtedy łatwiej obserwować wykonywanie testu.

### Automatyczne oczekiwanie

Jedną z ważnych cech Playwright jest **auto-waiting**.

Przykład:

```python
page.get_by_role(
    "button",
    name="Submit"
).click()
```

Playwright przed wykonaniem akcji automatycznie czeka, aż element będzie odpowiedni do interakcji.

Dzięki temu zwykle nie trzeba pisać:

```python
time.sleep(3)
```

i jest to jedna z istotnych różnic względem prostego podejścia opartego na ręcznym `sleep`.

### Locatory

Playwright udostępnia różne sposoby wyszukiwania elementów.

#### Role

```python
page.get_by_role(
    "button",
    name="Login"
)
```

#### Label

```python
page.get_by_label("Email")
```

#### Placeholder

```python
page.get_by_placeholder("Enter email")
```

#### Text

```python
page.get_by_text("Welcome")
```

#### Test ID

```python
page.get_by_test_id("login-button")
```

Można również używać CSS:

```python
page.locator("#login-button")
```

### Assertions

Playwright posiada również własny mechanizm asercji:

```python
from playwright.sync_api import expect

def test_title(page):

    page.goto("https://example.com")

    expect(page).to_have_title(
        "Example Domain"
    )
```

Można sprawdzać m.in.:

```python
expect(page.locator("h1")).to_be_visible()
```

```python
expect(page.locator("input")).to_have_value("Jan")
```

```python
expect(page.locator(".message")).to_contain_text("Success")
```

Asercje Playwright również posiadają mechanizm automatycznego oczekiwania.

### Screenshoty

Można wykonywać screenshoty:

```python
page.screenshot(
    path="screenshot.png"
)
```

Całej strony:

```python
page.screenshot(
    path="page.png",
    full_page=True
)
```

Jest to szczególnie przydatne przy debugowaniu nieudanych testów.

### Nagrywanie trace

Playwright posiada bardzo przydatną funkcję **Trace Viewer**.

Można rejestrować przebieg testu, a później analizować:

* wykonane akcje,
* screenshoty,
* DOM,
* requesty,
* response,
* czas wykonania poszczególnych operacji.

Jest to bardzo przydatne przy analizowaniu testów, które zawodzą tylko sporadycznie.

### Testy API

Playwright nie ogranicza się wyłącznie do UI. Udostępnia również klienta API.

Przykładowo:

```python
def test_api(api_request_context):

    response = api_request_context.get(
        "https://example.com/api/users"
    )

    assert response.ok
```

Dzięki temu można wykonywać zarówno testy UI, jak i API w ramach jednego ekosystemu Playwright.

### Integracja z pytest

To właśnie główna funkcja `pytest-playwright`.

Typowy test:

```python
def test_create_user(page):

    page.goto("/users")

    page.get_by_role(
        "button",
        name="Add user"
    ).click()

    page.get_by_label("Name").fill("Jan")

    page.get_by_role(
        "button",
        name="Save"
    ).click()

    expect(
        page.get_by_text("User created")
    ).to_be_visible()
```

`pytest` odpowiada za:

* wykrywanie testów,
* fixtures,
* parametryzację,
* markery,
* uruchamianie testów,
* raportowanie wyniku.

`pytest-playwright` dostarcza integrację z przeglądarką.

`Playwright` wykonuje operacje na stronie.

### Konfiguracja

Wtyczka udostępnia wiele opcji przez CLI.

Przykładowo:

```bash
pytest --browser chromium
```

```bash
pytest --headed
```

```bash
pytest --slowmo 500
```

`--slowmo` spowalnia wykonywanie operacji, co może być przydatne podczas debugowania.

Można też ustawić opcje globalnie za pomocą konfiguracji pytest, np. w `pytest.ini`.

### Typowe zastosowania w QA

`pytest-playwright` jest używany przede wszystkim do:

#### Testów UI

```text
otwarcie strony
      ↓
logowanie
      ↓
przejście do panelu
      ↓
utworzenie rekordu
      ↓
weryfikacja rezultatu
```

#### Testów E2E

Sprawdzanie całych procesów biznesowych z perspektywy użytkownika.

#### Testów regresyjnych

Automatyczne sprawdzanie, czy istniejące funkcjonalności nadal działają.

#### Cross-browser testing

Uruchamianie testów na Chromium, Firefox i WebKit.

#### Testów hybrydowych

Przygotowanie danych przez API → wykonanie operacji w UI → weryfikacja danych przez API.

To ostatnie podejście jest szczególnie interesujące w rozbudowanych frameworkach QA.

### pytest-playwright vs Selenium

W kontekście automatyzacji UI można spotkać oba rozwiązania:

|                            | pytest-playwright | Selenium                       |
|----------------------------|-------------------|--------------------------------|
| Język                      | Python + inne     | wiele języków                  |
| Automatyzacja przeglądarki | Playwright        | WebDriver                      |
| Auto-waiting               | ✅                | bardziej ręczne podejście      |
| Chromium                   | ✅                | ✅                             |
| Firefox                    | ✅                | ✅                             |
| WebKit                     | ✅                | pośrednio / inne podejścia     |
| API testing                | ✅                | nie jest głównym zastosowaniem |
| Integracja z pytest        | bardzo dobra      | przez odpowiednie biblioteki   |

Nie oznacza to, że jedno rozwiązanie automatycznie zastępuje drugie — oba są szeroko stosowane w automatyzacji testów.

### Zalety

* prosta integracja z pytest,
* gotowe fixtures,
* obsługa Chromium, Firefox i WebKit,
* automatyczne oczekiwanie na elementy,
* nowoczesne locatory,
* screenshoty i trace,
* możliwość testowania UI i API,
* dobre możliwości uruchamiania testów w CI/CD.

### Ograniczenia

* wymaga dodatkowych przeglądarek Playwright,
* testy UI są bardziej złożone i wolniejsze niż testy samego API,
* wymaga utrzymywania locatorów przy zmianach UI,
* podobnie jak inne frameworki UI, może wymagać dodatkowej pracy przy stabilizacji dużych zestawów testów.

### Krótka definicja do notatek

**pytest-playwright** – oficjalna wtyczka integrująca Playwright z pytest, udostępniająca gotowe fixtures
do automatyzacji przeglądarek i tworzenia testów UI/E2E. Umożliwia m.in. testowanie aplikacji na Chromium,
Firefox i WebKit, automatyczne oczekiwanie na elementy, wykonywanie screenshotów i trace'ów oraz integrację testów
UI z ekosystemem pytest.

---

## 📕pytest-bdd

pytest-bdd to rozszerzenie `pytest`, które pozwala tworzyć testy w podejściu **BDD (Behavior-Driven Development)**,
wykorzystując język **Gherkin**.

Najważniejsza idea: zamiast opisywać test wyłącznie kodem Pythona, definiujesz **zachowanie aplikacji w formie scenariusza biznesowego**, np.:

> Given użytkownik jest na stronie logowania
> When wpisze poprawne dane
> Then powinien zostać zalogowany

### 1. Instalacja

```bash
pip install pytest-bdd
```

Po instalacji `pytest-bdd` działa razem z `pytest`.

### 2. Gherkin – scenariusz `.feature`

Test BDD zwykle zaczyna się od pliku `.feature`.

Przykład:

```gherkin
Feature: Login

  Scenario: Successful login
    Given the user is on the login page
    When the user enters valid credentials
    And clicks the login button
    Then the user should be logged in
```

Tutaj mamy klasyczną strukturę:

* **Feature** – funkcjonalność, którą testujemy
* **Scenario** – konkretny przypadek testowy
* **Given** – stan początkowy / przygotowanie
* **When** – wykonywana akcja
* **Then** – oczekiwany rezultat
* **And** – kontynuacja poprzedniego kroku

To właśnie język **Gherkin**.

### 3. Połączenie z Pythonem

Sam `.feature` opisuje **co** ma się wydarzyć, ale nie mówi jeszcze **jak** to zrobić.

W Pythonie definiujemy implementację poszczególnych kroków.

Przykładowo:

```python
from pytest_bdd import given, when, then


@given("the user is on the login page")
def open_login_page(page):
    page.goto("https://example.com/login")


@when("the user enters valid credentials")
def enter_credentials(page):
    page.get_by_label("Username").fill("user")
    page.get_by_label("Password").fill("password")


@when("clicks the login button")
def click_login(page):
    page.get_by_role("button", name="Login").click()


@then("the user should be logged in")
def verify_login(page):
    assert page.get_by_text("Welcome").is_visible()
```

Czyli:

**Gherkin:**

```text
Given the user is on the login page
```

jest połączony z:

```python
@given("the user is on the login page")
```

a kod wewnątrz funkcji wykonuje rzeczywistą akcję.

### 4. `pytest-bdd` + `pytest`

To ważne: `pytest-bdd` **nie jest alternatywą dla pytest**.

Jest rozszerzeniem pytest.

Można to przedstawić tak:

```text
pytest
  │
  └── pytest-bdd
        │
        ├── Gherkin / .feature
        ├── Given
        ├── When
        └── Then
```

Dzięki temu nadal korzystasz z mechanizmów pytest, takich jak:

* fixtures,
* parametrization,
* assertions,
* markers,
* plugins,
* CLI,
* raportowanie.

### 5. `pytest-bdd` + Playwright

W Twoim przypadku jest to szczególnie ciekawe, ponieważ używasz `pytest-playwright`.

Możesz połączyć:

```text
pytest-bdd
     ↓
pytest
     ↓
pytest-playwright
     ↓
Playwright
     ↓
Browser
```

Na przykład:

#### `login.feature`

```gherkin
Feature: Login

  Scenario: Successful login
    Given the user is on the login page
    When the user logs in with valid credentials
    Then the dashboard should be displayed
```

#### Python

```python
from pytest_bdd import given, when, then


@given("the user is on the login page")
def open_login_page(page):
    page.goto("https://example.com/login")


@when("the user logs in with valid credentials")
def login(page):
    page.get_by_label("Username").fill("user")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()


@then("the dashboard should be displayed")
def verify_dashboard(page):
    assert page.get_by_role("heading", name="Dashboard").is_visible()
```

Tutaj:

* `pytest-bdd` odpowiada za BDD/Gherkin,
* `pytest-playwright` dostarcza fixture `page`,
* Playwright steruje przeglądarką,
* pytest uruchamia cały test.

### 6. Fixtures

`pytest-bdd` bardzo dobrze współpracuje z fixtures z pytest.

Na przykład:

```python
@pytest.fixture
def user():
    return {
        "username": "test_user",
        "password": "secret"
    }
```

Możesz później wykorzystać ją w step definition:

```python
@given("the user has valid credentials")
def valid_credentials(user):
    assert user["username"]
    assert user["password"]
```

W praktyce oznacza to, że możesz wykorzystać całą architekturę fixture, którą znasz z normalnego pytest.

### 7. Parametryzacja scenariuszy

BDD pozwala również tworzyć scenariusze z różnymi danymi.

Przykład:

```gherkin
Scenario Outline: Login with different credentials
    Given the user is on the login page
    When the user enters "<username>" and "<password>"
    Then the login result should be "<result>"

Examples:
    | username | password | result  |
    | user1    | pass1    | success |
    | user2    | wrong    | failure |
```

Dzięki temu jeden scenariusz może zostać wykonany wielokrotnie z różnymi danymi.

To jest odpowiednik podejścia parametryzowanego, które znasz z `pytest.mark.parametrize`.

### 8. Po co właściwie używać `pytest-bdd`?

Główną zaletą jest **czytelność testów dla osób nietechnicznych**.

Normalny test:

```python
def test_successful_login(page):
    page.goto("/login")
    page.get_by_label("Username").fill("user")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()

    assert page.get_by_text("Dashboard").is_visible()
```

Test BDD:

```gherkin
Scenario: Successful login
    Given the user is on the login page
    When the user logs in with valid credentials
    Then the dashboard should be displayed
```

Drugi zapis jest znacznie bardziej **biznesowy**.

Dlatego BDD może być przydatne, gdy w projekcie współpracują ze sobą np.:

* QA,
* developerzy,
* Product Owner,
* analitycy biznesowi,
* osoby biznesowe.

Scenariusz `.feature` może być zrozumiały nawet dla osoby, która nie zna Pythona.

### 9. Czy każdy projekt powinien używać `pytest-bdd`?

Nie.

BDD ma sens przede wszystkim wtedy, gdy **czytelne scenariusze biznesowe są rzeczywiście potrzebne**.

Jeżeli jesteś jedyną osobą piszącą testy automatyczne i testy mają przede wszystkim techniczny charakter, klasyczny pytest może być prostszy:

```python
def test_create_board():
    ...
```

Zamiast:

```text
Scenario: Create a new board
    Given ...
    When ...
    Then ...
```

`pytest-bdd` dodaje dodatkową warstwę abstrakcji, więc w prostych projektach może być niepotrzebne.

### 10. `pytest-bdd` a Cucumber

Jeżeli spotkasz **Cucumber**, warto wiedzieć, że idea jest bardzo podobna.

Oba wykorzystują:

**Gherkin → Given / When / Then → step definitions**

Różnica jest przede wszystkim w ekosystemie.

W Pythonie możesz używać:

```text
pytest + pytest-bdd
```

podczas gdy w innych językach popularne są rozwiązania oparte o Cucumber.

### 11. Jak wygląda cały przepływ?

W typowym projekcie:

```text
login.feature
      │
      │ Gherkin
      ↓
pytest-bdd
      │
      │ mapowanie kroków
      ↓
Python step definitions
      │
      ├── pytest fixtures
      │
      ├── Playwright
      ├── Requests
      └── inne biblioteki
      │
      ↓
   pytest
      │
      ↓
  test result
      │
      ↓
Allure
```

Czyli `pytest-bdd` jest przede wszystkim **warstwą BDD nad pytest**, a nie biblioteką do samego wykonywania testów.

### Krótka definicja do notatek

> **pytest-bdd** – rozszerzenie `pytest` umożliwiające tworzenie testów w podejściu BDD z wykorzystaniem języka Gherkin
> (`Feature`, `Scenario`, `Given`, `When`, `Then`). Łączy biznesowo opisane scenariusze `.feature` z implementacją
> kroków w Pythonie i współpracuje z fixtures oraz innymi pluginami pytest, np. `pytest-playwright`.

---

## 📕playwright install

Playwright `playwright install` **nie jest biblioteką ani pluginem Pythona**. Jest to **polecenie CLI Playwright**,
które służy do pobrania i zainstalowania przeglądarek, którymi Playwright będzie sterował podczas testów.

To ważne rozróżnienie, ponieważ w Twoim projekcie masz np.:

```bash
pip install pytest-playwright
```

ale to **nie instaluje jeszcze przeglądarek**.

Dlatego wykonuje się:

```bash
playwright install
```

### 1. Co robi `playwright install`?

Polecenie pobiera przeglądarki wymagane przez Playwright:

* **Chromium**
* **Firefox**
* **WebKit**

Czyli:

```text
pytest-playwright
        ↓
instaluje integrację pytest ↔ Playwright

playwright install
        ↓
instaluje przeglądarki
        ↓
Chromium / Firefox / WebKit
```

Bez zainstalowanych browser binaries test Playwright może zakończyć się błędem informującym, że dana przeglądarka nie została zainstalowana.

### 2. Instalacja wszystkich przeglądarek

Najprościej:

```bash
playwright install
```

Instaluje to wszystkie przeglądarki obsługiwane przez Playwright.

### 3. Instalacja konkretnej przeglądarki

Możesz również zainstalować tylko wybraną:

```bash
playwright install chromium
```

albo:

```bash
playwright install firefox
```

lub:

```bash
playwright install webkit
```

Przykładowo, jeżeli Twoje testy wykorzystują wyłącznie Chromium:

```bash
pip install pytest-playwright
playwright install chromium
```

nie musisz pobierać pozostałych przeglądarek.

### 4. Dlaczego Playwright sam nie korzysta z przeglądarki zainstalowanej w Windows?

To jedna z ważniejszych rzeczy.

Playwright korzysta z **własnych, kompatybilnych wersji przeglądarek**, które pobiera za pomocą `playwright install`.

Czyli nie chodzi po prostu o:

```text
Google Chrome zainstalowany w Windows
```

ale o wersję Chromium zarządzaną przez Playwright.

Dzięki temu Playwright ma większą kontrolę nad zgodnością wersji frameworka i przeglądarki.

### 5. Jak to wygląda w Twoim projekcie?

Jeżeli masz:

```bash
pip install pytest-playwright
```

to typowa konfiguracja wygląda:

```bash
pip install pytest
pip install pytest-playwright
playwright install
```

A potem możesz napisać:

```python
def test_homepage(page):
    page.goto("https://example.com")

    assert page.title() == "Example Domain"
```

`page` pochodzi z `pytest-playwright`, a sam browser jest dostarczany przez instalację Playwright.

### 6. `playwright install` vs `pip install playwright`

To również warto rozróżnić:

| Polecenie                       | Co robi                                     |
| ------------------------------- | ------------------------------------------- |
| `pip install playwright`        | instaluje bibliotekę Playwright dla Pythona |
| `pip install pytest-playwright` | instaluje integrację Playwright z pytest    |
| `playwright install`            | pobiera przeglądarki Playwright             |
| `playwright install chromium`   | pobiera tylko Chromium                      |

W Twoim przypadku najczęściej wystarczy:

```bash
pip install pytest-playwright
playwright install
```

ponieważ `pytest-playwright` ma Playwright jako zależność.

### 7. Czy `playwright install` powinien być w `requirements.txt`?

Nie.

To **polecenie CLI**, a nie dependency do wpisania jako:

```text
playwright install
```

w `requirements.txt`.

W `requirements.txt` możesz mieć np.:

```text
pytest
pytest-playwright
```

a po instalacji zależności wykonujesz:

```bash
playwright install
```

W CI/CD często wygląda to więc mniej więcej tak:

```bash
pip install -r requirements.txt
playwright install
pytest
```

### Krótka definicja do notatek

> **`playwright install`** – polecenie CLI Playwright służące do pobrania i instalacji przeglądarek używanych przez
> Playwright (`Chromium`, `Firefox`, `WebKit`). Nie jest biblioteką ani pluginem, lecz krokiem konfiguracji środowiska
> potrzebnym do wykonywania testów Playwright.

---

## 📕allure-pytest-bdd

Allure Report `allure-pytest-bdd` to plugin integrujący **Allure Report** z **pytest-bdd**.

Jego zadaniem jest sprawienie, żeby testy napisane w BDD za pomocą `pytest-bdd` były odpowiednio zbierane i prezentowane w raporcie Allure.

Czyli:

```text
pytest-bdd
    ↓
testy BDD / Gherkin
    ↓
allure-pytest-bdd
    ↓
Allure
    ↓
raport testów
```

### 1. Po co jest `allure-pytest-bdd`?

Sam `pytest-bdd` pozwala uruchamiać scenariusze:

```gherkin
Scenario: Successful login
    Given the user is on the login page
    When the user logs in
    Then the dashboard is displayed
```

Natomiast `allure-pytest-bdd` pozwala przekazać informacje o wykonaniu tych scenariuszy do Allure, dzięki czemu raport może przedstawiać strukturę BDD w czytelnej formie.

Możesz więc zobaczyć m.in.:

* `Feature`
* `Scenario`
* kroki `Given / When / Then`
* status testu
* czas wykonania
* błędy i stack trace
* załączniki
* screenshoty
* informacje o środowisku

### 2. Instalacja

Instalujesz plugin przez:

```bash
pip install allure-pytest-bdd
```

W projekcie, w którym używasz również zwykłego `allure-pytest`, możesz mieć oba pluginy, ale ich role są różne:

```text
allure-pytest
      ↓
zwykłe testy pytest

allure-pytest-bdd
      ↓
testy pytest-bdd
```

### 3. Przykład

Masz scenariusz:

```gherkin
Feature: Login

  Scenario: Successful login
    Given the user is on the login page
    When the user enters valid credentials
    Then the dashboard should be displayed
```

oraz implementację:

```python
from pytest_bdd import given, when, then


@given("the user is on the login page")
def open_login_page(page):
    page.goto("https://example.com/login")


@when("the user enters valid credentials")
def enter_credentials(page):
    page.get_by_label("Username").fill("user")
    page.get_by_label("Password").fill("password")


@then("the dashboard should be displayed")
def verify_dashboard(page):
    assert page.get_by_role("heading", name="Dashboard").is_visible()
```

Uruchamiasz:

```bash
pytest --alluredir=allure-results
```

Po wykonaniu testów powstają dane dla Allure w katalogu:

```text
allure-results/
```

Następnie możesz wygenerować raport:

```bash
allure serve allure-results
```

### 4. Co daje to w raporcie?

Zamiast widzieć wyłącznie techniczną nazwę funkcji Pythona:

```text
test_login.py::test_successful_login
```

raport może prezentować test w kontekście BDD:

```text
Feature: Login

  Scenario: Successful login
      Given the user is on the login page
      When the user enters valid credentials
      Then the dashboard should be displayed
```

To jest szczególnie przydatne w projektach, gdzie scenariusze BDD mają być czytelne również dla osób nietechnicznych.

### 5. `allure-pytest-bdd` a `allure-pytest`

Warto zapamiętać różnicę:

| Plugin              | Do czego służy                       |
| ------------------- | ------------------------------------ |
| `allure-pytest`     | integruje Allure z pytest            |
| `allure-pytest-bdd` | integruje Allure z pytest-bdd        |
| `pytest-bdd`        | umożliwia pisanie testów BDD/Gherkin |
| `allure`            | generuje i prezentuje raporty        |

Czyli `allure-pytest-bdd` jest **warstwą integracyjną**, a nie osobnym frameworkiem testowym.

### 6. W Twoim stacku

Jeżeli używasz jednocześnie:

* `pytest`
* `pytest-bdd`
* `pytest-playwright`
* `allure-pytest-bdd`

to całość może wyglądać tak:

```text
                    pytest
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
     pytest-bdd             pytest-playwright
          │                       │
          ↓                       ↓
     Gherkin/BDD              Playwright
          │                       │
          └───────────┬───────────┘
                      ↓
                   Testy
                      │
                      ↓
             allure-pytest-bdd
                      │
                      ↓
                 Allure Report
```

A w przypadku Twojego projektu automatyzacji UI mogłoby to oznaczać:

```text
.feature
   ↓
pytest-bdd
   ↓
Python step definitions
   ↓
pytest-playwright
   ↓
Playwright
   ↓
Browser
   ↓
allure-pytest-bdd
   ↓
Allure Report
```

### Krótka definicja do notatek

> **allure-pytest-bdd** – plugin integrujący Allure Report z `pytest-bdd`, umożliwiający raportowanie testów BDD/Gherkin
> w Allure, wraz ze scenariuszami, krokami `Given/When/Then`, statusami, błędami i załącznikami.
