"""Tests mirror US-001's Gherkin acceptance criteria one-to-one
(docs/user-stories/stories/domain-registration-auth/US-001-sso-registration-login.md)."""


def _register(client, email="buyer@example.com", role="user", udid_number="SF-000"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "username": email.split("@")[0],
            "password": "S3cure!Pass",
            "role": role,
            "udid_number": udid_number,
        },
    )


def test_new_user_registers_via_cars_sso(client):
    # Scenario: New user registers via CARS SSO
    resp = _register(client)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["role"] == "user"
    assert body["data"]["udid_verified"] is False  # UDID not required to complete registration


def test_registered_user_logs_in(client):
    # Scenario: Registered user logs in
    _register(client, email="login@example.com")
    login_code = "dev-code:login@example.com:S3cure!Pass:true"
    resp = client.get(f"/api/auth/cars/callback?code={login_code}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["role"] == "user"
    assert body["data"]["access_token"]


def test_post_login_udid_verification_success_and_failure(client):
    # Scenario: Post-login UDID verification for sponsored purchase
    _register(client, email="udid@example.com", udid_number=None)
    login_code = "dev-code:udid@example.com:S3cure!Pass:true"
    token = client.get(f"/api/auth/cars/callback?code={login_code}").json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # success path
    ok_resp = client.post("/api/auth/verify-udid", json={"udid_number": "SF-12345"}, headers=headers)
    assert ok_resp.status_code == 200
    assert ok_resp.json()["data"]["udid_verified"] is True

    # failure path (fresh user, no-match UDID)
    _register(client, email="udid2@example.com", udid_number=None)
    token2 = client.get(
        f"/api/auth/cars/callback?code=dev-code:udid2@example.com:S3cure!Pass:true"
    ).json()["data"]["access_token"]
    fail_resp = client.post(
        "/api/auth/verify-udid",
        json={"udid_number": "NOT-A-MATCH"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert fail_resp.status_code == 422
    assert fail_resp.json()["success"] is False


def test_blocked_user_cannot_log_in(client):
    # Scenario: Blocked user cannot log in
    _register(client, email="blocked@example.com")

    # Simulate a Super Admin block (US-014) by flipping is_active directly via /login's
    # underlying model — exercised here through direct DB access since US-014's own
    # block endpoint is out of this story's scope.
    from app.database import SessionLocal
    from app.models import User

    db = SessionLocal()
    user = db.query(User).filter(User.email == "blocked@example.com").first()
    user.is_active = False
    db.commit()
    db.close()

    resp = client.get("/api/auth/cars/callback?code=dev-code:blocked@example.com:S3cure!Pass:true")
    assert resp.status_code == 403
    assert resp.json()["message_code"] == "account_blocked"


def test_password_reset_entry_point_and_invalid_login(client):
    # Password reset itself is CARS-hosted (out of this service's UI scope, see ADR-0001);
    # this test covers the invalid-credentials branch that /login's principal exchange guards.
    _register(client, email="reset@example.com")
    resp = client.post(
        "/api/auth/login",
        json={"principal": {"email": "reset@example.com", "password": "WrongPassword!", "isEnabled": True}},
    )
    assert resp.status_code == 401
    assert resp.json()["message_code"] == "invalid_credentials"
