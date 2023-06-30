# Struktura projektu i konfiguracja

## Spis treści

<a id="spis-tresci"></a>

- [Struktura projektu i konfiguracja](#struktura-projektu-i-konfiguracja)
  - [Spis treści](#spis-treści)
  - [Pliki projektu](#pliki-projektu)
  - [Konfiguracja](#konfiguracja)
    - [Połączenie](#połączenie)
    - [Generowanie danych](#generowanie-danych)
    - [Przygotowanie środowiska](#przygotowanie-środowiska)
    - [Generowanie raportu PDF](#generowanie-raportu-pdf)
  
Powrót do strony głównej: [README.md](../README.md).

## Pliki projektu

Poniższe drzewo projektu zawiera opisy zawartości folderów oraz poszczególnych plików. Zawartości niektórych folderów oznaczone są jako `...`. Można przez to rozumieć, iż dany folder ma wiele plików o tym samym, niewyróżniającym się charakterze, zgodnym z opisem folderu.

```
📦geeks-and-dragons-db
┣ 📂assets                      - zasoby potrzebne do generowania raportu
┃ ┣ 📂generated                 - pliki składowe raportu wygenerowane dynamicznie
┃ ┣ ┣ ...
┃ ┣ ┣ _temp_report.html         - tworzony w czasie generowania roboczy plik html raportu 
┃ ┣ 📂static                    - stałe elementy raportu
┃ ┣ ┣ 📜style.css               - reguły stylu dla raportu
┃ ┣ ┣ 📜template.html           - szablon raportu
┣ 📂config                      - pliki konfiguracyjne
┃ ┣ 📂prompts                   - zewnętrzne tabele (.csv) używane do losowania
┃ ┣ ┣ ...
┃ ┣ ⚙️database.connection.json  - podstawowe ustawienia połączenia z bazą
┃ ┣ ⚙️pdf.gener.json            - parametry związane z narzędziem wkhtmltopdf
┃ ┣ ⚙️random.settings.json      - parametry związane z generowaniem danych
┣ 📂doc                         - wszelkie pliki dokumentacji
┃ ┣ 📂images                    - ilustracje używane w dokumentacji
┃ ┣ ┣ 🖼️ERD_simplified.png      - uproszczony rastrowy schemat bazy danych
┃ ┣ ┣ 🖼️ERD.svg                 - pełny waktorowy schemat bazy danych                
┃ ┣ 📂src                       - dokumnetacja kodu źródłowego
┃ ┣ ┣ ...
┃ ┣ 📄db-struct.md              - dokumentacja mechaniki struktury bazy danych
┃ ┣ 📄file-struct.md            - dokumentacja struktury projektu i konfiguracji
┃ ┣ 📄impressions.md            - wrażenia po realizacji projektu
┣ 📂sql                         - komendy SQL używane przy projektowaniu bazy
┃ ┣ 📜tables.sql                - komendy tworzące tabele
┃ ┣ 📜views.sql                 - komendy tworzące widoki
┣ 📂reports                     - wygenerowane raporty
┃ ┣ ⚙️recent.json               - dane na temat raportów przechowywane u użytkownika 
┃ ┣ ...
┣ 📂src                         - kod źródłowy aplikacji zarządzającej bazą danych
┃ ┣ 📜__init__.py
┃ ┣ 📜app.py                    - funkcjonalność uruchomienia aplikacji
┃ ┣ 📜connection.py             - funkcjonalność odpowiedzialna za połączenie
┃ ┣ 📜drandom.py                - funkcjonalność generowania danych
┃ ┣ 📜fillup.py                 - funkcjonalność uzupełniania bazy
┃ ┣ 📜randutils.py              - pomocnicze metody do generowania danych
┃ ┣ 📜reader.py                 - funkcjonalność odczytu raportu
┃ ┣ 📜report.py                 - funkcjonalność generowania raportu
┣ 📂tests                       - paczka testująca src (chwilowo pusta)
┃ ┣ 📜__init__.py               
┣ 📜database-manager.py         - kod uruchamiający aplikację zarządzającą bazą danych
┣ 📄LICENSE                     - licencja projektu
┣ 📄README.md                   - plik głównej dokumentacji
┣ ⚙️requirements.txt            - informacje na temat zależności
┣ 📜setup.sh                    - skrypt przygotowujący środowisko
```

## Konfiguracja

### Połączenie

<a id="polaczenie"></a>

Domyślnie aplikacja łączy się z bazą danych i poprzez użytkownika określonych w `config/database.connection.json`. W razie potrzeby skorzystania z innych ustawień, można zmienić wartości w tym pliku.

Hasło dla określonej bazy i użytkownika dla bezpieczeństwa nie jest zapisane bezpośrednio w tym pliku. Jeżeli uruchomiona aplikacja poprosi o wpisanie hasła, należy na bieżąco je podać.

### Generowanie danych

Stałe związane z losowaniem danych do bazy można zmodyfikować w razie potrzeby w pliku `config/random.settings.json`.

Dodatkowo, wszystkie tabele `config/prompts/*.csv` można zastąpić według uznania innymi, ale trzymając się konwencji nazw kolumn, typu zawartości itp.

### Przygotowanie środowiska

<a id="przygotowanie-srodowiska"></a>

Komendy przygotowane w `setup.sh` (szczegóły użycia są przedstawione przy okazji [instrukcji obsługi aplikacji](../README.md#sposób-użycia)), zmodyfikować dla konkretnych warunków systemu. Powinny działać dla domyślnych ścieżek instalacji, ale nie musi tak być. Tak naprawdę plik ten służy wyłącznie do stworzenia i uruchomienia wirtualnego środowiska oraz zainstalowania zależności.

### Generowanie raportu PDF

Ścieżka do pliku wykonywalnego narzędzia _wkhtmltopdf_ znajduje się w pliku `config/pdf.gener.json`. Należy upewnić się, że wspomniany program faktycznie znajduje się pod tym adresem. Jest to wspominane także w [instrukcji obsługi aplikacji](../README.md#sposób-użycia).
