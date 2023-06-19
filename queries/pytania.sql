--1
SELECT MONTH(s.date) month, s.staff_id, COUNT(s.sale_id) FROM 
(SELECT MONTH(s.date) month, MAX(COUNT(s.sale_id))
GROUP BY MONTH(s.date))
GROUP BY MONTH(s.date), s.staff_id
ORDER BY MONTH(s.date) ASC, COUNT(s.sale_id) DESC

--2
SELECT g.title, GROUP_CONCAT(p.particip_id SEPARATOR ", ") FROM participations p
LEFT JOIN tournaments t USING(p.tournament_id)
LEFT JOIN games g USING(t.game_id)
WHERE p.place >= 1 AND p.place <= 10
GROUP BY g.title;

--3
SELECT g.title, COUNT(s.sale_id) cash FROM games g
LEFT JOIN inventory i USING(game_id)
LEFT JOIN sales s USING(inventory_id)
LEFT JOIN payments p USING(payment_id)
GROUP BY g.title
ORDER BY COUNT(p.payment_id) DESC;

SELECT g.title, COUNT(r.rental_id) money FROM games g
LEFT JOIN inventory i USING(game_id)
LEFT JOIN rental r USING(inventory_id)
LEFT JOIN payments p USING(payment_id)
GROUP BY gm.game_category
ORDER BY COUNT(r.rental_id) DESC
LIMIT 5;



--DODATKOWE

--1
SELECT gm.game_category, COUNT(r.rental_id)+COUNT(p.payment_id) popularity FROM game_categories gm
LEFT JOIN games g USING(category_id)
LEFT JOIN inventory i USING(game_id)
LEFT JOIN rental r USING(inventory_id)
LEFT JOIN payments p USING(payment_id)
GROUP BY gm.game_category
ORDER BY COUNT(r.rental_id)+COUNT(p.payment_id) DESC
LIMIT 5;
--2
SELECT MONTH(s.date) month, YEAR(s.date) year, MAX(amount) highest,
MIN(amount) lowest FROM 
(Select MONTH(s.date), YEAR(s.date), SUM(amount),
FROM payments p
LEFT JOIN sales s USING(payment_id)
GROUP BY MONTH(s.date), YEAR(s.date)
ORDER BY SUM(amount) ASC);
--3
SELECT DATENAME(WEEKDAY, t.start_time) name_of_day, 
COUNT(DATENAME(WEEKDAY, t.start_time)) amount FROM tournaments t
GROUP BY DATENAME(WEEKDAY, t.start_time)
ORDER BY COUNT(DATENAME(WEEKDAY, t.start_time)) DESC
LIMIT 1;
--4 WPŁYW ILOŚCI RANDEK NA ILOŚĆ SPRZEDANYCH PRODUKTÓW PRZEZ PRACOWNIKA
SELECT s.first_name, s.last_name, r.dates_number, count(s.sale_id) FROM staff s
LEFT JOIN relationships r USING(staff_id)
LEFT JOIN sales s USING(staff_id)
GROUP BY s.first_name, s.last_name
ORDER BY count(s.sale_id) DESC;

