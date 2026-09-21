# 🛠️Konfiguracja projektu – notatki

# 📑Spis treści

1. [🔧Konfiguracja](#konfiguracja)
   - [Python – Instalacja](#python--instalacja)
   - [IDE PyCharm  – Instalacja](#ide-pycharm--instalacja)
   - [GitHub – Tworzenie i klonowanie repozytorium](#github--tworzenie-i-klonowanie-repozytorium)
   - [Dependencies – Instalacja](#dependencies--instalacja)

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
   🔴TODO: Opisać dependencies
   - **pytest-playwright**
   - **pytest-bdd**
   - **playwright install**
   - **allure-pytest-bdd** 🔴TODO
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
