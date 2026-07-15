import pytest
from app import app, inventory_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Reset inventory before each test to guarantee isolated state
        inventory_db.clear()
        inventory_db["101"] = {
            "id": "101",
            "product_name": "Organic Almond Milk",
            "brand": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar",
            "quantity": 50,
            "price": 3.99
        }
        yield client

def test_get_all_items(client):
    response = client.get('/inventory')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == "101"

def test_get_single_item_found(client):
    response = client.get('/inventory/101')
    assert response.status_code == 200
    data = response.get_json()
    assert data['product_name'] == "Organic Almond Milk"

def test_get_single_item_not_found(client):
    response = client.get('/inventory/999')
    assert response.status_code == 404

def test_post_item_manual(client):
    new_payload = {
        "id": "102",
        "product_name": "Dark Chocolate",
        "brand": "Lindt",
        "ingredients_text": "Cocoa, Sugar, Cocoa Butter",
        "quantity": 100,
        "price": 4.50
    }
    response = client.post('/inventory', json=new_payload)
    assert response.status_code == 201
    
    # Assert database creation
    assert "102" in inventory_db
    assert inventory_db["102"]["product_name"] == "Dark Chocolate"

def test_post_item_duplicate_id_fails(client):
    duplicate_payload = {
        "id": "101",
        "product_name": "Another Almond Milk"
    }
    response = client.post('/inventory', json=duplicate_payload)
    assert response.status_code == 400

def test_patch_item(client):
    update_payload = {
        "quantity": 30,
        "price": 4.25
    }
    response = client.patch('/inventory/101', json=update_payload)
    assert response.status_code == 200
    assert inventory_db["101"]["quantity"] == 30
    assert inventory_db["101"]["price"] == 4.25

def test_delete_item(client):
    response = client.delete('/inventory/101')
    assert response.status_code == 200
    assert "101" not in inventory_db