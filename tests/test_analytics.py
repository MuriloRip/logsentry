from fastapi import status


class TestAnalyticsEndpoints:
    """Test suite for analytics endpoints."""

    def _create_log(self, client, auth_headers, level="INFO", service="svc-a", source="app.main"):
        return client.post(
            "/api/v1/logs/",
            json={
                "level": level,
                "message": f"Log from {service}",
                "source": source,
                "service_name": service,
            },
            headers=auth_headers,
        )

    def test_get_stats(self, client, auth_headers):
        self._create_log(client, auth_headers, level="INFO")
        self._create_log(client, auth_headers, level="ERROR")
        self._create_log(client, auth_headers, level="ERROR")

        response = client.get("/api/v1/analytics/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_entries"] == 3
        assert data["by_level"]["error"] == 2
        assert data["by_level"]["info"] == 1

    def test_get_top_errors(self, client, auth_headers):
        self._create_log(client, auth_headers, level="ERROR", source="app.auth")
        self._create_log(client, auth_headers, level="ERROR", source="app.auth")
        self._create_log(client, auth_headers, level="ERROR", source="app.payment")

        response = client.get("/api/v1/analytics/top-errors", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["source"] == "app.auth"
        assert data[0]["error_count"] == 2

    def test_get_service_breakdown(self, client, auth_headers):
        self._create_log(client, auth_headers, service="user-svc")
        self._create_log(client, auth_headers, service="user-svc")
        self._create_log(client, auth_headers, service="payment-svc", level="ERROR")

        response = client.get("/api/v1/analytics/services", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_analytics_requires_auth(self, client):
        response = client.get("/api/v1/analytics/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
