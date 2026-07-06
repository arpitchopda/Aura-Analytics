import sqlite3
import json
import os

def dict_factory(cursor, row):
    """Convert SQLite row results to a dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def run_analytics_queries():
    db_path = "data/customer_analytics.db"
    json_output_path = "web/dashboard_data.json"
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Please run clean_and_load.py first.")
        
    print("Running business queries and extracting analytical insights...")
    
    conn = sqlite3.connect(db_path)
    # Use regular connection for printable output, then dict_factory for JSON
    cursor = conn.cursor()
    
    dashboard_data = {}
    
    # 1. KPI Summary Cards
    cursor.execute("""
        SELECT 
            (SELECT ROUND(SUM(total_revenue), 2) FROM transactions) AS total_revenue,
            (SELECT COUNT(DISTINCT customer_id) FROM customers) AS total_customers,
            (SELECT ROUND(AVG(total_revenue), 2) FROM (SELECT SUM(total_revenue) AS total_revenue FROM transactions GROUP BY invoice_no)) AS avg_order_value,
            (SELECT ROUND(AVG(review_rating), 1) FROM transactions) AS avg_rating,
            (SELECT COUNT(DISTINCT invoice_no) FROM transactions) AS total_orders
    """)
    kpis = cursor.fetchone()
    dashboard_data["kpis"] = {
        "total_revenue": kpis[0],
        "total_customers": kpis[1],
        "avg_order_value": kpis[2],
        "avg_rating": kpis[3],
        "total_orders": kpis[4]
    }
    
    print("\n================== KEY PERFORMANCE INDICATORS (KPIs) ==================")
    print(f"Total Revenue:         ${kpis[0]:,.2f}")
    print(f"Total Customers:       {kpis[1]:,}")
    print(f"Total Orders:          {kpis[4]:,}")
    print(f"Average Order Value:   ${kpis[2]:.2f}")
    print(f"Average Review Rating: {kpis[3]}/5.0")
    print("=======================================================================")

    # Switch connection to dict-based rows for easy JSON generation
    conn.row_factory = dict_factory
    dict_conn = sqlite3.connect(db_path)
    dict_conn.row_factory = dict_factory
    dict_cursor = dict_conn.cursor()
    
    # 2. Profitable Categories
    print("\n--- Sales Performance by Product Category ---")
    dict_cursor.execute("""
        SELECT 
            category,
            SUM(quantity) AS total_items_sold,
            ROUND(SUM(total_revenue), 2) AS total_revenue,
            ROUND(AVG(review_rating), 2) AS average_rating
        FROM transactions
        GROUP BY category
        ORDER BY total_revenue DESC;
    """)
    categories = dict_cursor.fetchall()
    dashboard_data["categories"] = categories
    for cat in categories:
        print(f"Category: {cat['category']:<25} | Revenue: ${cat['total_revenue']:<10,.2f} | Sold: {cat['total_items_sold']:<5} | Rating: {cat['average_rating']}/5")
        
    # 3. Customer Lifetime Value by Subscription
    print("\n--- Customer Revenue by Subscription Status ---")
    dict_cursor.execute("""
        SELECT 
            c.subscription_status,
            COUNT(DISTINCT c.customer_id) AS total_customers,
            ROUND(SUM(t.total_revenue), 2) AS total_revenue,
            ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS average_revenue_per_customer
        FROM customers c
        LEFT JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.subscription_status;
    """)
    subscription_clv = dict_cursor.fetchall()
    dashboard_data["subscription_clv"] = subscription_clv
    for sub in subscription_clv:
        print(f"Subscriber: {sub['subscription_status']:<3} | Count: {sub['total_customers']:<5} | Revenue: ${sub['total_revenue']:<12,.2f} | Spend/Cust: ${sub['average_revenue_per_customer']:,.2f}")
        
    # 4. Shopping Behavior by Subscription
    dict_cursor.execute("""
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
    """)
    dashboard_data["subscription_behavior"] = dict_cursor.fetchall()

    # 5. Location Sales Performance (Top 5)
    print("\n--- Top Locations by Sales Revenue ---")
    dict_cursor.execute("""
        SELECT 
            c.location,
            COUNT(DISTINCT c.customer_id) AS customer_count,
            ROUND(SUM(t.total_revenue), 2) AS total_revenue,
            ROUND(SUM(t.total_revenue) / COUNT(DISTINCT c.customer_id), 2) AS spend_per_customer
        FROM customers c
        JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.location
        ORDER BY total_revenue DESC;
    """)
    locations = dict_cursor.fetchall()
    dashboard_data["locations"] = locations
    for loc in locations[:5]:
         print(f"Location: {loc['location']:<15} | Customers: {loc['customer_count']:<4} | Revenue: ${loc['total_revenue']:<10,.2f} | Spend/Cust: ${loc['spend_per_customer']:,.2f}")

    # 6. Monthly Sales Trends
    dict_cursor.execute("""
        SELECT 
            STRFTIME('%Y-%m', invoice_date) AS month,
            COUNT(DISTINCT invoice_no) AS total_orders,
            ROUND(SUM(total_revenue), 2) AS monthly_revenue,
            ROUND(AVG(total_revenue), 2) AS average_order_value
        FROM transactions
        GROUP BY month
        ORDER BY month ASC;
    """)
    dashboard_data["monthly_trends"] = dict_cursor.fetchall()

    # 7. Payment Methods Breakdown
    dict_cursor.execute("""
        SELECT 
            payment_method,
            COUNT(invoice_no) AS transaction_count,
            ROUND(SUM(total_revenue), 2) AS total_revenue,
            ROUND(SUM(total_revenue) * 100.0 / (SELECT SUM(total_revenue) FROM transactions), 2) AS revenue_share_pct
        FROM transactions
        GROUP BY payment_method
        ORDER BY total_revenue DESC;
    """)
    dashboard_data["payment_methods"] = dict_cursor.fetchall()

    # 8. Top 10 VIP Customers
    dict_cursor.execute("""
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
    """)
    dashboard_data["vip_customers"] = dict_cursor.fetchall()

    # 9. Demographics Summary
    dict_cursor.execute("""
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
    """)
    dashboard_data["demographics"] = dict_cursor.fetchall()

    # Write dashboard JSON
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=4)
        
    print(f"\nSuccessfully compiled dashboard analytical JSON: {json_output_path}")
    
    dict_conn.close()
    conn.close()

if __name__ == "__main__":
    run_analytics_queries()
