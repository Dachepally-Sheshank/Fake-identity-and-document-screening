def upload(client, filename: str = "synthetic_fake_id.png"):
    return client.post("/api/v1/documents/upload", files={"file": (filename, b"synthetic-test-image", "image/png")})


def test_upload_analyze_face_explain_and_audit(client):
    uploaded = upload(client)
    assert uploaded.status_code == 201
    document_id = uploaded.json()["document_id"]

    analyzed = client.post(f"/api/v1/documents/{document_id}/analyze", json={"demo_scenario": "auto"})
    assert analyzed.status_code == 201
    verification = analyzed.json()
    assert verification["decision"] == "HIGH_RISK"
    assert verification["risk_score"] >= 70
    assert any(signal["id"] == "critical_escalation" for signal in verification["signals"])

    face = client.post(f"/api/v1/verification/{verification['id']}/face-match", json={"demo_outcome": "mismatch"})
    assert face.status_code == 200
    assert face.json()["decision"] == "HIGH_RISK"
    assert client.get(f"/api/v1/verification/{verification['id']}/explanation").status_code == 200
    audit = client.get(f"/api/v1/audit/{verification['id']}")
    assert audit.status_code == 200
    assert len(audit.json()["document_hash"]) == 64


def test_upload_rejects_unsupported_file(client):
    response = client.post("/api/v1/documents/upload", files={"file": ("not-a-document.txt", b"x", "text/plain")})
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "HTTP_415"


def test_duplicate_upload_reuses_the_existing_document(client):
    first = upload(client, "synthetic_repeat.png")
    second = upload(client, "synthetic_repeat.png")
    assert first.status_code == second.status_code == 201
    assert first.json()["document_id"] == second.json()["document_id"]


def test_validation_error_is_structured(client):
    response = client.post("/api/v1/documents/missing/analyze", json={"demo_scenario": "unknown"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
