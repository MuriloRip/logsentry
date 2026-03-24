from fastapi import status


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""

    def test_register_user_successfully(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "secret123",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client):
        user_data = {
            "username": "user1",
            "email": "dup@example.com",
            "password": "secret123",
        }
        client.post("/api/v1/auth/register", json=user_data)

        user_data["username"] = "user2"
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_login_successfully(self, client):
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "secret123",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            data={"username": "login@example.com", "password": "secret123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client):
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "wrongpw",
                "email": "wrong@example.com",
                "password": "secret123",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            data={"username": "wrong@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_authenticated(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == "testuser"

    def test_get_me_unauthenticated(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
