[![Status](https://img.shields.io/badge/status-alpha-orange)]()
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

# Geeks & Dragons database

<a id="geeks-n-dragons-database"></a>
  
## Spis treści

<a id="spis-tresci"></a>
  
Strona główna:

- [Geeks \& Dragons database](#geeks--dragons-database)
  - [Spis treści](#spis-treści)
  - [Wstęp](#wstęp)
  - [Opis projektu](#opis-projektu)
    - [Cel](#cel)
    - [Elementy](#elementy)
    - [Wyzwania](#wyzwania)
  - [Struktura projektu](#struktura-projektu)
  - [Szczegóły dotyczące bazy](#szczegóły-dotyczące-bazy)
  - [Sposób użycia](#sposób-użycia)
    - [1. Instalacja głównych narzędzi](#1-instalacja-głównych-narzędzi)
    - [2. Pobranie repozytorium](#2-pobranie-repozytorium)
    - [3. Przygotowanie środowiska](#3-przygotowanie-środowiska)
    - [4. Uruchomienie głównej aplikacji](#4-uruchomienie-głównej-aplikacji)
  - [Technologie](#technologie)
    - [Podstawowe technologie](#podstawowe-technologie)
    - [Generowanie i analiza danych](#generowanie-i-analiza-danych)
    - [Generowanie raportów](#generowanie-raportów)
    - [Dokumentacja](#dokumentacja)
    - [Współpraca i przechowywanie kodu](#współpraca-i-przechowywanie-kodu)
  - [Autorzy](#autorzy)

Połączone strony:

- [Strukura i mechanika bazy danych](doc/db-struct.md),
- [Pliki projektu i konfiguracja](doc/file-struct.md),
- [Wrażenia z realizacji projektu](doc/impressions.md),
- [Dokumentacja kodu źródłowego](doc/src/index.html).

## Wstęp

<a id="wstep"></a>
  
Projekt _Geeks & Dragons database_ dotyczy kompleksowego systemu obsługi danych dla sklepu z grami nieelektronicznymi.

[Tę stronę](README.md) traktować można jako główną __dokumentację__ projektu. Ze względu na obszerność niektórych wątków, pewne kwestie - m.in. strukturalne - będą opisane szczegółowo na podstronach, do których odnośniki znajdują się w odpowiednich miejscach na tej stronie.

## Opis projektu

### Cel

Projekt został stworzony w ramach kursu Bazy Danych 2023 na Wydziale Matematyki Politechniki Wrocławskiej. Miał pokazać umiejętności projektowania wysokiej jakości baz oraz analizy znajdujących się w nich danych. Chodziło przy tym o to, aby osiągnąć wysoki poziom automatyzacji.

Oferowana funkcjonalność dotyczy generowania fikcyjnego stanu bazy danych w konkretnym momencie historii (z zachowaniem logiki relacji) oraz analizy tego stanu. Nie jest to pełny system obsługi, łącznie z wprowadzaniem na bieżąco produktów, klientów itp.

### Elementy

Baza posiada dane o

- pracownikach,
- asortymencie,
- odbytych turniejach, w tym zawodnikach i wynikach,
- terminarzu nadchodzących spotkań,
- informacjach finansowych,
- wypożyczeniach i sprzedaży.

Dobrze naśladują one rzeczywistość, ale znajdujemy równocześnie pewne uproszczenia. Jest to bowiem jedynie model, a nie prawdziwe dane.

Pełny projekt składa się zaś z następujących części:

1. projekt i utworzenie schematu,
2. skryptowe wpełnienie bazy,
3. analiza danych,
4. raport,
5. dokumentacja.

Punkt (1) i (5) zawierają się w dokumentacji, czyli tak jak wspomniano - tym pliku oraz jego podstronach. Punkty (2, 3, 4) są automatycznie przeprowadzane przez zaimplementowaną bibliotekę i opisane dokumentacji. Dodatkowo, część punktu (1), polegająca na tworzeniu bazy kodem SQL, jest elementem funkcjonalności tej biblioteki.

Gotowy raport jest dostępny w repozytorium i może być wyświetlony przez odpowiednie użycie głównego skryptu. Można też wygenerować nowy.

### Wyzwania

Projekt dotyczył wielu płaszczyzn i integracji licznych technologii.

__To co twórcy uważają, za najtrudniejsze w realizacji__, znajduje się na podstronie o [wrażeniach z realizacji projektu](doc/impressions.md).

## Struktura projektu

__Lista plików wraz z opisem ich zawartości__ dostępna jest na podstronie o [plikach projektu i konfiguracji](doc/file-struct.md). Są tam też instrukcje na temat ewentualnej konfiguracji związanej z połączeniem, sposobem generowania, albo szablonem raportu.

## Szczegóły dotyczące bazy

<a id="szczegoly-dotyczace-bazy"></a>
  
W osobnym dokumencie o [strukurze i mechanice bazy danych](doc/db-struct.md) przede wszystkim obejrzeć można __schemat bazy__, wraz z nazwami atrybutów, ich typami oraz oznaczeniami kluczy.
  
Dalej, opisane są tam metody konstrukcji tabel (razem z wyjaśnieniem rodzajów danych w poszczególnych kolumnach), założenia techniczne oraz __lista zależności funkcyjnych__. Wszystko w punktach - tabela po tabeli.
  
Na końcu znajdujemy też formalne __wyjaśnienie, że struktura spełnia standard EKNF__.
  
## Sposób użycia

<a id="sposob-uzycia"></a>
  
Poniżej przedstawiony jest w krokach __sposób użycia__ poszczególnych części aplikacji. Kroki (1-3) są przygotowawcze i dość oczywiste. Praca z właściwym skryptem i jego opcjami opisana jest w punkcie (4).

### 1. Instalacja głównych narzędzi

<a id="1-instalacja-glownych-narzedzi"></a>
  
Aby używać skryptów projektu, należy przede wszystkim zainstalować na urządzeniu [Pythona 3.9](https://www.python.org/downloads/release/python-390/). Używany będzie także terminal - dla systemu Windows korzystać należy z [GitBash](https://git-scm.com/download/), instalowanego razem z systemem Git.

Instrukcje instalacji dostępne są na podanych stronach internetowych.

[![PythonVersion](https://img.shields.io/badge/Python-3.9-blue)](https://www.python.org/downloads/release/python-390/)
[![GitBash](https://img.shields.io/badge/Git%20Bash-gray)](https://git-scm.com/download/win)

### 2. Pobranie repozytorium

Repozytorium można pobrać bezpośrednio przez wywołanie w termianlu Bash

```bash
git clone https://github.com/o-Mateo-o/geeks-and-dragons-db.git
cd geeks-and-dragons-db
```

Jeżeli cały projekt jest już na urządzeniu możesz pominąć ten krok otworzyć w folderze projektu terminal Bash.

### 3. Przygotowanie środowiska

<a id="3-przygotowanie-srodowiska"></a>

Aby przygotować się do użycia, należy uruchomić wirtualne środowisko ze wskazaną wersją Pythona oraz zainstalować zależności. W prosty sposób robimy to przygotowanym skryptem przygotowawczym:

```bash
source setup.sh
```

Jeżeli Python jest zainstalowany na niestandardowej ścieżce, można łatwo zmienić ścieżkę do niego w [skrypcie przygotowawczym](setup.sh). Nie ma też problemu z wywołaniem po kolei wskazanych w skrypcie komend osobno w terminalu.

### 4. Uruchomienie głównej aplikacji

<a id="4-uruchomienie-glownej-aplikacji"></a>
  
Główną aplikację, wypełniającą losowo bazę danych i otwierającą świeży raport, uruchamiamy przez

```bash
./database-manager.py -fro
```

Można jednak chcieć wykonywać pojedyncze kroki, podając jako argumenty inne flagi, niż pełne `-fro`.

- Jeżeli chcemy tylko wygenerować dane i uzupełnić bazę, używamy flagi `-f`/`--fill`.

- Jeżeli chcemy tylko dokonać analiz i wygenerować raport, służy do tego flaga `-r`/`--report`.

- Dodatkowo, można otworzyć przygotowany raport automatycznie. Do tego korzystamy z flagi `-o`/`--open`.

Kompleksowa pomoc dostępna jest także oczywiście po uruchomieniu.

```bash
./database-manager.py -h
```

__UWAGA!__ Za pierwszym razem możemy zostać zapytani o hasło. Postępowanie w tym przypadku jest opisane w pomocy (`-h`) oraz bezpośrednio przy komunikcie.

## Technologie

Główne __technologie__ różnych kategorii, używane przy realizacji projektu, wymienione są poniżej.

### Podstawowe technologie

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white)](https://mariadb.org/)
[![Shell Script](https://img.shields.io/badge/shell_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)

### Generowanie i analiza danych

[![MySQL](https://img.shields.io/badge/mysql%20connector-%23316192.svg?style=for-the-badge)](https://pypi.org/project/mysql-connector-python/)
[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white)](https://scipy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-%23eeeeee.svg?style=for-the-badge&logo=matplotlib&logoColor=black)](https://matplotlib.org/)

### Generowanie raportów

<a id="generowanie-raportow"></a>
  
[![Jinja](https://img.shields.io/badge/jinja-eeeeee.svg?style=for-the-badge&logo=jinja&logoColor=black)](https://jinja.palletsprojects.com/en/3.1.x/)
[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://dev.w3.org/html5/spec-LC/)
[![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS/Overview.en.html)
[![PDFKit](https://img.shields.io/badge/PDFKit-d6b947.svg?style=for-the-badge)](https://pypi.org/project/pdfkit/)

### Dokumentacja

[![Markdown](https://img.shields.io/badge/markdown-%23000000.svg?style=for-the-badge&logo=markdown&logoColor=white)](https://www.markdownguide.org/)
[![Pdoc](https://img.shields.io/badge/Pdoc-%23198030.svg?style=for-the-badge&logo=pdoc3&logoColor=black)](https://pypi.org/project/pdoc3/)

### Współpraca i przechowywanie kodu

<a id="wspolpraca-i-przechowywanie-kodu"></a>
  
[![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/o-Mateo-o/geeks-and-dragons-db)

## Autorzy

Projekt tworzyli członkowie grupy ___Jamniczki___:

- [Natalia Iwańska](https://github.com/natalia185),
- [Klaudia Janicka](https://github.com/klaudynka245),
- [Adam Kawałko](https://github.com/Adasiek01),
- [Mateusz Machaj](https://github.com/o-Mateo-o).
