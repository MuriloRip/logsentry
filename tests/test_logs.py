from fastapi import status


class TestLogEndpoints:
    """Test suite for log ingestion and querying."""

    def _create_log(self, client, auth_headers, **kwargs):
        default = {
            "level": "INFO",
            "message": "Test log message",
            "source": "app.test",
            "service_name": "test-service",
        }
        default.update(kwargs)
        return client.post("/api/v1/logs/", json=default, headers=auth_headers)

    def test_create_log_entry(self, client, auth_headers):
        response = self._create_log(client, auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["level"] == "INFO"
        assert data["message"] == "Test log message"
        assert data["source"] == "app.test"

    def test_create_log_requires_auth(self, client):
        response = client.post(
            "/api/v1/logs/",
            json={
                "level": "INFO",
                "message": "test",
                "source": "test",
                "service_name": "test",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_batch_ingestion(self, client, auth_headers):
        batch = {
            "entries": [
                {"level": "INFO", "message": "Log 1", "source": "app.a", "service_name": "svc-a"},
                {"level": "ERROR", "message": "Log 2", "source": "app.b", "service_name": "svc-b"},
                {"level": "WARNING", "message": "Log 3", "source": "app.c", "service_name": "svc-c"},
            ]
        }
        response = client.post("/api/v1/logs/batch", json=batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert "3" in response.json()["message"]

    def test_list_logs_with_pagination(self, client, auth_headers):
        # Create several logs
        for i in range(5):
            self._create_log(client, auth_headers, message=f"Log entry {i}")

        response = client.get(
            "/api/v1/logs/?page=1&page_size=2", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["total_pages"] == 3

    def test_filter_by_level(self, client, auth_headers):
        self._create_log(client, auth_headers, level="INFO")
        self._create_log(client, auth_headers, level="ERROR")
        self._create_log(client, auth_headers, level="ERROR")

        response = client.get(
            "/api/v1/logs/?level=ERROR", headers=auth_headers
        )
        data = response.json()
        assert data["total"] == 2
        assert all(item["level"] == "ERROR" for item in data["items"])

    def test_get_log_by_id(self, client, auth_headers):
        create_resp = self._create_log(client, auth_headers)
        entry_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/logs/{entry_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == entry_id

    def test_delete_log_entry(self, client, auth_headers):
        create_resp = self._create_log(client, auth_headers)
        entry_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/logs/{entry_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        response = client.get(f"/api/v1/logs/{entry_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_returns_404(self, client, auth_headers):
        response = client.delete("/api/v1/logs/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
