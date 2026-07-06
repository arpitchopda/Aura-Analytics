import csv
import random
from datetime import datetime, timedelta
import os

def generate_customer_profiles(num_customers=1000):
    """Generates a list of unique customer profiles to ensure demographic consistency."""
    genders = ["Male", "Female", "Non-Binary"]
    gender_weights = [0.47, 0.49, 0.04]
    
    locations = [
        "New York", "California", "Texas", "Florida", "Illinois",
        "Washington", "Massachusetts", "Georgia", "Ohio", "Colorado"
    ]
    location_weights = [0.18, 0.22, 0.15, 0.12, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03]
    
    profiles = []
    for i in range(1, num_customers + 1):
        cust_id = f"C{10000 + i}"
        gender = random.choices(genders, weights=gender_weights)[0]
        
        # Age distribution: skew towards 25-45
        age_group = random.choices(["young", "mid", "senior"], weights=[0.25, 0.55, 0.20])[0]
        if age_group == "young":
            age = random.randint(18, 25)
        elif age_group == "mid":
            age = random.randint(26, 50)
        else:
            age = random.randint(51, 75)
            
        location = random.choices(locations, weights=location_weights)[0]
        subscription = random.choices(["Yes", "No"], weights=[0.30, 0.70])[0]
        
        profiles.append({
            "CustomerID": cust_id,
            "Gender": gender,
            "Age": age,
            "Location": location,
            "SubscriptionStatus": subscription
        })
    return profiles

