import sys
import requests

BASE_URL = "http://127.0.0.1:5000/inventory"

def display_menu():
    print("\n" + "="*45)
    print("      INVENTORY MANAGEMENT CLI SYSTEM      ")
    print("="*45)
    print("1. View All Inventory Items")
    print("2. Find Item by ID")
    print("3. Add New Item (Manual or with Barcode)")
    print("4. Update Stock Levels or Price")
    print("5. Delete Product")
    print("6. Exit")
    print("="*45)

def get_all_items():
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            items = response.json()
            if not items:
                print("\n[!] The inventory is currently empty.")
                return
            print("\nID    | Product Name             | Brand        | Qty  | Price")
            print("-" * 65)
            for item in items:
                print(f"{item['id']:<5} | {item['product_name'][:24]:<24} | {item['brand'][:12]:<12} | {item['quantity']:<4} | ${item['price']:.2f}")
        else:
            print(f"Error fetching data: {response.json().get('error', 'Unknown Error')}")
    except requests.exceptions.ConnectionError:
        print("\n[Error] Cannot connect to API. Is Flask running?")

def find_item_by_id():
    item_id = input("\nEnter Item ID to look up: ").strip()
    if not item_id:
        return
    try:
        response = requests.get(f"{BASE_URL}/{item_id}")
        if response.status_code == 200:
            item = response.json()
            print("\n--- Product Details ---")
            print(f"ID: {item['id']}")
            print(f"Name: {item['product_name']}")
            print(f"Brand: {item['brand']}")
            print(f"Ingredients: {item['ingredients_text']}")
            print(f"Quantity: {item['quantity']}")
            print(f"Price: ${item['price']:.2f}")
        else:
            print(f"\n[!] Error: {response.json().get('error', 'Item not found')}")
    except requests.exceptions.ConnectionError:
        print("\n[Error] Connection Refused.")

def add_item():
    print("\n--- Add New Product ---")
    item_id = input("Enter custom Unique ID (required): ").strip()
    if not item_id:
        print("Error: ID is required.")
        return
    
    barcode = input("Enter Barcode to auto-fetch OpenFoodFacts data (leave blank to skip): ").strip()
    
    # Pre-populate defaults if no barcode or barcode fails
    name = brand = ingredients = ""
    if not barcode:
        name = input("Enter Product Name: ").strip()
        brand = input("Enter Brand: ").strip()
        ingredients = input("Enter Ingredients: ").strip()

    qty_input = input("Enter Stock Quantity (default 0): ").strip() or "0"
    price_input = input("Enter Price (default 0.00): ").strip() or "0.00"
    
    try:
        payload = {
            "id": item_id,
            "product_name": name,
            "brand": brand,
            "ingredients_text": ingredients,
            "quantity": int(qty_input),
            "price": float(price_input)
        }
        if barcode:
            payload["barcode"] = barcode

        response = requests.post(BASE_URL, json=payload)
        if response.status_code == 201:
            res_data = response.json()
            print(f"\n[Success] Added: {res_data['product_name']} ({res_data['brand']})")
        else:
            print(f"\n[Error] {response.json().get('error', 'Could not create item')}")
    except ValueError:
        print("\n[Input Error] Quantity must be an integer, and Price must be a decimal.")
    except requests.exceptions.ConnectionError:
        print("\n[Error] Connection Refused.")

def update_item():
    item_id = input("\nEnter Product ID to update: ").strip()
    if not item_id:
        return
    
    print("Leave empty to keep existing value.")
    new_qty = input("New Quantity: ").strip()
    new_price = input("New Price: ").strip()
    
    payload = {}
    try:
        if new_qty:
            payload["quantity"] = int(new_qty)
        if new_price:
            payload["price"] = float(new_price)
            
        if not payload:
            print("No updates made.")
            return

        response = requests.patch(f"{BASE_URL}/{item_id}", json=payload)
        if response.status_code == 200:
            print("\n[Success] Item updated successfully!")
        else:
            print(f"\n[Error] {response.json().get('error', 'Update failed')}")
    except ValueError:
        print("\n[Input Error] Invalid number formats provided.")
    except requests.exceptions.ConnectionError:
        print("\n[Error] Connection Refused.")

def delete_item():
    item_id = input("\nEnter Product ID to delete: ").strip()
    if not item_id:
        return
    confirm = input(f"Are you sure you want to permanently delete item {item_id}? (y/N): ").lower()
    if confirm != 'y':
        print("Deletion canceled.")
        return
        
    try:
        response = requests.delete(f"{BASE_URL}/{item_id}")
        if response.status_code == 200:
            print(f"\n[Success] {response.json().get('message')}")
        else:
            print(f"\n[Error] {response.json().get('error', 'Deletion failed')}")
    except requests.exceptions.ConnectionError:
         print("\n[Error] Connection Refused.")

def main():
    while True:
        display_menu()
        choice = input("Select an option (1-6): ").strip()
        if choice == "1":
            get_all_items()
        elif choice == "2":
            find_item_by_id()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            print("\nShutting down client. Goodbye!")
            sys.exit(0)
        else:
            print("\n[Invalid Selection] Please choose a valid menu number.")

if __name__ == "__main__":
    main()