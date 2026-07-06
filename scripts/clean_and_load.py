import os
import pandas as pd
import sqlite3

def clean_and_load_data():
    raw_csv_path = "data/raw_customer_shopping.csv"
    cleaned_csv_path = "data/cleaned_customer_shopping.csv"
    db_path = "data/customer_analytics.db"
    schema_path = "sql/schema.sql"
    
    print("Starting Data Cleaning & Loading Pipeline...")
    
    # 1. Read Raw CSV
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_csv_path}. Please run generate_data.py first.")
        
    df = pd.read_csv(raw_csv_path)
    print(f"Loaded raw dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
    
    # 2. Data Cleaning
    # Check for duplicates
    duplicates_count = df.duplicated().sum()
    if duplicates_count > 0:
        print(f"Removing {duplicates_count} duplicate rows...")
        df = df.drop_duplicates()
        
    # Check for missing values
    missing_values = df.isnull().sum()
    print("Missing values per column before cleaning:")
    print(missing_values)
    
    # Clean strings: Strip whitespace, normalize casing
    string_cols = ["InvoiceNo", "CustomerID", "Gender", "Location", "Category", "ItemName", "PaymentMethod", "SubscriptionStatus", "DiscountApplied"]
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # Compute TotalRevenue field
    df["TotalRevenue"] = df["Quantity"] * df["UnitPrice"]
    # Round TotalRevenue to 2 decimal places
    df["TotalRevenue"] = df["TotalRevenue"].round(2)
    
    # Export cleaned CSV
    df.to_csv(cleaned_csv_path, index=False)
    print(f"Cleaned dataset saved to {cleaned_csv_path}")
    
    # 3. Database Normalization & Insertion
    print("Normalizing tables for relational schema...")
    
    # Extract Customers (Unique profiles)
    customers_df = df[["CustomerID", "Gender", "Age", "Location", "SubscriptionStatus"]].drop_duplicates(subset=["CustomerID"])
    print(f"Extracted {customers_df.shape[0]} unique customer profiles.")
    
    # Extract Transactions (Fact table columns)
    transactions_df = df[[
        "InvoiceNo", "CustomerID", "Category", "ItemName", "Quantity", 
        "UnitPrice", "TotalRevenue", "PaymentMethod", "InvoiceDate", "ReviewRating", "DiscountApplied"
    ]]
    
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Initialize schema
    print(f"Executing database schema from {schema_path}...")
    with open(schema_path, "r") as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)
        
    # Load Customers into DB
    # Mapping pandas columns to sqlite columns
    customers_df.columns = ["customer_id", "gender", "age", "location", "subscription_status"]
    customers_df.to_sql("customers", conn, if_exists="append", index=False)
    print("Loaded 'customers' table.")
    
    # Load Transactions into DB
    transactions_df.columns = [
        "invoice_no", "customer_id", "category", "item_name", "quantity", 
        "unit_price", "total_revenue", "payment_method", "invoice_date", "review_rating", "discount_applied"
    ]
    transactions_df.to_sql("transactions", conn, if_exists="append", index=False)
    print("Loaded 'transactions' table.")
    
    # Commit changes and close
    conn.commit()
    
    # Quick integrity check
    cursor.execute("SELECT COUNT(*) FROM customers;")
    db_customers_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM transactions;")
    db_transactions_count = cursor.fetchone()[0]
    
    print("\nDatabase Integrity Verification:")
    print(f"- Customers in Database: {db_customers_count}")
    print(f"- Transactions in Database: {db_transactions_count}")
    
    conn.close()
    print("Data loading completed successfully!")

if __name__ == "__main__":
    clean_and_load_data()