def generate_transactions(customers, num_transactions=12000):
    """Generates random transactions matching real-world trends (seasonality, category preferences)."""
    # Categories and items with base prices
    inventory = {
        "Clothing": [
            ("T-Shirt", 25.0), ("Jeans", 55.0), ("Jacket", 120.0), 
            ("Sneakers", 85.0), ("Socks", 9.99), ("Hoodie", 45.0)
        ],
        "Electronics": [
            ("Smartphone", 699.0), ("Laptop", 1099.0), ("Headphones", 149.0), 
            ("Smartwatch", 199.0), ("Bluetooth Speaker", 79.0), ("Tablet", 329.0)
        ],
        "Books": [
            ("Fiction Novel", 14.99), ("Biography", 22.50), ("Sci-Fi Anthology", 17.99), 
            ("Cookbook", 29.99), ("Self-Help Book", 19.99), ("Tech Guide", 49.99)
        ],
        "Home & Kitchen": [
            ("Blender", 45.00), ("Coffee Maker", 89.99), ("Air Fryer", 119.99), 
            ("Dinnerware Set", 59.99), ("Vacuum Cleaner", 149.99), ("Toaster", 35.0)
        ],
        "Beauty & Personal Care": [
            ("Moisturizer", 28.00), ("Lipstick", 18.50), ("Perfume", 75.00), 
            ("Shampoo", 11.99), ("Hair Dryer", 45.00), ("Skincare Kit", 60.00)
        ],
        "Sports & Outdoors": [
            ("Yoga Mat", 29.99), ("Dumbbell Set", 49.99), ("Water Bottle", 19.99), 
            ("Camping Tent", 149.99), ("Running Shoes", 95.00), ("Backpack", 39.99)
        ]
    }
    
    categories = list(inventory.keys())
    payment_methods = ["Credit Card", "Debit Card", "PayPal", "Cash"]
    payment_weights = [0.55, 0.20, 0.15, 0.10]
    
    start_date = datetime(2024, 1, 1)
    
    transactions = []
    invoice_counter = 50001
    
    for _ in range(num_transactions):
        invoice_no = f"INV{invoice_counter}"
        invoice_counter += 1
        
        # Pick customer
        cust = random.choice(customers)
        cust_id = cust["CustomerID"]
        cust_age = cust["Age"]
        cust_sub = cust["SubscriptionStatus"]
        
        # Age-based category preferences
        # Young: Electronics/Clothing, Mid: Balanced, Senior: Books/Home
        if cust_age <= 25:
            cat_weights = [0.30, 0.35, 0.05, 0.05, 0.15, 0.10] # Tech/Clothing heavy
        elif cust_age >= 55:
            cat_weights = [0.10, 0.10, 0.30, 0.30, 0.10, 0.10] # Books/Home heavy
        else:
            cat_weights = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15] # Balanced
            
        category = random.choices(categories, weights=cat_weights)[0]
        item_name, base_price = random.choice(inventory[category])
        
        # Quantity distribution: usually 1 or 2, rarely up to 5
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.60, 0.25, 0.10, 0.03, 0.02])[0]
        
        # Price variation: +/- 5% random variation for price fluctuation
        unit_price = round(base_price * random.uniform(0.95, 1.05), 2)
        
        # Payment method
        payment = random.choices(payment_methods, weights=payment_weights)[0]
        
        # Invoice date with seasonality and holiday spikes
        # 730 days in 2024 & 2025
        rand_days = random.randint(0, 729)
        date_val = start_date + timedelta(days=rand_days)
        
        # November & December have 2x shopping volume
        if date_val.month in [11, 12] and random.random() < 0.3:
            # Shifted to holiday season
            pass
        elif date_val.month in [6, 7] and random.random() < 0.15:
            # Summer sale shift
            pass
        else:
            # Normal distribution shift
            if random.random() < 0.2:
                # Add extra transactions to weekend (Friday, Saturday, Sunday)
                weekday = date_val.weekday()
                if weekday not in [4, 5, 6]:
                    date_val += timedelta(days=(4 - weekday)) # Move to Friday
                    
        # Add random time
        hour = random.randint(9, 21)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        date_val = date_val.replace(hour=hour, minute=minute, second=second)
        
        # Review Rating: 1.0 to 5.0
        # Highly rated on average, subscription members tend to rate higher
        if cust_sub == "Yes":
            rating = round(random.choices([5.0, 4.0, 3.0, 2.0, 1.0], weights=[0.55, 0.30, 0.10, 0.03, 0.02])[0] - random.uniform(0, 0.5), 1)
        else:
            rating = round(random.choices([5.0, 4.0, 3.0, 2.0, 1.0], weights=[0.40, 0.35, 0.15, 0.07, 0.03])[0] - random.uniform(0, 0.5), 1)
        rating = max(1.0, min(5.0, rating))
        
        # Discount Applied: subscribers get discounts more often
        if cust_sub == "Yes":
            discount = random.choices(["Yes", "No"], weights=[0.50, 0.50])[0]
        else:
            discount = random.choices(["Yes", "No"], weights=[0.15, 0.85])[0]
            
        transactions.append({
            "InvoiceNo": invoice_no,
            "CustomerID": cust_id,
            "Gender": cust["Gender"],
            "Age": cust_age,
            "Location": cust["Location"],
            "Category": category,
            "ItemName": item_name,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "PaymentMethod": payment,
            "InvoiceDate": date_val.strftime("%Y-%m-%d %H:%M:%S"),
            "ReviewRating": rating,
            "SubscriptionStatus": cust_sub,
            "DiscountApplied": discount
        })
        
    # Sort transactions by date
    transactions.sort(key=lambda x: x["InvoiceDate"])
    return transactions

def main():
    print("Generating synthetic customer shopping dataset...")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create profiles and transactions
    customers = generate_customer_profiles(num_customers=1200)
    transactions = generate_transactions(customers, num_transactions=15000)
    
    # Output to CSV
    csv_file = "data/raw_customer_shopping.csv"
    headers = [
        "InvoiceNo", "CustomerID", "Gender", "Age", "Location", 
        "Category", "ItemName", "Quantity", "UnitPrice", "PaymentMethod", 
        "InvoiceDate", "ReviewRating", "SubscriptionStatus", "DiscountApplied"
    ]
    
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(transactions)
        
    print(f"Dataset successfully created and saved to {csv_file}")
    print(f"Generated {len(customers)} unique customers and {len(transactions)} transaction records.")

if __name__ == "__main__":
    main()
