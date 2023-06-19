--1
SELECT gm.game_category, count(r.rental_id)+count(p.payment_id) popularity FROM game_categories gm
LEFT JOIN games g USING(category_id)
LEFT JOIN inventory i USING(game_id)
LEFT JOIN rental r USING(inventory_id)
LEFT JOIN payments p USING(rental_id)
GROUP BY gm.game_category
ORDER BY count(r.rental_id)+count(p.payment_id) DESC
LIMIT 5;
--2
SELECT month(s.date), year(s.date), MAX(amount),
MIN(amount)  FROM 
(Select month(s.date), year(s.date), SUM(amount),
FROM payments p
LEFT JOIN sales s USING(payment_id)
GROUP BY month(s.date), year(s.date)
ORDER BY SUM(amount) ASC);

