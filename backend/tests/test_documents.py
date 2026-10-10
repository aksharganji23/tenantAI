import io


def test_upload_invalid_extension(client, technova_admin_token):
    file_content = b"malicious binary payload"
    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {technova_admin_token}"},
        files={"file": ("exploit.exe", io.BytesIO(file_content), "application/octet-stream")},
        data={"title": "Exploit"}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_valid_txt_document(client, technova_admin_token):
    sample_text = (
        "TechNova Cloud Storage Service Level Agreement.\n\n"
        "Availability Guarantee: 99.99% monthly uptime.\n"
        "Support Tier: 24/7 dedicated enterprise response within 15 minutes."
    )
    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {technova_admin_token}"},
        files={"file": ("sla_policy.txt", io.BytesIO(sample_text.encode("utf-8")), "text/plain")},
        data={"title": "Cloud SLA Policy"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Cloud SLA Policy"
    assert data["status"] == "READY"
    assert data["chunk_count"] > 0

    # Clean up created doc
    del_resp = client.delete(
        f"/api/v1/documents/{data['id']}",
        headers={"Authorization": f"Bearer {technova_admin_token}"}
    )
    assert del_resp.status_code == 200
