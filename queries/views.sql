-- q 1
CREATE VIEW best_employees AS
SELECT NULL;
-- q 2
CREATE VIEW top_players AS
SELECT NULL;
-- q 3.a
CREATE VIEW top_saled_games AS
SELECT NULL;
-- q 3.b
CREATE VIEW top_rented_games AS
SELECT NULL;
-- q 4.1
CREATE VIEW top_game_categories AS
SELECT NULL;
-- q 4.2.a
CREATE VIEW monthly_profits AS
SELECT NULL;
-- q 4.2.b
CREATE VIEW bw_profit_months_yearly AS
SELECT NULL;
-- q 4.3.a
CREATE VIEW weekly_trafic AS
SELECT NULL;
-- q 4.3.b
CREATE VIEW top_traffic_wday AS
SELECT NULL;
-- q 4.4
CREATE VIEW sales_n_dates AS
SELECT NULL;
-- additional
-- all the payments with their dates
CREATE VIEW all_payments AS
SELECT p.amount,
    i.date
FROM payments p
    LEFT JOIN invoices i USING (invoice_id);