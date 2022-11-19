import json


def test_create_product(client):
    data = {"name":"testprpduct"}
    response = client.post("/products/",json.dumps(data))
    assert response.status_code == 200 
    assert response.json()["name"] == "testproduct"
    assert response.json()["is_active"] == True



def test_create_category(client):
    data = {"name":"testcategory"}
    response = client.post("/categories/",json.dumps(data))
    assert response.status_code == 200 
    assert response.json()["name"] == "testcategory"
    assert response.json()["is_active"] == True