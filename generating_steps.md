# Kroki przy generowaniu danych

Skonsolidowane instrukcje, które wszyscy robiliśmy. Warto przeczytać dodatkowo `doc\db-struct.md`, żeby wiedzieć jakie kolumny ostatecznie mają wszędzie być i co jest czym, gdyby coś było pominięte.

Można na razie robić kody w jakimś Jupyter Notebooku. Później się je przeklei.

## Pierwsza faza - przygotowanie

Wczytanie wszystkich tabel przygotowanych z csvek jako `prompt_games`, `prompt_last_names_male` itp.

Ustalam gdzieś datę otwarcia sklepu na 2 lata wstecz.

Konstruuję tabelę `prompt_dates`, gdzie mamy daty, dni tygodnia do dat, ale wyrzucamy wszystkie święta i niedziele. Z niej będziemy wymyślać daty, a dni nierobocze nie będą potrzebne.

## Druga faza - tabele pomocnicze

### Pracownicy

Biorę liczbę pracowników 6 i tworzę takiej długości DataFrame (będzie jedna podmianka).

Pięciu pierwszym nadaję daty rozpoczęcia pracy z otwarciem sklepu. Losuję moment zwolnienia piątego typa z rozkładu podobnego do normalnego po indeksach z dat `prompt_dates`. Nadaję mu taką datę zwolnienia i następny dzień jako zatrudnienie pracoenika nr 6. Wszyscy oprócz zwolnionego NaN w dacie końca pracy.

- wybieram płeć z równym prawdopodobieństwem
- dla konmkretnej płci losuję imię i nazwisko z rozkładami z kolumy na `prompt_first_names_male`, `prompt_last_names_male` podzielopnej przez sumę wszystkiech w kolumnie (jako wagi) itp.
- dać każdemu losowo ciąg 9 znaków jako nr tel, ale nie jest on dowolny! Słyszałem, że problemem w ocenie może być to jak się zaczynają (tu mamy od jakich liczb rozpoczynają się numery telefonów w Polsce: https://pl.wikipedia.org/wiki/Numery_telefoniczne_w_Polsce)
- nadać mail z połączenia imienia i nazwiska 'first_name.last_name@poczta.pl'. Skrzynkę pocztową losować z CSVki możliwych stron (jeszcze jej nie ma).
- losuję - podobnie jak imię - miasto. zapisuę w kolumnie CITY ich miasto słownie (tak, na razie pewnie łatwiej będzie umieścić to tutaj i takich zabiegów jest więcej. czysszczenie w fazie III)
- losujemy płacę dla każdego (poprzedczka 3490 + Exp z jakąś lambdą -- żeby były różne ale wszystkie większe od zadanego minimum)
- nadaję updated_at jako większą z daty zatrudnienia i zwolnienia (tylkjo tak żeby nulle nie przeszkadzały)
- temu z największą płacą nadaję stanowisko managerskie
- nadaje im id po kolei
  
### Związki

Biorę `N` relacji = ceil(liczba pracowników * 1.5)

- Lecę w pętli po `i` in range(`N`):
  - losuję pracownika z wagą będącą jego zarobkami i przepisuję jego id oraz `i` jako staff_id i partner_id oraz jeszcze płeć pracownika na razie
  - liczba randek: losuję liczbę z rozkładu normalnego o średniej 5 i odchyleniu 2 zaokrągloną
  - biorę losową równomiernie datę od rozpoczęcia pracy pracownika do momentu bierzącego i zapisuję ją do updated_at

- nadaję im id po kolei numerki

### Partnerzy

- Biorę tychże partnerów i ich id i przydzielam im płeć z prawdopodobieństwem 0.9 odwrotną do płci pracownika
- według tej płci losuję imiona, tak jak dla pracowników
- przepusuję updated_at ze związków
- nadaję id po posortowaniu datami

### Klienci - część A

- na razie tylko dataframe z ich indexami. Niech będzie ich 1500 na razie.

### Koszty utrzymania

Konstruuję to tak, że na razie będzie tu więcej rzeczy niż trzeba. Wykonuję kilka kroków, uzupełniając po kolei wydatki w pomocniczej tabeli. Wpisujemy datę, tytuł, kwotę, typ.

#### Czynsz

- daję 5 dzień każdego miesiąca funkcjonowania sklepu z `prompt_dates` jako dzień zapłaty za czynsz. Zawsze niech będzie to 3250.
- piszę tytuł 'czynsz [nazwa miesiąca]'
- dodaję kolumnę z typem "czynsz"

#### Energia elekryczna

- znów z piątym dniem miesiąca podobnie. teraz daję tytuł 'energia elektryczna [nazwa miesiąca]' i wartość z rozkładu max( N(130, 4), 100). To "max" to takie zabezpieczenie żeby nie było...
- typ daję jako "media"

#### Woda

- analogicznie. typ: media; rozkład N(30, 2), zabezpieczenie że większe od 15, tytuł woda i nazwa miesiąca

#### Ogrzewanie

- TYLKO OD LISTOPADA DO MARCA!!!! daję typ media, tytuł z ogrzewanie i nazwa miesiąca a wartość np. N(80, 4) ale no żeby nie było ujemne itp
  
#### Płace

- co miesiąc dnia 1go _dla każdego_ pracownika, wg jego płacy (taka jaka jest teraz)
- typ zapisuje jako "pensja"
- tytuł jako "pensja [miesiąc] [imię i nazwisko pracownika]"

- Wpisujemy daty updated_at wtedy kiedy była płatność.
- Teraz sortujemy wszystko datami i "reindeksujemy". chodzi o to żeby mieć kolumnę z id płatności oraz (narazie taką samą) wstępną id faktury

### Tytuły wydatków

Tak to jest dziwne, ale EKNF czasem przesadza.

- biorę wszystkie unikalne tytuły i kategorie z 




%%%%%% tu dodaję kolejne rzeczy

## Trzecia faza - czyszczenie tabeli pomocniczych, indeksowanie

## Czwarta faza - ostateczne tabele z tabel pomocniczych
