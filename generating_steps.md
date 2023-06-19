# Kroki przy generowaniu danych

Skonsolidowane instrukcje, które wszyscy robiliśmy. Warto przeczytać dodatkowo `doc\db-struct.md`, żeby wiedzieć jakie kolumny ostatecznie mają wszędzie być i co jest czym, gdyby coś było pominięte.

Można na razie robić kody w jakimś Jupyter Notebooku. Później się je przeklei.

**Używamy przemyślanych nazw zmiennych, żeby się potem nie pogubić.**

## Pierwsza faza - przygotowanie

- Wczytanie wszystkich tabel przygotowanych z csvek jako `prompt_games`, `prompt_last_names_male` itp.

- Ustalam gdzieś datę otwarcia sklepu na 2 lata wstecz.

- Konstruuję tabelę `prompt_dates`, gdzie mamy daty, dni tygodnia do dat, ale wyrzucamy wszystkie święta i niedziele. Z niej będziemy wymyślać daty, a dni nierobocze nie będą potrzebne.

- Modelujemy od razu ruch - na razie tylko dla dni. To ułatwi dalsze poczynania, bo tylko się dostawi temat z godzinami:
  - ustalamy A = początkową l. klientów bez dodania zmian natężenia i B = średni dzienny wzrost
  - zapisujemy jako np kolumnę `volume_base` w `prompt_dates` najpierw wartości floor(A + numer dnia * B) (spróbujmy z A = 6 i B = 0.01 - **będzie można tym manipulować gdyby sklep bankrutował**)
  - dodajemy przykładowo dniami tygodnia +2 w pon, +1 we wt, +0 w śr, +4 w czw, +5 w pt, +5 w sob.
  - do kolumny `volume_sales` dajemy max(0, `volume_base` + round(Normal(0, 1.5)))
  - do kolumny `volume_rental` dajemy max(0,  round(40% * `volume_base` + Normal(0, 1.5))) - osobno losujemy ten szum, żeby to nie było zależne
  - można próbowac manipilować tymi A, B czy dziennymi dodatkami, aby wychodziło ok. 1500 w sumie (nie wiem czy na rok czy w ogóle - tu pytanie do Natalii)

- Jeszcze robimy tabelę procentową z numerami godzin od 8-19 (bo sklep czynny 8-20 i godz. nr 19 trwa od 19 do 20) oraz jakąś liczbą natężenia (np. nazywamy `prompt_hours`)
  - można to wpisać ręcznie w CSV wczreśniej nawet, ale ogónie może przypominać taki przebieg, że rano mało, najwięcej osób koło 17 i samym wieczorem znowu mniej
  - przerabiamy tę tabelę tak, że dzielimy liczby przez ich sumę, otrzymując wagi godzinowe sumujące się do 1

- Jeżeli nie ma nigdzie popularności gier, to randomowo ułożyć gry z `prompt_games` ale przełożyć jamniczki na górę, a następnie w stylu gęstości rozkładu exp nadać im wagi. zrobić tak, żeby sumowały sie do 1.

## Druga faza - tabele pomocnicze

### Pracownicy

Biorę liczbę pracowników 6 i tworzę takiej długości DataFrame (będzie jedna podmianka).

Pięciu pierwszym nadaję daty rozpoczęcia pracy z otwarciem sklepu, godziną 9:00. Losuję moment zwolnienia piątego typa z rozkładu podobnego do normalnego po indeksach z dat `prompt_dates`. Nadaję mu taką datę zwolnienia i następny dzień jako zatrudnienie pracoenika nr 6. Wszyscy oprócz zwolnionego NaN w dacie końca pracy.

