-- Business Queries for Customer Analytics

-- 1. Which product categories are most profitable (highest total revenue)?
-- Rationale: Helps target inventory management and marketing focus.
SELECT 
    category,
    SUM(quantity) AS total_items_sold,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    ROUND(AVG(review_rating), 2) AS average_rating
FROM transactions
GROUP BY category
ORDER BY total_revenue DESC;


-- 2. What is the Customer Lifetime Value (CLV)? Or average revenue per customer?
-- Rationale: Measures customer value to calculate acquisition cost limits.
SELECT 
    c.subscription_status,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    ROUND(SUM(t.total_revenue), 2) AS total_revenue,
    ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS average_revenue_per_customer
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.subscription_status;


-- 3. What is the subscription impact on shopping behavior (average rating, AOV, discounts)?
-- Rationale: Evaluates if loyalty subscriptions lead to larger carts or higher satisfaction.
SELECT 
    c.subscription_status,
    COUNT(t.invoice_no) AS total_transactions,
    ROUND(AVG(t.quantity), 2) AS avg_items_per_order,
    ROUND(AVG(t.total_revenue), 2) AS average_order_value,
    ROUND(AVG(t.review_rating), 2) AS average_rating,
    SUM(CASE WHEN t.discount_applied = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS discount_utilization_pct
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.subscription_status;


-- 4. Which locations generate the most sales?
-- Rationale: Directs geographic expansion and regional advertising budgets.
SELECT 
    c.location,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    COUNT(t.invoice_no) AS transaction_count,
    ROUND(SUM(t.total_revenue), 2) AS total_revenue,
    ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS spend_per_customer
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.location
ORDER BY total_revenue DESC;


-- 5. What are the monthly sales trends?
-- Rationale: Highlights seasonal trends and month-over-month growth.
SELECT 
    STRFTIME('%Y-%m', invoice_date) AS month,
    COUNT(DISTINCT invoice_no) AS total_orders,
    ROUND(SUM(total_revenue), 2) AS monthly_revenue,
    ROUND(AVG(total_revenue), 2) AS average_order_value
FROM transactions
GROUP BY month
ORDER BY month ASC;


-- 6. What is the breakdown of payment methods by total transaction count and revenue?
-- Rationale: Informs payment processing fee negotiation and integration priorities.
SELECT 
    payment_method,
    COUNT(invoice_no) AS transaction_count,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    ROUND(SUM(total_revenue) * 100.0 / (SELECT SUM(total_revenue) FROM transactions), 2) AS revenue_share_pct
FROM transactions
GROUP BY payment_method
ORDER BY total_revenue DESC;


-- 7. Who are the top 10 highest-spending customers?
-- Rationale: Identifies VIP customers for high-value loyalty perks.
SELECT 
    c.customer_id,
    c.age,
    c.gender,
    c.location,
    c.subscription_status,
    COUNT(t.invoice_no) AS total_orders,
    ROUND(SUM(t.total_revenue), 2) AS lifetime_spend,
    ROUND(AVG(t.review_rating), 2) AS avg_given_rating
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id
ORDER BY lifetime_spend DESC
LIMIT 10;


-- 8. Customer demographics summary (Age Groups vs Spending)
-- Rationale: Creates age-based consumer profiles.
SELECT 
    CASE 
        WHEN age < 25 THEN 'Under 25'
        WHEN age BETWEEN 25 AND 40 THEN '25-40'
        WHEN age BETWEEN 41 AND 55 THEN '41-55'
        ELSE 'Over 55'
    END AS age_group,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    ROUND(SUM(t.total_revenue), 2) AS total_spend,
    ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS avg_spend_per_customer
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY age_group
ORDER BY total_spend DESC;
