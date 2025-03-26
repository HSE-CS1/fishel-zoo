--  this file will create a new table to keep track of ticket orders

.open fishelzoo.db
.mode box

DROP TABLE IF EXISTS tickets;

CREATE TABLE IF NOT EXISTS tickets(
    order_number INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    contact TEXT,
    visit_date DATE,
    num_tickets INTEGER,
    confirmation TEXT NOT NULL UNIQUE,
    CHECK (num_tickets > 0)
);


-- add one row of test data
INSERT INTO tickets
    (name, contact, visit_date, num_tickets, confirmation)
    VALUES
    ("Fishel", "317-555-1234", "2025-03-20", 8, "9999");