- wybieram płeć z równym prawdopodobieństwem
- dla konmkretnej płci losuję imię i nazwisko z rozkładami z kolumy na `prompt_first_names_male`, `prompt_last_names_male` podzielopnej przez sumę wszystkiech w kolumnie (jako wagi) itp.
- dać każdemu losowo ciąg 9 znaków jako nr tel, ale nie jest on dowolny! Słyszałem, że problemem w ocenie może być to jak się zaczynają (tu mamy od jakich liczb rozpoczynają się numery telefonów w Polsce: https://pl.wikipedia.org/wiki/Numery_telefoniczne_w_Polsce) NUMERY NIE MOGĄ SIE POWTARZAĆ TEŻ!!!!
- nadać mail z połączenia imienia i nazwiska 'first_name.last_name@poczta.pl'. Skrzynkę pocztową losować z CSVki możliwych stron (jeszcze jej nie ma). EMAILE TAK SAMO NIE MOGĄ SIE POWTARZAĆ (jakby tak było to należy dodać jakiś numerek albo co)!!!!
- losuję - podobnie jak imię - miasto. zapisuę w kolumnie CITY ich miasto słownie (tak, na razie pewnie łatwiej będzie umieścić to tutaj i takich zabiegów jest więcej. czysszczenie w fazie III)
- losujemy płacę dla każdego (poprzedczka 3490 + Exp z jakąś lambdą -- żeby były różne ale wszystkie większe od zadanego minimum)
- nadaję updated_at jako większą z daty zatrudnienia i zwolnienia (tylkjo tak żeby nulle nie przeszkadzały)
- temu z największą płacą nadaję stanowisko managerskie
- nadaje im id po kolei

### Godziny pracy (nie używana w bazie ale pomocna)

Można stworzyć tabelę week_day-hour-worker.

- każdy rekord ma dzień od poniedziałku do soboty i "numer" godziny - od 8 do 19 (bo sklep jest otwarty 8-20, pon-sb. jest do 19 bo godz. nr 19 trwa 19-20)
- bierzemy więc wszystkie kombinacje
- dajemy przy kazdym np listy z pracownikami, co ręcznie można zadać, jak poniżej.

Dla prostoty robimy to z góry tak, że

- pierwszych dwóch pracuje pon-czw 8-15 i sob nd 8-14 (etat się zgadza)
- reszta od pon do czw 14-20 i w piątek i sobotę 12-20.

### Związki

Biorę `N` relacji = ceil(liczba pracowników * 1.5)

- Lecę w pętli po `i` in range(`N`):
  - losuję pracownika z wagą będącą jego zarobkami i przepisuję jego id oraz `i` jako staff_id i partner_id oraz jeszcze płeć pracownika na razie
  - liczba randek: losuję liczbę z rozkładu normalnego o średniej 5 i odchyleniu 2 zaokrągloną
  - biorę losową równomiernie datę od rozpoczęcia pracy pracownika do momentu bierzącego i zapisuję ją do updated_at (godzina niech będzie 8:00)

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

Do updated_at zapisuję oprócz daty godzinę jakąś z przedziału 8-20 ale dowolną.

#### Czynsz

- daję 5 dzień każdego miesiąca funkcjonowania sklepu z `prompt_dates` jako dzień zapłaty za czynsz. Zawsze niech będzie to [1000 albo 3250 - w dokumencie mamy napisane 1000 ale nwm czy to jest realna kwota za lokal. nawet za mieszkanie płaci się więcej].
- piszę tytuł 'czynsz [nazwa miesiąca]'
- dodaję kolumnę z typem "czynsz"

#### Energia elekryczna

jakoś rozdysponowałem kwotę 500, którą napisał Adam:

- znów z piątym dniem miesiąca podobnie. teraz daję tytuł 'energia elektryczna [nazwa miesiąca]' i wartość z rozkładu max( N(150, 4), 100). To "max" to takie zabezpieczenie żeby nie było...
- typ daję jako "media"

#### Woda

- analogicznie. typ: media; rozkład N(50, 2), zabezpieczenie że większe od 15, tytuł woda i nazwa miesiąca

#### Ogrzewanie

- TYLKO OD LISTOPADA DO MARCA!!!! daję typ media, tytuł z ogrzewanie i nazwa miesiąca a wartość np. N(100, 4) ale no żeby nie było ujemne itp
  
#### Płace

- co miesiąc dnia 1go _dla każdego_ pracownika, wg jego płacy (taka jaka jest teraz)
- typ zapisuje jako "pensja"
- tytuł jako "pensja [miesiąc] [imię i nazwisko pracownika]"

- Wpisujemy daty updated_at wtedy kiedy była płatność.
- Teraz sortujemy wszystko datami i "reindeksujemy". chodzi o to żeby mieć kolumnę z id płatności oraz (narazie taką samą) wstępną id faktury

### Tytuły wydatków

Tak to jest dziwne, ale EKNF czasem przesadza...

- biorę wszystkie tytuły z kosztów utrzymania
- przepisuję je razem z kategorią i updated_at do tej tabeli
- robię drop_duplicates (po samym tytule oczywiście) - tak na wszelki wypadek, zostawiając ostatni wiersz
- indeksuję

### Typy wydatków

- powtarzam proces z tytułów konstruujac tabelę wydatków. też indeksuję

### Wydatki i tytuły jeszcze raz

- Mając indeksy w tabeli typów wydatków, zamieniam w tabeli te tytuły wydatków na indeksy z tamtej tabeli. może byc pd.merge(..., how="left) - czyli taki left joinik
- podobny manewr robię w wydatkach w ogóle, tym razem dopisując indeksy bazujac na tytułach

### Turnieje

Należy zadbać o to by NA PEWNO przynajmniej 5 turniejów było w ostatnim roku. Nadajmy takie ograniczeniee przy generówaniiu gdzieś dat.

- biorę liczbę turniejów w ogóle (np tak po 10 na rok) i rozdzielam równomiernie w sensie terminów
- zapisuję ich daty startu dając jakiś szum np. Normal(0, 2 dni tabeli `prompt_dates`) ograniczony datami dzialaności sklepu. godninę startu dajemy jako 15:00 zawsze
- daję im nazwy wg pliku
- daję wg typu itp grę, która jest w turnieju (to musi mieć sens) - patrzę też oczywiście tylko na konkursowe z tabeli
- dodaję deldline zapisów np. 3 dni - tydzień wcześniej
- daję opłatę zawsze 50 zł.
- obliczam rundy, tworząc też kolumnę referencyjną przy zapisach uczestników:
  - biorę z CSV S = liczbę maksymalnie grających w grę
  - robię liczbę chętncyh C = round(losowo z rozkładu uniform(5,8) (z przecinkami) * S)
  - biorę taką najmniejszą liczbę B, że 2^B >= C
- dodaję ilość jako liczbę rund obliczoną rund (2^B + 2^(B-1) + ... + 2 + 1) - bo to jest takie drzewo rozgrywek
- jakies (zwykle podobne) koszty koło
- losuję jakiś nieduży (ok do 200zł może) koszt organizacji turnieju z sensownaego rozkładu, dodaję do niego jakiś numer faktury
- losuję z pracowników od razu indeks pracownika ale patrząc na tabelę kiedy kto pracuje (ona jest stworzona i dość prosta w obsłudze. pracownik musi być bowiem w pracy podczas turnieju)
- updated at zawsze data i godzina turnieju


### Udziały

- biorę dany turniej i jego liczbę C. losuję tyle uczestników z pośród indeksów uczestników.
- dodaję za każdym razem datę zapisu w jakimś rozkładzie oczekiwania, oczywiście sprzed daty "deadline zapisów" (czyli np deadline-Poisson(1)) i losowa godzina z czasu działalności sklepu
- w każdej z takich grup daję im miejsca jakieś, które zajęli. raczej zupełnie równomiernie i losowo.
- dodaję płatności - przepisuję fee z turnieju
- updaded_at jest datą+godziną zapisu i też służy potem przy ogarnięciu płatności

- jak to wszystko przeprowadzę, to sortuję po datach i po kolei datami nadaję indeksy

### Magazyn

losujemy w kilku krokach wszystkie pozycje. będziemy zapisywac tytuły gier a dopiero później przenosic je do innej tabeli. Dodajemy też ceny zakupu z hurtowni które poźniej przeniesiemy do payments.

#### Sprzedażowe

- losuję N - liczbę gier sprzedażowych w ogóle. dobym pomysłem będzie wzięcie `prompt_dates` i zsumowanie wszystkich volume_sales * (1.6 + rozkład exp z jakąś lambdą)
- mając wagi gier (która najlepiej się sprzedaje) grupami (może być w pętli) jechać tak:
  - konstruować waga*N wierszy danych tytułów (aby proporcaj popularności była spełniona)
  - podzielić na podgrupy tak, żeby było M = (5 * lata_funkconowania_sklepu) i biorąc daty jako M + Normal(0, 5 dni) ale ograniczać z dołu i góry rpzez daty funkcjonowania skepeu na wszelki wypadek
  - w każdej podgrupie daję wspólny indeks fakruty. może byc `i` po którym iterujemy, ale żeby było unikalne dla partii zamówionych gier i danego tyułu
  - nadaję każdej grze cenę, równą cenie z tabeli z CSV
  - nadaje updated_at oraz datę przyjścia zamówienia taką samą - jako datę wylosowaną w drugim pod-kroku
  - nadaję wszystkim pozycjom w podgrupie takie same ceny zakupu z hurtowni (80% ceny draft - można tę liczbę zmodyfikować)
- wszystkim dajemy active=TRUE na razie
- ndaję przeznaczenie S

tu można jeszcze zakombinować coś jak pozwoli czas

#### Rentalowe

- losuję N - liczbę gier rentalowych. biorę tak około 70 chyba max (Nie jestem pewien, ale tych gier na pewno nie będzie za dużo. nie jestem pewien jak o tym myśleliście)
- losuję te N gier analogicznym schewmatem jak sprzedażowe
- ...ale daty przyjscia do magazynu daję na rozpoczęcie działalności sklepu, że niby te do wypożyczenia były od początku i nie zdązyły się zepsuć bo to tylko 2 lata. niech to bedzie w uproszczeniu na osobną fakture niż spraedażowe
- ...jednak, jak już będą wypełnione gry z hurtowni, to przekształcam normalną cenę żeby było to 10% tej wartości (jeżeli okaze się za mało, można zwiększyć troche)
- wszystkim dajemy active=TRUE na razie. 2 losowe można trzasnąć z FALSE, że niby się coś popsuły
- ndaję przeznaczenie R

#### Turniejowe

- grupuję tabelę turniejów po grach i biorę maksymalną liczbę B w grupach, bo jest to liczba partii na najniższym poziomie
- schematem podobnym do powyższych losuję te gry, ale po prostu biorę tylko te gry, które kiedyś były w turniejach już i biorę każdego liczbę nie inną niż B (mogłoby być lepiej ale to na pewno zabezpiecza logikę)
- ceny zostawiam NaN
- nadaję przeznaczenie T
- daty przyjscia do magazynu daję na rozpoczęcie działalności sklepu, że niby były od początku i nie zdązyły się zepsuć bo to tylko 2 lata. niech to bedzie w uproszczeniu na osobną fakture niż spraedażowe

Łączę to wszysttko razem w jedną tabelę.

### Ceny gier

- grupuję magazyn po tupli kolumn (tytuł, przeznaczenie) i patrzę jakie są ceny (nie "draft" tylko te już koncowe), patrzę też na ostatnie updated_at grupy
- przekładam te ceny do tabeli z cenami gier i przepisuję z danej "grupy" updated_at
- indeksuję a indeksy daję jako klucze obce do cen na magazynie

### Sprzedaże

pRzygotowuję "magazyn sprzedażowy", czyli mający same przeznaczenia "S"

- biorę kolumnę `volumne_sales` z `prompt_games` czyli już ustalone losowe liczby kupujących klientów na każdy dzień
- idę w pętli for po dniach z jakimś `j`:
  - obsługuję w ten sposób osobno kazy dzien funkcjonowania sklepu
  - konstruuję pętlę for po jakimś `i` in range(liczba_klientów w volume_sales tego dnia), gdzie robię taki manewr:
    - losuję klientowi przedział godzinowy zakupów z wagami z tej tabeli gdzie one zostały stworzone
    - losuję z rozkładu równomiernego minuty i sekundy od 0 do 1 h
    - mam w ten sposób całą datę&godzinę zakupu
    - losuję liczbę `P` gier zamierzonych do kupna przez klienta na raz. najczęściej 1 (np 70% szans) 2 (25 %) 3 (5 %)
    - z gier (gier a nie magazynu!) losuję wg prawdopodobieństwa opisanego w tejże tabeli z grami `P` gier
    - filtruję magazyn sprzedażowy, który sobie w tym kroku przygotowaliśmy po polu ACTIVE=TRUE (bo chcę gry dostępne)
    - obcinam po dacie dostawy gry tak, żeby nie było sytuacji że kupuję profdukt, którego jeszcze nie było wtedy w sklepie i sprawdzam czy są właśnie
      - jeżeli dana gra jest na magazynie to zmieniam jej status active na FALSE i dodaję do nasztych `sales`
      - jeżeli nie ma takiej gry, to po prostu pomijam temat i uznajemy że klient chciał ale nie było to trudno
    - w tabeli magazynu cały czas jest jako robocza kolumna końcowa cena - przepisuję ją tu jako wartość płatności roboczo
    - losuję pracownika tak jak to jest zrobiono przy turniejach (czyli losując równomiernie z uwzględnieniem godzin pracy i dnia tygodnia, a te przecież znamy)
    - nadaję indeks faktury równy tupli (i, j)
    - nadaję updated_at takie jak data własnie jest.

Przez powatarzaenie w pętlach mam wszystkie zakupy. Jakby coś nie wychodzilo to można modyfikować m.in. A i B przy wypełnianiu magazynu.

### Rentale

Stosuję podobny proces do tego z tabeli sprzedażowwymi ale z drobnymi różnicami:

- używam `volume_rental`, czyli inne liczby klientów w ogóle; oraz używam przeznaczenia "R"
- muszę równomiernie dolosować jakieś id klienta
- mechanizm pożyczneia-zwrotu:
  - za każdym razem jak ktoś wypożycza grę, to daję active=FALSE
  - losuję natomiast jeszce czas przetrzymania gry, czyli dodatnią liczbę o rozkładzie  gamma z parametrami: skali=3, kształtu=2 (nie koniecznie całe!!! mają cyć z godzinami itp)
  - datę pożyczenia już mam bo wylosowana oczywiście, ale dodając czas przetrzymania do niej, konstruuję datę oddania. jeżeli jest ona większa niż "dzisiejsza" data, no to zostawiam NULL
  - jeżeli data oddania nie jest null, dodaję karę w wysoikości
  - kara ze względu na logikę rozumowania (opis w rental dokumentu db_struct.md) musi być jednak naliczana inaczej niż ustalono -- jako powiedzmy 30% ceny wypożyczenia za każdy rpzekroczony dzień. taką sumę wpisac należy w karę
  - jeżeli data oddania nie jest null, AGAIN, ZMIENIAMI ACTIVE=TRUE (bo jest gra znów w sklepie i można brac ją)
  - updated at to data zwrotu, a jeśli null to data rentalu
- losuję zawsze jeszcze przez jakieś zaokrąglenie i obcięcie rozkładu pewnego oceny gier od 1 do 10 czy coś takiego (np. scipy.stats.skewnorm)

Jest dopisane jeszcze założenie że klient nie może mieć 3 gier w tym samym czasie. Jeżeli uda sie to łatwo zaimplementować to można.

### Gry

- wszustkie użyte w inventory gry przekładam sobie do tabeli z grami
- nadaję updated_at takie, jak pierwsze kupno gry w magazynie (to można sb pogrupować i wziąć min)
- w sumie kopiuje informacje z `prompt_games`, żeby tam

### Kateorie gier i typy gier

- unikalne kategorie i typy, obecne w tabeli z grami, przezucam do tych tabel, nadaję indeksy (sortując pierwej wg dat wystąpienia)
- dodaję potem te indeksy w grach jako klucze obce

### Klienci - część B

- patrzę na udziały w zawodach oraz rentale. "klientów", którzy nic nie zrobili usuwam po prostu z tabeli
- biorę wszystkie udziały i rentale, grupując po kliencie. w tabeli klientów przepisuję te daty jako min z obu jako updated_at (to jest "data rejestracji")
- sortuję po tych datach rejestracji i dodaję im wtedy kluczę. w tabelach dot. udziałów w turniejach i rentalach przypisuję klucze obce wg nowego schematu - czyli tłumacząc stare id klientów na nowe, już ostateczne.
- numery tel i emaile nie mogą się powtarzać ani tu między sobą, ani z tabelą `staff`. należy to sprawdzać i ewentualnie losować ponownie

Do tego oczywiście:

- losuję dane osobowe customerów podobnym schematem jak u pracowników, tylko oczywiście jest mniej dancyh potrzebnych

### Miasta

- patrze na wszystkie miasta, które mieli klienci i pracownicy, a następnie zapisuję do miast, przepisując updated_at od klienta za każdym razem jak się dodaje wiersz tu
- sortuje po updated_at i robię drop_duplicates tak, że zostaną tylko te pierwsze wpisy. następne się "ignoruje"
- indeksuję sobie, czyli dodaje klucz główny i nazwy miast tłmaczę w tabelach pracowników i klientów na te numeryczne klucze obce

### Payments i invoices

- (`payments`) zbierazm z wszystkich tabel płatności oraz numetry faktur i zapisuję je do płatności na razie razem z datami, co są zawsze podane
- chodzi o tabele sprzedaży, rentali, wydatków utrzymaniowych, turniejów, udziałów turniejowych i magazynu
- wprowadzam robocze "id faktury": robię tak, że łącze prefiks (np. symbol nazwy tabeli) i numer faktury tam nadany. jest to konieczne bo numery faktur są unikalne w tabelach ale nie pomiędzy nimi
- grupuję po roboczym id wszysstkie faktury i zapisuje unikaty wraz z tymi datami, które mają do tabeli `invoices`
- mogę przesunąć timestamp tych płatności ewentualnie o tak max godzinę z jakiegoś rozkładu Exp, bo czasem wchodzą później
- updated_at niech zostaje takie jak powyższa wartość
- sortuję te faktury w tabeli `invoices` po ich czasach i nadaję im nowe id jako kolejne numerki
- tłumaczę robocze id w `payments` na nowe id, dodając updated_at takie jak w `invoices`

## Trzecia faza - ostateczne tabele z tabel pomocniczych

- w turniejach przerabiam analogicznym jak użwyany niejednokrotnie schematem tyuły gier na indeksy gier z tabeli games
- sumujemy payments i sprawdzamy czy jesteśmy na plusie. jak nie no to trzeba znacznie parametry zwiększyć, żeby było bezpiecznie
- wyrzucam wszystkie niepotrzebne kolumny
- sprawdzam czy wszystko co trzeba jest i czy jest doprze poindeksowane
- jako rezultat jest lista zmiennych z gotowymi tabelami, które mają nazwy kolumn takie jak zaprojektowanej bazie danych
