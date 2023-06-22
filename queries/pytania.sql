--1
SELECT YEAR(sa.date) year,
    MONTH(sa.date) month,
    st.first_name,
    st.last_name,
    COUNT(sa.sale_id) amount_of_sales,
    ROW_NUMBER() OVER (
        PARTITION BY YEAR(sa.date),
        MONTH(sa.date)
        ORDER BY COUNT(sa.sale_id) DESC
    ) AS rank
FROM sales sa
LEFT JOIN staff st USING(staff_id)
WHERE sa.return_oper IS FALSE
GROUP BY YEAR(sa.date),
    MONTH(sa.date),
    st.first_name,
    st.last_name
ORDER BY YEAR(sa.date),
    MONTH(sa.date),
    ROW_NUMBER() OVER (
        PARTITION BY YEAR(sa.date),
        MONTH(sa.date)
        ORDER BY COUNT(sa.sale_id) DESC
    );
--2
SELECT g.title,
    CONCAT_WS(" ", c.first_name, c.last_name) player
FROM customers c
    LEFT JOIN participations p USING(customer_id)
    LEFT JOIN tournaments t USING(tournament_id)
    LEFT JOIN games g USING(game_id)
WHERE p.place >= 1
    AND p.place <= 10
GROUP BY g.title;
--3a
SELECT g.title game,
    SUM(p.amount) amount
FROM games g
    LEFT JOIN inventory i USING(game_id)
    LEFT JOIN sales s USING(inventory_id)
    LEFT JOIN payments p USING(payment_id)
GROUP BY g.title
ORDER BY SUM(p.amount) DESC
LIMIT 5;
--3b
SELECT g.title game,
    SUM(p.amount) amount
FROM games g
    LEFT JOIN inventory i USING(game_id)
    LEFT JOIN rental s USING(inventory_id)
    LEFT JOIN payments p USING(payment_id)
GROUP BY g.title
ORDER BY SUM(p.amount) DESC
LIMIT 5;
--DODATKOWE
--1
-- jest mało kategorii więc pytanie ostatecznie moze być bardziej
-- szczegolowe niż "top 5". zrobmy po prostu analizę popularności kateg.

-- Racja Mateosiku
SELECT gm.game_category,
    COUNT(r.rental_id) + COUNT(s.sale_id) popularity
FROM game_categories gm
    LEFT JOIN games g USING(category_id)
    LEFT JOIN inventory i USING(game_id)
    LEFT JOIN rental r USING(inventory_id)
    LEFT JOIN sales s USING(inventory_id)
WHERE s.return_oper IS FALSE
GROUP BY gm.game_category
ORDER BY COUNT(r.rental_id) + COUNT(s.sale_id) DESC;
--2
(SELECT YEAR(s.date) year,
    MONTH(s.date) month,
    SUM(p.amount) amount
FROM payments p
    LEFT JOIN sales s USING(payment_id)
WHERE s.return_oper IS FALSE
GROUP BY YEAR(s.date),
    MONTH(s.date)
ORDER BY SUM(p.amount) DESC
LIMIT 1)

UNION ALL

(SELECT YEAR(s.date) year,
    MONTH(s.date) month,
    SUM(p.amount) amount
FROM payments p
    LEFT JOIN sales s USING(payment_id)
WHERE s.return_oper IS FALSE
GROUP BY YEAR(s.date),
    MONTH(s.date)
ORDER BY SUM(p.amount) ASC
LIMIT 1);

--3 
--- UWAGA, LEPIEJ ZMIENIĆ NA ANALIZĘ NP SPRZEDAŻY A NIE TURNIEJÓW
--- dni truniejowe losujemy jednostajnie i to niezbyt ciekawe

--- Słusznie Mateosiku
SELECT FORMAT(CAST(s.date AS DATE), 'ddd') name_of_day,
    COUNT(s.sale_id) amount_of_sales
FROM sales s
GROUP BY FORMAT(CAST(s.date AS DATE), 'ddd')
ORDER BY COUNT(s.sale_id) DESC;

--4 WPŁYW ILOŚCI RANDEK NA ILOŚĆ SPRZEDANYCH PRODUKTÓW PRZEZ PRACOWNIKA
SELECT st.first_name,
    st.last_name,
    SUM(r.dates_number) dates_number,
    COUNT(sa.sale_id) sales_number
FROM staff st
    LEFT JOIN relationships r USING(staff_id)
    LEFT JOIN sales sa USING(staff_id)
WHERE sa.return_oper IS FALSE
GROUP BY st.first_name,
    st.last_name
ORDER BY COUNT(sa.sale_id) DESC;