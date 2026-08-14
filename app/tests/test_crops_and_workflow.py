from datetime import date, timedelta


def setup_active_field(client, headers, farm_name="Crop Farm", field_name="Field 1"):
    resp = client.post(
        "/farms",
        json={"farm_name": farm_name, "location": "Madurai", "total_area": 100, "owner_name": "Farmer X"},
        headers=headers,
    )
    farm_id = resp.json()["id"]

    resp = client.post(
        f"/farms/{farm_id}/fields",
        json={"field_name": field_name, "area": 10, "soil_type": "Clay", "irrigation_type": "Sprinkler"},
        headers=headers,
    )
    return resp.json()["id"]


def test_crop_planting_date_validation(client, make_auth_headers):
    headers = make_auth_headers(role="admin", email="admin5@example.com")
    field_id = setup_active_field(client, headers)

    resp = client.post(
        "/crops",
        json={
            "field_id": field_id,
            "crop_name": "Wheat",
            "crop_type": "Cereal",
            "planting_date": str(date.today()),
            "expected_harvest_date": str(date.today() - timedelta(days=1)),
            "seed_quantity": 50,
        },
        headers=headers,
    )
    assert resp.status_code == 422


def test_no_overlapping_active_crops_on_same_field(client, make_auth_headers):
    headers = make_auth_headers(role="admin", email="admin6@example.com")
    field_id = setup_active_field(client, headers)

    resp = client.post(
        "/crops",
        json={
            "field_id": field_id,
            "crop_name": "Rice",
            "crop_type": "Cereal",
            "planting_date": str(date.today()),
            "expected_harvest_date": str(date.today() + timedelta(days=90)),
            "seed_quantity": 20,
        },
        headers=headers,
    )
    assert resp.status_code == 201

    resp2 = client.post(
        "/crops",
        json={
            "field_id": field_id,
            "crop_name": "Maize",
            "crop_type": "Cereal",
            "planting_date": str(date.today()),
            "expected_harvest_date": str(date.today() + timedelta(days=90)),
            "seed_quantity": 20,
        },
        headers=headers,
    )
    assert resp2.status_code == 400


def test_full_crop_to_sale_workflow(client, make_auth_headers):
    """End-to-end: crop -> irrigation -> treatment -> health -> harvest -> sale."""
    headers = make_auth_headers(role="admin", email="admin7@example.com")
    field_id = setup_active_field(client, headers, farm_name="Workflow Farm", field_name="Workflow Field")

    resp = client.post(
        "/crops",
        json={
            "field_id": field_id,
            "crop_name": "Tomato",
            "crop_type": "Vegetable",
            "planting_date": str(date.today()),
            "expected_harvest_date": str(date.today() + timedelta(days=60)),
            "seed_quantity": 5,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    crop_id = resp.json()["id"]

    # Irrigation allowed because the crop is active.
    resp = client.post(
        "/irrigation",
        json={
            "field_id": field_id,
            "irrigation_date": str(date.today()),
            "water_quantity": 500,
            "duration_minutes": 30,
        },
        headers=headers,
    )
    assert resp.status_code == 201

    # Fertilizer treatment.
    resp = client.post(
        "/crop-treatments",
        json={
            "crop_id": crop_id,
            "product_name": "NPK Mix",
            "product_type": "fertilizer",
            "quantity": 10,
            "applied_date": str(date.today()),
            "cost": 25.5,
        },
        headers=headers,
    )
    assert resp.status_code == 201

    # Critical health record should raise an alert (checked indirectly via dashboard).
    resp = client.post(
        "/crop-health",
        json={
            "crop_id": crop_id,
            "inspection_date": str(date.today()),
            "health_status": "critical",
            "disease_name": "Blight",
            "severity": "high",
        },
        headers=headers,
    )
    assert resp.status_code == 201

    # Harvest cannot be created yet — crop is not "ready_for_harvest".
    resp = client.post(
        "/harvests",
        json={
            "crop_id": crop_id,
            "harvest_date": str(date.today()),
            "quantity": 100,
            "unit": "kg",
            "quality_grade": "A",
        },
        headers=headers,
    )
    assert resp.status_code == 400

    # Move crop to ready_for_harvest.
    resp = client.put(f"/crops/{crop_id}", json={"status": "ready_for_harvest"}, headers=headers)
    assert resp.status_code == 200

    # Now harvest succeeds and crop status flips to harvested.
    resp = client.post(
        "/harvests",
        json={
            "crop_id": crop_id,
            "harvest_date": str(date.today()),
            "quantity": 100,
            "unit": "kg",
            "quality_grade": "A",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    harvest_id = resp.json()["id"]

    resp = client.get(f"/crops/{crop_id}", headers=headers)
    assert resp.json()["status"] == "harvested"

    # Harvested crop can no longer be modified.
    resp = client.put(f"/crops/{crop_id}", json={"crop_name": "Renamed"}, headers=headers)
    assert resp.status_code == 400

    # Sell part of the harvest.
    resp = client.post(
        "/sales",
        json={
            "harvest_id": harvest_id,
            "buyer_name": "Local Market",
            "quantity": 60,
            "price_per_unit": 12,
            "sale_date": str(date.today()),
        },
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["total_amount"] == 720

    # Selling more than what remains (100 - 60 = 40 remaining) must fail.
    resp = client.post(
        "/sales",
        json={
            "harvest_id": harvest_id,
            "buyer_name": "Another Buyer",
            "quantity": 50,
            "price_per_unit": 12,
            "sale_date": str(date.today()),
        },
        headers=headers,
    )
    assert resp.status_code == 400

    # Dashboard summary should reflect the critical alert and totals.
    resp = client.get("/dashboard/summary", headers=headers)
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["critical_crop_alerts"] >= 1
    assert summary["total_sales"] >= 1
    assert summary["total_revenue"] >= 720
