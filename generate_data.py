import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# ----------------------------------------------------
# 1. GENERATE CUSTOMERS DIMENSION (Dim_Customers)
# ----------------------------------------------------
print("Generating Customers...")
num_customers = 800
segments = ["Consumer", "Corporate", "Home Office"]
segment_probs = [0.5, 0.3, 0.2]

# US States and Cities by Region
us_geography = [
    {"Region": "East", "State": "New York", "City": "New York City", "Postal_Code": "10001"},
    {"Region": "East", "State": "New York", "City": "Buffalo", "Postal_Code": "14201"},
    {"Region": "East", "State": "Pennsylvania", "City": "Philadelphia", "Postal_Code": "19104"},
    {"Region": "East", "State": "Massachusetts", "City": "Boston", "Postal_Code": "02108"},
    {"Region": "West", "State": "California", "City": "Los Angeles", "Postal_Code": "90001"},
    {"Region": "West", "State": "California", "City": "San Francisco", "Postal_Code": "94102"},
    {"Region": "West", "State": "Washington", "City": "Seattle", "Postal_Code": "98101"},
    {"Region": "West", "State": "Oregon", "City": "Portland", "Postal_Code": "97201"},
    {"Region": "Central", "State": "Illinois", "City": "Chicago", "Postal_Code": "60601"},
    {"Region": "Central", "State": "Texas", "City": "Houston", "Postal_Code": "77001"},
    {"Region": "Central", "State": "Texas", "City": "Dallas", "Postal_Code": "75201"},
    {"Region": "Central", "State": "Michigan", "City": "Detroit", "Postal_Code": "48201"},
    {"Region": "South", "State": "Florida", "City": "Miami", "Postal_Code": "33101"},
    {"Region": "South", "State": "Georgia", "City": "Atlanta", "Postal_Code": "30301"},
    {"Region": "South", "State": "North Carolina", "City": "Charlotte", "Postal_Code": "28201"},
    {"Region": "South", "State": "Tennessee", "City": "Nashville", "Postal_Code": "37201"}
]

# Random customer names pool
first_names = ["John", "Jane", "Robert", "Mary", "Michael", "Patricia", "William", "Linda", "David", "Elizabeth",
               "Richard", "Barbara", "Joseph", "Susan", "Thomas", "Jessica", "Charles", "Sarah", "Christopher", "Karen"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
              "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"]

customer_ids = [f"CS-{i:05d}" for i in range(1, num_customers + 1)]
customer_names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(num_customers)]
customer_segments = np.random.choice(segments, size=num_customers, p=segment_probs)

selected_geos = [np.random.choice(us_geography) for _ in range(num_customers)]
cities = [geo["City"] for geo in selected_geos]
states = [geo["State"] for geo in selected_geos]
regions = [geo["Region"] for geo in selected_geos]
postals = [geo["Postal_Code"] for geo in selected_geos]

dim_customers = pd.DataFrame({
    "Customer_ID": customer_ids,
    "Customer_Name": customer_names,
    "Segment": customer_segments,
    "City": cities,
    "State": states,
    "Country": "United States",
    "Region": regions,
    "Postal_Code": postals
})

dim_customers.to_csv("data/Dim_Customers.csv", index=False)

# ----------------------------------------------------
# 2. GENERATE PRODUCTS DIMENSION (Dim_Products)
# ----------------------------------------------------
print("Generating Products...")
categories_structure = {
    "Technology": {
        "Subcategories": ["Phones", "Accessories", "Copiers", "Machines"],
        "Base_Price_Range": (50, 1200)
    },
    "Furniture": {
        "Subcategories": ["Chairs", "Tables", "Bookcases", "Furnishings"],
        "Base_Price_Range": (30, 800)
    },
    "Office Supplies": {
        "Subcategories": ["Paper", "Binders", "Art", "Storage", "Appliances", "Fasteners", "Envelopes"],
        "Base_Price_Range": (2, 150)
    }
}

num_products = 300
product_ids = [f"PR-{i:05d}" for i in range(1, num_products + 1)]

cats = list(categories_structure.keys())
prod_cats = np.random.choice(cats, size=num_products, p=[0.25, 0.30, 0.45])

prod_subcats = []
cost_prices = []
list_prices = []
product_names = []

# Product Name generator parts
adj_words = ["Premium", "Deluxe", "Ergonomic", "Eco-Friendly", "Pro-Series", "Compact", "Heavy-Duty", "Modern", "Classic", "Wireless"]
tech_words = ["SmartPhone X", "Keyboard Duo", "LaserJet 500", "3D Scanner", "Monitor Pro", "Router Hub", "Power Pack", "Storage SSD"]
furn_words = ["Executive Chair", "Oak Desk", "Pine Bookcase", "LED Lamp", "Office Sofa", "File Cabinet", "Drafting Table"]
supp_words = ["Notebook 5-Pack", "Gel Pen Set", "Heavy Binder", "Storage Box", "Metal Clips", "Bubble Envelopes", "Air Purifier"]

for i, cat in enumerate(prod_cats):
    subcats = categories_structure[cat]["Subcategories"]
    subcat = np.random.choice(subcats)
    prod_subcats.append(subcat)
    
    # Calculate Cost and List Prices
    price_min, price_max = categories_structure[cat]["Base_Price_Range"]
    cost = np.round(np.random.uniform(price_min, price_max * 0.6), 2)
    markup = np.random.uniform(1.3, 2.0)  # 30% to 100% markup
    list_price = np.round(cost * markup, 2)
    
    cost_prices.append(cost)
    list_prices.append(list_price)
    
    # Create product names
    adj = np.random.choice(adj_words)
    if cat == "Technology":
        name = f"{adj} {np.random.choice(tech_words)} v{i+10}"
    elif cat == "Furniture":
        name = f"{adj} {np.random.choice(furn_words)} #{i+10}"
    else:
        name = f"{adj} {np.random.choice(supp_words)} - Pack of {np.random.randint(2, 20)}"
    product_names.append(name)

