import sqlite3
import random
import datetime

# Helper: random date generator

def random_date(start_year=2023, end_year=2025):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)

    delta = end - start
    random_days = random.randint(0, delta.days)

    return (start + datetime.timedelta(days=random_days)).isoformat()

# Connect

conn = sqlite3.connect("sales.db")
cur = conn.cursor()

# Drop and recreate tables

cur.executescript("""
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    date TEXT,
    product_id INTEGER,
    customer_id INTEGER,
    quantity INTEGER,
    price REAL
);
""")


# Product Data (10 products)
products = [
    (1, "Laptop Pro 14", "Electronics"),
    (2, "Laptop Air 13", "Electronics"),
    (3, "Wireless Mouse", "Accessories"),
    (4, "Mechanical Keyboard", "Accessories"),
    (5, "Smartphone X", "Mobiles"),
    (6, "Smartphone Lite", "Mobiles"),
    (7, "Washing Machine 7kg", "Home Appliances"),
    (8, "Refrigerator 300L", "Home Appliances"),
    (9, "LED TV 43 inch", "Electronics"),
    (10, "Air Conditioner 1.5T", "Home Appliances")
]

cur.executemany("INSERT INTO products VALUES (?, ?, ?)", products)


# Customer Data (15 customers, 5 major Indian cities)

customer_names = [
    "Asha Sharma", "Ravi Kumar", "Priya Mehta", "Rahul Singh", "Neha Patel",
    "Arjun Verma", "Simran Gupta", "Vivek Yadav", "Aditya Kapoor",
    "Kiran Reddy", "Zoya Khan", "Imran Shaikh", "Meera Joshi",
    "Ramesh Das", "Suhani Goyal"
]

cities = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai"]

customers = []
for cid in range(1, 16):
    customers.append((cid, customer_names[cid - 1], random.choice(cities)))

cur.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers)

# Generate 120+ sales records

sales = []

for sid in range(1, 151):   # 150 rows
    date = random_date()
    product_id = random.randint(1, 10)
    customer_id = random.randint(1, 15)
    quantity = random.randint(1, 10)

    # realistic prices per product
    price_map = {
        1: 90000,  # Laptop Pro
        2: 70000,  # Laptop Air
        3: 1200,   # Mouse
        4: 3500,   # Keyboard
        5: 65000,  # Smartphone X
        6: 35000,  # Smartphone Lite
        7: 18000,  # Washing Machine
        8: 24000,  # Refrigerator
        9: 34000,  # LED TV
        10: 42000  # Air Conditioner
    }

    price = price_map[product_id] + random.randint(-2000, 2000)

    sales.append((sid, date, product_id, customer_id, quantity, price))

cur.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?)", sales)

conn.commit()
conn.close()

print("✅ sales.db generated successfully with 150 realistic sales records!")
