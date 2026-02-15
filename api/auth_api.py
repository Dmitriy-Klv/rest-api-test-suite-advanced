import os
from api.base_api import BaseAPI
from schemas.auth_schema import LoginResponse

USERNAME = os.getenv("TEST_USERNAME")
PASSWORD = os.getenv("TEST_PASSWORD")


class AuthAPI(BaseAPI):
    def login(self, username: str = USERNAME, password: str = PASSWORD) -> LoginResponse:
        payload = {
            "username": username,
            "password": password
        }

        response = self.post(
            "/auth/login",
            json=payload,
            expected_status=200
        )

        auth_data = LoginResponse.model_validate(response.json())

        self.session.headers.update({
            "Authorization": f"Bearer {auth_data.token}"
        })

        return auth_data
