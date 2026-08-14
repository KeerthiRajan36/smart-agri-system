def test_create_farm_requires_auth(client):
    resp = client.post(
        "/farms",
        json={"farm_name": "Green Acres", "location": "Chennai", "total_area": 100, "owner_name": "Farmer John"},
    )
    assert resp.status_code in (401, 403)


def test_create_and_list_farm(client, make_auth_headers):
    headers = make_auth_headers(role="admin", email="admin2@example.com")
    resp = client.post(
        "/farms",
        json={"farm_name": "Green Acres", "location": "Chennai", "total_area": 100, "owner_name": "Farmer John"},
        headers=headers,
    )
    assert resp.status_code == 201
    farm = resp.json()
    assert farm["farm_name"] == "Green Acres"
    assert farm["status"] == "active"

    resp = client.get("/farms", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["farm_name"] == "Green Acres"


def test_farmer_role_cannot_create_farm(client, make_auth_headers):
    headers = make_auth_headers(role="farmer", email="farmer1@example.com")
    resp = client.post(
        "/farms",
        json={"farm_name": "Unauthorized Farm", "location": "Chennai", "total_area": 50, "owner_name": "Someone"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_duplicate_farm_name_rejected(client, make_auth_headers):
    headers = make_auth_headers(role="admin", email="admin3@example.com")
    payload = {"farm_name": "Unique Farm", "location": "Salem", "total_area": 20, "owner_name": "X. Farmer"}
    resp1 = client.post("/farms", json=payload, headers=headers)
    assert resp1.status_code == 201
    resp2 = client.post("/farms", json=payload, headers=headers)
    assert resp2.status_code == 400


def test_field_area_cannot_exceed_farm_area(client, make_auth_headers):
    headers = make_auth_headers(role="admin", email="admin4@example.com")
    resp = client.post(
        "/farms",
        json={"farm_name": "Small Farm", "location": "Coimbatore", "total_area": 10, "owner_name": "Farmer Jane"},
        headers=headers,
    )
    farm_id = resp.json()["id"]

    resp = client.post(
        f"/farms/{farm_id}/fields",
        json={"field_name": "Field A", "area": 20, "soil_type": "Loamy", "irrigation_type": "Drip"},
        headers=headers,
    )
    assert resp.status_code == 400

    resp = client.post(
        f"/farms/{farm_id}/fields",
        json={"field_name": "Field A", "area": 5, "soil_type": "Loamy", "irrigation_type": "Drip"},
        headers=headers,
    )
    assert resp.status_code == 201
