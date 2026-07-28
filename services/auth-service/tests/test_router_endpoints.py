"""Covers router/dependency paths not exercised by the Gherkin-scenario tests in
test_auth.py: the CARS redirect helper endpoint, direct /login, /me, and the
auth failure branches (invalid bearer token, UDID service unavailable)."""


def _register_and_login(client, email):
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "username": email.split("@")[0],
            "password": "S3cure!Pass",
            "role": "user",
        },
    )
    resp = client.get(f"/api/auth/cars/callback?code=dev-code:{email}:S3cure!Pass:true")
    return resp.json()["data"]["access_token"]


def test_cars_authorize_redirect_returns_url(client):
    resp = client.get("/api/auth/cars/authorize")
    assert resp.status_code == 200
    assert resp.json()["data"]["redirect_url"].startswith("http")


def test_login_endpoint_success(client):
    email = "direct-login@example.com"
    _register_and_login(client, email)  # ensures user exists
    resp = client.post(
        "/api/auth/login",
        json={"principal": {"email": email, "password": "S3cure!Pass", "isEnabled": True}},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["access_token"]


def test_me_endpoint_returns_current_user(client):
    email = "me-endpoint@example.com"
    token = _register_and_login(client, email)
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == email


def test_me_endpoint_without_token_is_rejected(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401  # HTTPBearer: no credentials supplied


def test_verify_udid_rejects_invalid_token(client):
    resp = client.post(
        "/api/auth/verify-udid",
        json={"udid_number": "SF-1"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    # Raised directly by ecom_core's get_current_user as an HTTPException — this is
    # FastAPI's default {"detail": ...} envelope, not the StandardResponse one, since
    # it never reaches our custom exception handlers.
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid or expired token"


def test_verify_udid_service_unavailable_returns_502(client):
    email = "udid-timeout@example.com"
    token = _register_and_login(client, email)
    resp = client.post(
        "/api/auth/verify-udid",
        json={"udid_number": "TIMEOUT"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 502
    assert resp.json()["message_code"] == "udid_service_unavailable"


def test_cars_callback_rejects_unrecognized_code(client):
    resp = client.get("/api/auth/cars/callback?code=not-a-dev-code")
    assert resp.status_code == 401
    assert resp.json()["message_code"] == "cars_auth_failed"


def test_register_duplicate_email_returns_409(client):
    email = "dup@example.com"
    client.post(
        "/api/auth/register",
        json={"email": email, "username": "dupuser1", "password": "S3cure!Pass", "role": "user"},
    )
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "username": "dupuser2", "password": "S3cure!Pass", "role": "user"},
    )
    assert resp.status_code == 409
    assert resp.json()["message_code"] == "duplicate_resource"


def test_register_with_invalid_role_returns_422(client):
    # RegisterRequest.role is a Literal of the known role names, so an unknown role
    # is rejected by request validation before it ever reaches AuthService.register_user.
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "badrole@example.com",
            "username": "badrole",
            "password": "S3cure!Pass",
            "role": "not_a_real_role",
        },
    )
    assert resp.status_code == 422
    assert resp.json()["message_code"] == "validation_error"


def test_register_with_missing_field_returns_422(client):
    resp = client.post("/api/auth/register", json={"email": "incomplete@example.com"})
    assert resp.status_code == 422
    assert resp.json()["message_code"] == "validation_error"
