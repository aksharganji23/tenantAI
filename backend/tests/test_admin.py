def test_admin_stats_access_as_superadmin(client, superadmin_token):
    response = client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {superadmin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_tenants"] >= 2
    assert data["total_users"] >= 5
    assert data["total_documents"] >= 2


def test_admin_stats_access_denied_for_regular_user(client, technova_user_token):
    response = client.get(
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    assert response.status_code == 403
    assert "Superadmin" in response.json()["detail"]


def test_usage_logs_isolation(client, technova_admin_token):
    # Tenant admins can view only redacted logs for their tenant.
    technova_user_token = technova_admin_token
    response = client.get(
        "/api/v1/logs",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0
    # None of the logs should have GreenLeaf tenant info
    for log in logs:
        assert log["tenant_name"] != "GreenLeaf Retail"
        assert log["user_email"] is None
        assert log["ip_address"] is None


def test_usage_logs_denied_for_regular_user(client, technova_user_token):
    response = client.get("/api/v1/logs", headers={"Authorization": f"Bearer {technova_user_token}"})
    assert response.status_code == 403


def test_cross_tenant_simulation_denied_for_regular_user(client, technova_user_token):
    response = client.post(
        "/api/v1/admin/security/simulate-cross-tenant-attack",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    assert response.status_code == 403


def test_cross_tenant_simulation_endpoint(client, superadmin_token):
    response = client.post(
        "/api/v1/admin/security/simulate-cross-tenant-attack",
        headers={"Authorization": f"Bearer {superadmin_token}"},
        params={
            "source_tenant_slug": "greenleaf",
            "target_tenant_slug": "technova",
            "resource_type": "document"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_blocked"] is True
    assert data["data_leaked"] is False
    assert data["http_status"] == 404
    assert data["audit_logged"] is True
