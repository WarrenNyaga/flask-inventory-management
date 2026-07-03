# server/external_api.py
import requests

def fetch_product_by_barcode(barcode):
    """
    Fetches food details from the OpenFoodFacts API using a barcode string.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1: # 1 means product found
                product_data = data.get("product", {})
                return {
                    "product_name": product_data.get("product_name", "Unknown Item"),
                    "brands": product_data.get("brands", "Generic"),
                    "ingredients": product_data.get("ingredients_text", "No ingredients listed")
                }
    except requests.RequestException:
        pass
    return None