-- Schema definition for Customer Analytics Relational Database

-- Drop tables if they exist to allow clean rebuilds
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS customers;

-- 1. Customers Table (Dimensions)
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female', 'Non-Binary')),
    age INTEGER NOT NULL CHECK(age >= 0),
    location TEXT NOT NULL,
    subscription_status TEXT NOT NULL CHECK(subscription_status IN ('Yes', 'No'))
);

-- 2. Transactions Table (Facts)
CREATE TABLE transactions (
    invoice_no TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    category TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    total_revenue REAL NOT NULL CHECK(total_revenue >= 0),
    payment_method TEXT NOT NULL CHECK(payment_method IN ('Credit Card', 'Debit Card', 'PayPal', 'Cash')),
    invoice_date TEXT NOT NULL, -- Stored as ISO8601 string: YYYY-MM-DD HH:MM:SS
    review_rating REAL CHECK(review_rating BETWEEN 1.0 AND 5.0),
    discount_applied TEXT NOT NULL CHECK(discount_applied IN ('Yes', 'No')),
    PRIMARY KEY (invoice_no, item_name),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create indexes for performance on frequent query filters
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_date ON transactions(invoice_date);
