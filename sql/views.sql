-- q 1.b
CREATE VIEW employees_ranking AS
SELECT YEAR(sa.date) year,
    MONTH(sa.date) month,
    st.first_name,
    st.last_name,
    COUNT(sa.sale_id) number_of_sales,
    ROW_NUMBER() OVER (
        PARTITION BY YEAR(sa.date),
        MONTH(sa.date)
        ORDER BY COUNT(DISTINCT sa.sale_id) DESC
    ) AS rank
FROM sales sa
    LEFT JOIN staff st USING(staff_id)
WHERE sa.return_oper IS FALSE
    AND (
        (st.to_date IS NULL)
        OR (
            st.to_date >= MAKEDATE(YEAR(sa.date), MONTH(sa.date) + 1)
        )
    )
GROUP BY YEAR(sa.date),
    MONTH(sa.date),
    st.first_name,
    st.last_name
ORDER BY YEAR(sa.date) DESC,
    MONTH(sa.date) DESC,
    ROW_NUMBER() OVER (
        PARTITION BY YEAR(sa.date),
        MONTH(sa.date)
        ORDER BY COUNT(DISTINCT sa.sale_id) DESC
    ) DESC;
-- q 1.b
CREATE VIEW best_employees AS
SELECT year,
    month,
    CONCAT_WS(" ", first_name, last_name) employee,
    number_of_sales
FROM employees_ranking
WHERE rank = 1
ORDER BY year DESC,
    month DESC;
-- q 2
CREATE VIEW top_players AS
SELECT game,
    player,
    avg_score
FROM (
        SELECT g.title game,
            CONCAT_WS(" ", c.first_name, c.last_name) player,
            ROW_NUMBER() OVER (
                PARTITION BY g.title,
                c.customer_id
                ORDER BY AVG(p.score) DESC
            ) AS group_rank,
            AVG(p.score) OVER (
                PARTITION BY g.title,
                c.customer_id
            ) AS avg_score
        FROM customers c
            RIGHT JOIN (
                SELECT customer_id,
                    tournament_id,
                    (
                        MAX(place) OVER (PARTITION BY tournament_id) - place
                    ) / MAX(place) OVER (PARTITION BY tournament_id) AS score
                FROM participations
            ) p USING(customer_id)
            RIGHT JOIN tournaments t USING(tournament_id)
            LEFT JOIN games g USING(game_id)
        HAVING g.title IS NOT NULL
            AND player IS NOT NULL
    ) tp
WHERE group_rank <= 10
ORDER BY game,
    group_rank;
-- q 3.a
CREATE VIEW top_saled_games AS
SELECT g.title game,
    SUM(p.amount) total_amount
FROM games g
    RIGHT JOIN inventory i USING(game_id)
    RIGHT JOIN sales s USING(inventory_id)
    LEFT JOIN payments p USING(payment_id)
GROUP BY g.title
ORDER BY SUM(p.amount) DESC
LIMIT 5;
-- q 3.b
CREATE VIEW top_rented_games AS
SELECT g.title game,
    SUM(p.amount) total_amount
FROM games g
    RIGHT JOIN inventory i USING(game_id)
    RIGHT JOIN rental s USING(inventory_id)
    LEFT JOIN payments p USING(payment_id)
GROUP BY g.title
ORDER BY SUM(p.amount) DESC
LIMIT 5;
-- q 4.1
CREATE VIEW game_category_ranking AS
SELECT gm.game_category,
    COUNT(DISTINCT r.rental_id) + COUNT(DISTINCT s.sale_id) popularity
FROM game_categories gm
    RIGHT JOIN games g USING(category_id)
    RIGHT JOIN inventory i USING(game_id)
    LEFT JOIN rental r USING(inventory_id)
    LEFT JOIN sales s USING(inventory_id)
WHERE s.return_oper IS FALSE
GROUP BY gm.game_category
ORDER BY COUNT(DISTINCT r.rental_id) + COUNT(DISTINCT s.sale_id) DESC;
-- q 4.2
CREATE VIEW bw_profit_months AS (
    SELECT (
            SELECT "maximal"
        ) record_type,
        YEAR(i.date) year,
        MONTH(i.date) month,
        SUM(p.amount) amount
    FROM invoices i
        LEFT JOIN payments p USING(invoice_id)
    WHERE p.amount > 0
    GROUP BY YEAR(i.date),
        MONTH(i.date)
    ORDER BY SUM(p.amount) DESC
    LIMIT 1
)
UNION ALL
(
    SELECT (
            SELECT "minimal"
        ) record_type,
        YEAR(i.date) year,
        MONTH(i.date) month,
        SUM(p.amount) amount
    FROM invoices i
        LEFT JOIN payments p USING(invoice_id)
    WHERE p.amount > 0
    GROUP BY YEAR(i.date),
        MONTH(i.date)
    ORDER BY SUM(p.amount) ASC
    LIMIT 1
);
-- q 4.3
CREATE VIEW weekly_trafic AS
SELECT DAYNAME(s.date) name_of_day,
    COUNT(s.sale_id) number_of_sales
FROM sales s
WHERE s.return_oper IS FALSE
GROUP BY DAYNAME(s.date)
ORDER BY WEEKDAY(s.sale_id) ASC;
-- q 4.4
CREATE VIEW sales_n_dates AS
SELECT rr.employee,
    rr.dates_number,
    COUNT(DISTINCT sa.sale_id) sales_number
FROM (
        SELECT st.staff_id,
            CONCAT_WS(" ", st.first_name, st.last_name) employee,
            SUM(r.dates_number) dates_number --
        FROM staff st
            LEFT JOIN relationships r USING(staff_id)
        GROUP BY CONCAT_WS(" ", st.first_name, st.last_name)
    ) rr
    LEFT JOIN sales sa USING(staff_id)
WHERE sa.return_oper IS FALSE
GROUP BY rr.staff_id
ORDER BY COUNT(DISTINCT sa.sale_id) DESC;
-- additional
-- all the payments with their dates
CREATE VIEW all_payments AS
SELECT i.date,
    p.amount
FROM invoices i
    LEFT JOIN payments p USING (invoice_id);
-- all the payments with their dates
CREATE VIEW monthly_balance AS
SELECT YEAR(p.date) year,
    MONTH(p.date) month,
    SUM(p.amount) balance
FROM all_payments p
GROUP BY YEAR(p.date),
    MONTH(p.date)
ORDER BY SUM(p.amount) DESC;