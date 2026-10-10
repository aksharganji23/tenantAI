from app.api import auth
from app.models.email_verification import EmailVerificationCode
from app.models.tenant import Tenant
from app.models.user import User
from tests.conftest import TestingSessionLocal


def test_registration_requires_email_verification(client, monkeypatch):
    sent = {}

    def capture_code(recipient, code):
        sent["recipient"] = recipient
        sent["code"] = code

    monkeypatch.setattr(auth, "send_verification_code", capture_code)
    email = "new-admin@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "company_name": "Example Company",
            "company_slug": "example-company",
            "full_name": "New Admin",
            "email": email,
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 200
    assert sent["recipient"] == email
    assert len(sent["code"]) == 6

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass123!"},
    )
    assert blocked.status_code == 403

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == email).one()
        challenge = db.query(EmailVerificationCode).filter(EmailVerificationCode.user_id == user.id).one()
        assert challenge.code_hash != sent["code"]
    finally:
        db.close()

    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"email": email, "otp": sent["code"]},
    )
    assert verified.status_code == 200
    allowed = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass123!"},
    )
    assert allowed.status_code == 200

    db = TestingSessionLocal()
    db.query(Tenant).filter(Tenant.slug == "example-company").delete()
    db.commit()
    db.close()
