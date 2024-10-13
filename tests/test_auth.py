from passlib.context import CryptContext

from models.user import User


class TestAuthAPI:
    def test_login_no_user(self, client):
        response = client.post(
            "/api/v1/login", data={"username": "no-user", "password": "no-pass"}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "User no-user not found."}

    def test_login_success_user(self, client, db_session):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user = User(
            username="sample-user", hashed_password=pwd_context.hash("sample-password")
        )
        db_session.add(user)
        db_session.commit()

        response = client.post(
            "/api/v1/login",
            data={"username": "sample-user", "password": "sample-password"},
        )
        assert response.status_code == 200

        response_data = response.json()
        assert response_data
        assert "access_token" in response_data
        assert (
            "token_type" in response_data
            and response_data.get("token_type") == "Bearer"
        )
