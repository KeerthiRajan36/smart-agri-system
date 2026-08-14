def test_register_and_login(client):
    resp = client.post(
        "/auth/register",
        json={
            "full_name": "Alice Admin",
            "email": "alice@example.com",
            "password": "strongpass1",
            "role": "admin",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "admin"

    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "strongpass1"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body

    headers = {"Authorization": f"Bearer {body['access_token']}"}
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_login_invalid_credentials(client):
    resp = client.post("/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_duplicate_registration(client):
    payload = {
        "full_name": "Bob",
        "email": "bob@example.com",
        "password": "password123",
        "role": "farmer",
    }
    resp1 = client.post("/auth/register", json=payload)
    assert resp1.status_code == 201
    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 400


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 403)
