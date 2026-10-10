def test_successful_login(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@technova.com",
        "password": "DemoPass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@technova.com"
    assert data["user"]["role"] == "tenant_admin"
    assert data["user"]["tenant_slug"] == "technova"


def test_failed_login_bad_password(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@technova.com",
        "password": "WrongPassword123!"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_failed_login_unknown_user(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "intruder@unknown.com",
        "password": "Password123!"
    })
    assert response.status_code == 401


def test_get_current_user_profile(client, technova_user_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {technova_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@technova.com"
    assert data["tenant_slug"] == "technova"


def test_unauthenticated_request_rejected(client):
    response = client.get("/api/v1/documents")
    assert response.status_code == 401


def test_invalid_jwt_rejected(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.fake.token"}
    )
    assert response.status_code == 401
