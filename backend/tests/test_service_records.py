def create_vehicle(
    authenticated_client,
) -> int:
    response = authenticated_client.post(
        "/api/v1/vehicles",
        json={
            "registration": "AB12CDE",
            "make": "Honda",
            "model": "Civic",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_service_record_crud(
    authenticated_client,
):
    vehicle_id = create_vehicle(
        authenticated_client
    )

    create_response = (
        authenticated_client.post(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records"
            ),
            json={
                "service_date": "2026-08-10",
                "title": "Front brake pads",
                "category": "repair",
                "mileage": 82400,
                "garage": "Local Garage",
                "cost": 145.50,
                "notes": (
                    "Front pads replaced."
                ),
            },
        )
    )

    assert (
        create_response.status_code
        == 201
    )

    record = create_response.json()

    assert (
        record["title"]
        == "Front brake pads"
    )

    record_id = record["id"]

    list_response = (
        authenticated_client.get(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records"
            )
        )
    )

    assert (
        list_response.status_code
        == 200
    )

    assert len(
        list_response.json()
    ) == 1

    update_response = (
        authenticated_client.put(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records/"
                f"{record_id}"
            ),
            json={
                "cost": 155.00,
                "notes": (
                    "Pads and fitting."
                ),
            },
        )
    )

    assert (
        update_response.status_code
        == 200
    )

    assert (
        update_response.json()["cost"]
        == 155.0
    )

    delete_response = (
        authenticated_client.delete(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records/"
                f"{record_id}"
            )
        )
    )

    assert (
        delete_response.status_code
        == 204
    )


def test_receipt_upload_and_open(
    authenticated_client,
    monkeypatch,
    tmp_path,
):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "upload_dir",
        tmp_path,
    )

    vehicle_id = create_vehicle(
        authenticated_client
    )

    record_response = (
        authenticated_client.post(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records"
            ),
            json={
                "service_date": "2026-08-10",
                "title": "Brake pads purchased",
                "category": "parts",
            },
        )
    )

    record_id = (
        record_response.json()["id"]
    )

    pdf_bytes = (
        b"%PDF-1.4\n"
        b"fake test receipt\n"
        b"%%EOF"
    )

    upload_response = (
        authenticated_client.post(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records/"
                f"{record_id}/receipts"
            ),
            files={
                "file": (
                    "brake-pads.pdf",
                    pdf_bytes,
                    "application/pdf",
                )
            },
        )
    )

    assert (
        upload_response.status_code
        == 201
    )

    receipt = upload_response.json()

    assert (
        receipt["original_filename"]
        == "brake-pads.pdf"
    )

    open_response = (
        authenticated_client.get(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records/"
                f"{record_id}/receipts/"
                f"{receipt['id']}/file"
            )
        )
    )

    assert (
        open_response.status_code
        == 200
    )

    assert (
        open_response.content
        == pdf_bytes
    )


def test_invalid_receipt_type_is_rejected(
    authenticated_client,
    monkeypatch,
    tmp_path,
):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "upload_dir",
        tmp_path,
    )

    vehicle_id = create_vehicle(
        authenticated_client
    )

    record_response = (
        authenticated_client.post(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records"
            ),
            json={
                "service_date": "2026-08-10",
                "title": "Test",
                "category": "other",
            },
        )
    )

    record_id = (
        record_response.json()["id"]
    )

    response = (
        authenticated_client.post(
            (
                f"/api/v1/vehicles/"
                f"{vehicle_id}/service-records/"
                f"{record_id}/receipts"
            ),
            files={
                "file": (
                    "receipt.exe",
                    b"not allowed",
                    "application/octet-stream",
                )
            },
        )
    )

    assert response.status_code == 415