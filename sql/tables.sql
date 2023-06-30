CREATE TABLE city (
  city_id INT NOT NULL AUTO_INCREMENT,
  city VARCHAR(40) NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (city_id)
);
CREATE TABLE customers (
  customer_id INT NOT NULL AUTO_INCREMENT,
  first_name VARCHAR(30) NOT NULL,
  last_name VARCHAR(40) NOT NULL,
  phone VARCHAR(10) NOT NULL,
  email VARCHAR(80) NOT NULL,
  city_id INT NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (customer_id)
);
CREATE TABLE game_categories (
  category_id INT NOT NULL AUTO_INCREMENT,
  game_category VARCHAR(40) NOT NULL UNIQUE,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (category_id)
);
CREATE TABLE game_prices (
  price_id INT NOT NULL AUTO_INCREMENT,
  current_price DECIMAL(5, 2) NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (price_id)
);
CREATE TABLE game_types (
  type_id INT NOT NULL AUTO_INCREMENT,
  game_type VARCHAR(40) NOT NULL UNIQUE,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (type_id)
);
CREATE TABLE games (
  game_id INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL UNIQUE,
  description TEXT NULL,
  category_id INT NOT NULL,
  type_id INT NOT NULL,
  competitivity BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (game_id)
);
CREATE TABLE inventory (
  inventory_id INT NOT NULL AUTO_INCREMENT,
  game_id INT NOT NULL,
  destination CHAR(1) NOT NULL COMMENT 'T, S or R',
  price_id INT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  purchase_payment_id INT NOT NULL,
  delivery_date TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (inventory_id)
);
CREATE TABLE maintenance_expenses (
  spend_id INT NOT NULL AUTO_INCREMENT,
  title_id INT NOT NULL,
  payment_id INT NOT NULL UNIQUE,
  date TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (spend_id)
);
CREATE TABLE expense_titles (
  title_id INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL UNIQUE,
  expenses_type_id INT NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (title_id)
);
CREATE TABLE expense_types (
  expenses_type_id INT NOT NULL AUTO_INCREMENT,
  expenses_type VARCHAR(40) NOT NULL UNIQUE,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (expenses_type_id)
);
CREATE TABLE participations (
  particip_id INT NOT NULL AUTO_INCREMENT,
  tournament_id INT NOT NULL,
  customer_id INT NOT NULL,
  place INT NOT NULL,
  sign_up_date TIMESTAMP NOT NULL,
  fee_payment_id INT NOT NULL UNIQUE,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (particip_id),
  CONSTRAINT UC_participation UNIQUE (tournament_id, customer_id)
);
CREATE TABLE partners (
  partner_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(30) NULL,
  gender CHAR(1) NULL COMMENT 'M or F',
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (partner_id)
);
CREATE TABLE payments (
  payment_id INT NOT NULL AUTO_INCREMENT,
  amount DECIMAL(7, 2) NOT NULL,
  invoice_id INT NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (payment_id)
);
CREATE TABLE invoices (
  invoice_id INT NOT NULL AUTO_INCREMENT,
  date TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (invoice_id)
);
CREATE TABLE relationships (
  relationship_id INT NOT NULL AUTO_INCREMENT,
  staff_id INT NOT NULL,
  partner_id INT NOT NULL,
  dates_number INT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (relationship_id)
);
CREATE TABLE rental (
  rental_id INT NOT NULL AUTO_INCREMENT,
  inventory_id INT NOT NULL,
  customer_id INT NOT NULL,
  rental_date TIMESTAMP NOT NULL,
  return_date TIMESTAMP NULL,
  staff_id INT NOT NULL,
  payment_id INT NOT NULL UNIQUE,
  penalty_payment_id INT NULL,
  rate INT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (rental_id),
  CONSTRAINT UC_rental UNIQUE (inventory_id, rental_date)
);
CREATE TABLE sales (
  sale_id INT NOT NULL AUTO_INCREMENT,
  inventory_id INT NOT NULL,
  staff_id INT NOT NULL,
  payment_id INT NOT NULL UNIQUE,
  date TIMESTAMP NOT NULL,
  return_oper BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (sale_id)
);
CREATE TABLE staff (
  staff_id INT NOT NULL AUTO_INCREMENT,
  first_name VARCHAR(30) NOT NULL,
  last_name VARCHAR(40) NOT NULL,
  phone VARCHAR(10) NOT NULL,
  email VARCHAR(80) NOT NULL,
  city_id INT NOT NULL,
  current_salary DECIMAL(6, 2) NULL DEFAULT 3490.00,
  is_manager BOOLEAN NOT NULL DEFAULT FALSE,
  gender CHAR(1) NULL COMMENT 'M or F',
  from_date DATE NOT NULL,
  to_date DATE NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (staff_id)
);
CREATE TABLE tournaments (
  tournament_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(60) NOT NULL,
  game_id INT NOT NULL,
  start_time TIME NOT NULL,
  matches INT NOT NULL,
  fee DECIMAL(4, 2) NOT NULL,
  sign_up_deadline DATE NOT NULL,
  staff_id INT NOT NULL,
  expenses_payments_id INT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (tournament_id)
);
ALTER TABLE games
ADD CONSTRAINT FK_game_categories_TO_games FOREIGN KEY (category_id) REFERENCES game_categories (category_id);
ALTER TABLE staff
ADD CONSTRAINT FK_city_TO_staff FOREIGN KEY (city_id) REFERENCES city (city_id);
ALTER TABLE customers
ADD CONSTRAINT FK_city_TO_customers FOREIGN KEY (city_id) REFERENCES city (city_id);
ALTER TABLE participations
ADD CONSTRAINT FK_customers_TO_participations FOREIGN KEY (customer_id) REFERENCES customers (customer_id);
ALTER TABLE tournaments
ADD CONSTRAINT FK_games_TO_tournaments FOREIGN KEY (game_id) REFERENCES games (game_id);
ALTER TABLE participations
ADD CONSTRAINT FK_tournaments_TO_participations FOREIGN KEY (tournament_id) REFERENCES tournaments (tournament_id);
ALTER TABLE inventory
ADD CONSTRAINT FK_games_TO_inventory FOREIGN KEY (game_id) REFERENCES games (game_id);
ALTER TABLE games
ADD CONSTRAINT FK_game_types_TO_games FOREIGN KEY (type_id) REFERENCES game_types (type_id);
ALTER TABLE rental
ADD CONSTRAINT FK_inventory_TO_rental FOREIGN KEY (inventory_id) REFERENCES inventory (inventory_id);
ALTER TABLE rental
ADD CONSTRAINT FK_customers_TO_rental FOREIGN KEY (customer_id) REFERENCES customers (customer_id);
ALTER TABLE sales
ADD CONSTRAINT FK_inventory_TO_sales FOREIGN KEY (inventory_id) REFERENCES inventory (inventory_id);
ALTER TABLE inventory
ADD CONSTRAINT FK_game_prices_TO_inventory FOREIGN KEY (price_id) REFERENCES game_prices (price_id);
ALTER TABLE relationships
ADD CONSTRAINT FK_staff_TO_relationships FOREIGN KEY (staff_id) REFERENCES staff (staff_id);
ALTER TABLE relationships
ADD CONSTRAINT FK_partners_TO_relationships FOREIGN KEY (partner_id) REFERENCES partners (partner_id);
ALTER TABLE rental
ADD CONSTRAINT FK_staff_TO_rental FOREIGN KEY (staff_id) REFERENCES staff (staff_id);
ALTER TABLE sales
ADD CONSTRAINT FK_staff_TO_sales FOREIGN KEY (staff_id) REFERENCES staff (staff_id);
ALTER TABLE tournaments
ADD CONSTRAINT FK_staff_TO_tournaments FOREIGN KEY (staff_id) REFERENCES staff (staff_id);
ALTER TABLE inventory
ADD CONSTRAINT FK_payments_TO_inventory FOREIGN KEY (purchase_payment_id) REFERENCES payments (payment_id);
ALTER TABLE tournaments
ADD CONSTRAINT FK_payments_TO_tournaments FOREIGN KEY (expenses_payments_id) REFERENCES payments (payment_id);
ALTER TABLE sales
ADD CONSTRAINT FK_payments_TO_sales FOREIGN KEY (payment_id) REFERENCES payments (payment_id);
ALTER TABLE rental
ADD CONSTRAINT FK_payments_TO_rental FOREIGN KEY (payment_id) REFERENCES payments (payment_id);
ALTER TABLE participations
ADD CONSTRAINT FK_payments_TO_participations FOREIGN KEY (fee_payment_id) REFERENCES payments (payment_id);
ALTER TABLE maintenance_expenses
ADD CONSTRAINT FK_payments_TO_maintenance_expenses FOREIGN KEY (payment_id) REFERENCES payments (payment_id);
ALTER TABLE rental
ADD CONSTRAINT FK_payments_TO_rental1 FOREIGN KEY (penalty_payment_id) REFERENCES payments (payment_id);
ALTER TABLE payments
ADD CONSTRAINT FK_invoices_TO_payments FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id);
ALTER TABLE maintenance_expenses
ADD CONSTRAINT FK_expense_titles_TO_maintenance_expenses FOREIGN KEY (title_id) REFERENCES expense_titles (title_id);
ALTER TABLE expense_titles
ADD CONSTRAINT FK_expense_types_TO_expense_titles FOREIGN KEY (expenses_type_id) REFERENCES expense_types (expenses_type_id);