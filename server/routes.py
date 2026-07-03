# server/routes.py
from flask import jsonify, request, make_response
from server.database import INVENTORY_DATABASE, get_next_id
from server.external_api import fetch_product_by_barcode

def initialize_routes(app):

    # 1. GET /inventory - Fetch all items
    @app.route('/inventory', methods=['GET'])
    def get_all_items():
        return jsonify(INVENTORY_DATABASE), 200

    # 2. GET /inventory/<id> - Fetch a single item
    @app.route('/inventory/<int:item_id>', methods=['GET'])
    def get_single_item(item_id):
        item = next((i for i in INVENTORY_DATABASE if i["id"] == item_id), None)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item), 200

    # 3. POST /inventory - Add a brand new item (Supports standard manual adds or Barcode scan adds)
    @app.route('/inventory', methods=['POST'])
    def add_item():
        data = request.get_json(silent=True)
        if data is None:
            data = request.form.to_dict()
        data = data or {}
        barcode = data.get("barcode")

        # If barcode provided, auto-fetch details from OpenFoodFacts
        if barcode:
            external_data = fetch_product_by_barcode(barcode)
            if external_data:
                # Use fetched values only when not provided in the payload
                data.setdefault("product_name", external_data.get("product_name"))
                data.setdefault("brands", external_data.get("brands"))
                data.setdefault("ingredients", external_data.get("ingredients"))

        if not data.get("product_name"):
            return jsonify({"error": "Missing product_name"}), 400

        try:
            # This safely checks if values exist before turning them into numbers
            price_val = float(data.get("price", 0) or 0)
            stock_val = int(data.get("stock", 0) or 0)
        except (ValueError, TypeError):
            return jsonify({"error": "Price must be a number and stock must be an integer"}), 400

        new_item = {
            "id": get_next_id(),
            "product_name": data["product_name"],
            "brands": data.get("brands", "Generic"),
            "ingredients": data.get("ingredients", "N/A"),
            "price": price_val,
            "stock": stock_val
        }
        INVENTORY_DATABASE.append(new_item)
        return jsonify(new_item), 201

    # 4. PATCH /inventory/<id> - Update an item properties
    @app.route('/inventory/<int:item_id>', methods=['PATCH'])
    def update_item(item_id):
        item = next((i for i in INVENTORY_DATABASE if i["id"] == item_id), None)
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        data = request.get_json() or {}
        if "price" in data:
            item["price"] = float(data["price"])
        if "stock" in data:
            item["stock"] = int(data["stock"])
        if "product_name" in data:
            item["product_name"] = data["product_name"]
            
        return jsonify(item), 200

    # 5. DELETE /inventory/<id> - Remove an item
    @app.route('/inventory/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        global INVENTORY_DATABASE
        item = next((i for i in INVENTORY_DATABASE if i["id"] == item_id), None)
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        INVENTORY_DATABASE.remove(item)
        return jsonify({"message": f"Successfully deleted item {item_id}"}), 200