# client/cli.py
import requests
import sys

BASE_URL = "http://127.0.0.1:5555"

def show_menu():
    print("\n=== INVENTORY MANAGEMENT SYSTEM CLI ===")
    print("1. View Full Inventory Items")
    print("2. Search Item Details by ID")
    print("3. Create New Item Manually")
    print("4. Add Item via Barcode Scan (External API)")
    print("5. Update Price/Stock levels")
    print("6. Delete an Item")
    print("7. Exit Application")

def run_cli():
    while True:
        show_menu()
        choice = input("\nSelect an action option (1-7): ").strip()
        
        if choice == '1':
            res = requests.get(f"{BASE_URL}/inventory")
            for item in res.json():
                print(f"[{item['id']}] {item['product_name']} ({item['brands']}) - ${item['price']} | Stock: {item['stock']}")
                
        elif choice == '2':
            item_id = input("Enter Item ID: ")
            res = requests.get(f"{BASE_URL}/inventory/{item_id}")
            print(res.json())
            
        elif choice == '3':
            name = input("Product Name: ")
            brand = input("Brand Name: ")
            price = input("Price ($): ")
            stock = input("Stock count: ")
            payload = {"product_name": name, "brands": brand, "price": price, "stock": stock}
            res = requests.post(f"{BASE_URL}/inventory", json=payload)
            print("Response:", res.json())
            
        elif choice == '4':
            barcode = input("Scan/Enter product barcode numbers: ")
            price = input("Set retail sales price ($): ")
            stock = input("Initial warehouse stock counts: ")
            payload = {"barcode": barcode, "price": price, "stock": stock}
            res = requests.post(f"{BASE_URL}/inventory", json=payload)
            print("Response:", res.json())
            
        elif choice == '5':
            item_id = input("Enter Target Item ID to alter: ")
            price = input("New price (Leave blank to skip modification): ")
            stock = input("New stock level (Leave blank to skip modification): ")
            payload = {}
            if price: payload["price"] = price
            if stock: payload["stock"] = stock
            res = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
            print("Updated Status:", res.json())
            
        elif choice == '6':
            item_id = input("Confirm structural Item ID to eradicate: ")
            res = requests.delete(f"{BASE_URL}/inventory/{item_id}")
            print("Action message:", res.json())
            
        elif choice == '7':
            print("Exiting dashboard...")
            sys.exit()
        else:
            print("Invalid input selection options. Try again.")

if __name__ == "__main__":
    # Ensure server is running before kicking off CLI client terminal
    try:
        run_cli()
    except requests.exceptions.ConnectionError:
        print("Error: Make sure your Flask backend server is running on port 5555 first!")