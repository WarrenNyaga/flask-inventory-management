from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Mock database simulating in-memory storage with some initial data
inventory_db = {
    "101": {
        "id": "101",
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "quantity": 50,
        "price": 3.99
    }
}

# Helper function to fetch data from OpenFoodFacts API
def fetch_external_product(barcode):
    """
    Queries the external OpenFoodFacts API using a barcode.
    Enhances inventory data with defensive error handling.
    """
    clean_barcode = str(barcode).strip()
    if not clean_barcode:
        return None
        
    url = f"https://world.openfoodfacts.org/api/v0/product/{clean_barcode}.json"
    try:
        # Added a User-Agent header and a strict 5-second timeout
        response = requests.get(url, headers={"User-Agent": "InventoryApp/1.0"}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product_data = data.get("product", {})
                return {
                    "product_name": product_data.get("product_name") or product_data.get("product_name_en") or "Unknown Product",
                    "brand": product_data.get("brands") or "Unknown Brand",
                    "ingredients_text": product_data.get("ingredients_text") or "No ingredients listed on file"
                }
    except requests.RequestException as e:
        print(f"[API Network Error] Connection to OpenFoodFacts failed: {e}")
    return None

# GET /inventory - Fetch all items
@app.route('/inventory', methods=['GET'])
def get_all_items():
    return jsonify(list(inventory_db.values())), 200

# GET /inventory/<id> - Fetch a single item
@app.route('/inventory/<id>', methods=['GET'])
def get_item(id):
    item = inventory_db.get(id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200

# POST /inventory - Add a new item
@app.route('/inventory', methods=['POST'])
def add_item():
    data = request.get_json() or {}
    
    # Validation
    item_id = data.get("id")
    if not item_id:
        return jsonify({"error": "ID is required"}), 400
    if item_id in inventory_db:
        return jsonify({"error": "Item with this ID already exists"}), 400
    
    quantity = data.get("quantity", 0)
    price = data.get("price", 0.0)
    
    # If barcode is provided, try fetching external data
    barcode = data.get("barcode")
    external_data = {}
    if barcode:
        fetched = fetch_external_product(barcode)
        if fetched:
            external_data = fetched

    # Merging input payload with external API data
    new_item = {
        "id": item_id,
        "product_name": data.get("product_name") or external_data.get("product_name") or "Unnamed Product",
        "brand": data.get("brand") or external_data.get("brand") or "Generic",
        "ingredients_text": data.get("ingredients_text") or external_data.get("ingredients_text") or "N/A",
        "quantity": int(quantity),
        "price": float(price)
    }
    
    inventory_db[item_id] = new_item
    return jsonify(new_item), 201

# PATCH /inventory/<id> - Update an item
@app.route('/inventory/<id>', methods=['PATCH'])
def update_item(id):
    if id not in inventory_db:
        return jsonify({"error": "Item not found"}), 404
    
    data = request.get_json() or {}
    item = inventory_db[id]
    
    if "product_name" in data:
        item["product_name"] = data["product_name"]
    if "brand" in data:
        item["brand"] = data["brand"]
    if "ingredients_text" in data:
        item["ingredients_text"] = data["ingredients_text"]
    if "quantity" in data:
        item["quantity"] = int(data["quantity"])
    if "price" in data:
        item["price"] = float(data["price"])
        
    return jsonify(item), 200

# DELETE /inventory/<id> - Remove an item
@app.route('/inventory/<id>', methods=['DELETE'])
def delete_item(id):
    if id not in inventory_db:
        return jsonify({"error": "Item not found"}), 404
    
    deleted_item = inventory_db.pop(id)
    return jsonify({"message": f"Item '{deleted_item['product_name']}' successfully deleted."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)