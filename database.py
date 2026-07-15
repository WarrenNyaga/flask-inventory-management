# server/database.py

# Simulated database storing product dictionaries
INVENTORY_DATABASE = [
    {
        "id": 1,
        "product_name": "Almond Milk",
        "brands": "Silk",
        "ingredients": "Filtered water, almonds, cane sugar",
        "price": 3.99,
        "stock": 45
    }
]

# Helper function to generate a auto-incrementing ID for new items
def get_next_id():
    if not INVENTORY_DATABASE:
        return 1
    return max(item["id"] for item in INVENTORY_DATABASE) + 1