dim_products = pd.DataFrame({
    "Product_ID": product_ids,
    "Category": prod_cats,
    "Sub_Category": prod_subcats,
    "Product_Name": product_names,
    "Cost_Price": cost_prices,
    "List_Price": list_prices
})

dim_products.to_csv("data/Dim_Products.csv", index=False)

# ----------------------------------------------------
# 3. GENERATE ORDERS FACT (Fact_Orders)
# ----------------------------------------------------
print("Generating Orders...")
num_orders = 6000

# Setup order generation dates: 2023-01-01 to 2025-12-31
start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 31)
date_diff_days = (end_date - start_date).days

# Build a list of random dates with Q4 seasonality (November & December have higher probabilities)
order_dates = []
for _ in range(num_orders):
    rand_days = np.random.randint(0, date_diff_days)
    o_date = start_date + timedelta(days=rand_days)
    
    # Seasonality check: give a 20% chance of shifting to Q4 to boost holiday sales
    if o_date.month not in [11, 12] and np.random.rand() < 0.20:
        new_month = np.random.choice([11, 12])
        new_day = np.random.randint(1, 29)
        o_date = datetime(o_date.year, new_month, new_day)
        
    order_dates.append(o_date)

# Sort dates to look realistic
order_dates.sort()

# Pre-generate Order IDs
unique_order_ids = [f"CA-{date.year}-{100000 + i}" for i, date in enumerate(order_dates)]
order_ids = []
curr_order_idx = 0

# Random choices for ship modes and priorities
ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
ship_mode_probs = [0.60, 0.20, 0.15, 0.05]
priorities = ["Low", "Medium", "High", "Critical"]
priority_probs = [0.15, 0.50, 0.25, 0.10]

row_data = []

# Generate records
for row_id in range(1, num_orders + 1):
    # Group items into orders (approx 1.5 items per order on average)
    if row_id == 1 or np.random.rand() > 0.40:
        # New Order
        o_date = order_dates[curr_order_idx]
        o_id = unique_order_ids[curr_order_idx]
        cust_id = np.random.choice(customer_ids)
        ship_mode = np.random.choice(ship_modes, p=ship_mode_probs)
        
        # Calculate shipping delay based on Ship Mode
        if ship_mode == "Same Day":
            ship_delay = 0
        elif ship_mode == "First Class":
            ship_delay = np.random.randint(1, 3)
        elif ship_mode == "Second Class":
            ship_delay = np.random.randint(2, 5)
        else:  # Standard
            ship_delay = np.random.randint(3, 8)
            
        ship_date = o_date + timedelta(days=ship_delay)
        priority = np.random.choice(priorities, p=priority_probs)
        curr_order_idx += 1
    else:
        # Append to previous order (uses previous metadata, but new product item)
        # Note: o_date, o_id, cust_id, ship_mode, ship_date, priority remain from previous loop iteration
        pass
        
    # Select product
    prod_idx = np.random.randint(0, num_products)
    prod_row = dim_products.iloc[prod_idx]
    prod_id = prod_row["Product_ID"]
    cost_price = prod_row["Cost_Price"]
    list_price = prod_row["List_Price"]
    
    # Transactional Metrics
    quantity = int(np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], p=[0.3, 0.25, 0.18, 0.12, 0.07, 0.04, 0.02, 0.01, 0.005, 0.005]))
    
    # Discount (0%, 10%, 20%, 30%, 50%)
    discount = float(np.random.choice([0.0, 0.1, 0.2, 0.3, 0.5], p=[0.55, 0.20, 0.15, 0.07, 0.03]))
    
    # Sales = Quantity * List_Price * (1 - Discount)
    sales = np.round(quantity * list_price * (1.0 - discount), 2)
    
    # Shipping Cost
    ship_base = {"Same Day": 15.0, "First Class": 8.0, "Second Class": 5.0, "Standard Class": 2.5}
    shipping_cost = np.round(ship_base[ship_mode] + (sales * np.random.uniform(0.01, 0.03)), 2)
    
    # Total product cost
    total_prod_cost = np.round(quantity * cost_price, 2)
    
    # Profit = Sales - Total Product Cost - Shipping Cost
    profit = np.round(sales - total_prod_cost - shipping_cost, 2)
    
    row_data.append({
        "Row_ID": row_id,
        "Order_ID": o_id,
        "Order_Date": o_date.strftime("%Y-%m-%d"),
        "Ship_Date": ship_date.strftime("%Y-%m-%d"),
        "Ship_Mode": ship_mode,
        "Customer_ID": cust_id,
        "Product_ID": prod_id,
        "Sales": sales,
        "Quantity": quantity,
        "Discount": discount,
        "Profit": profit,
        "Shipping_Cost": shipping_cost,
        "Order_Priority": priority
    })

fact_orders = pd.DataFrame(row_data)

# Ensure chronological order matches Row ID
fact_orders = fact_orders.sort_values(by="Order_Date").reset_index(drop=True)
fact_orders["Row_ID"] = fact_orders.index + 1

fact_orders.to_csv("data/Fact_Orders.csv", index=False)

print("\nData generation complete!")
print(f"Dim_Customers: {dim_customers.shape[0]} records saved to 'data/Dim_Customers.csv'")
print(f"Dim_Products: {dim_products.shape[0]} records saved to 'data/Dim_Products.csv'")
print(f"Fact_Orders: {fact_orders.shape[0]} records saved to 'data/Fact_Orders.csv'")
