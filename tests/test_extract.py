"""Test Extract module."""

from unittest.mock import MagicMock, Mock

from dependencies import get_pinecone_index, get_redis_client


class TestExtractAPI:
    """Test Extract API."""

    def test_extract_empty_body(self, login_client):
        """
        Test Extract API with empty body.

        :param login_client: login client
        """
        test_client, _ = login_client

        response = test_client.post("/api/v1/extract")

        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body"],
                    "msg": "Field required",
                    "input": None,
                }
            ]
        }

    def test_extract_valid_new_search(self, login_client):
        """
        Test Extract API with valid new search (not cached).

        :param login_client:
        :return:
        """
        test_client, app = login_client

        mock_pinecone = Mock()
        mock_pinecone.query.return_value = Mock(
            matches=[MagicMock(score=1, metadata={"text": "Sample matching text"})]
        )
        app.dependency_overrides[get_pinecone_index] = lambda: mock_pinecone

        response = test_client.post(
            "/api/v1/extract",
            json={"query_text": "Sample", "file_id": "not-cached-file-name"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "data": [{"score": 1, "text": "Sample matching text"}]
        }

    def test_extract_valid_cached_search(self, login_client):
        """
        Test Extract API with valid cached search.

        :param login_client: login client fixture
        """
        test_client, app = login_client

        mock_redis = Mock()
        mock_redis.get = lambda *args: b'[{"score": 1, "text": "Sample matching text"}]'
        app.dependency_overrides[get_redis_client] = lambda: mock_redis

        response = test_client.post(
            "/api/v1/extract",
            json={"query_text": "Sample", "file_id": "cached-file-name"},
        )

        print(response.json())
        assert response.status_code == 200

        assert response.json() == {
            "data": [{"score": 1, "text": "Sample matching text"}]
        }
