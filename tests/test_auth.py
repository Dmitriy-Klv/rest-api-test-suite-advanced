import allure
import pytest

from api.auth_api import AuthAPI
from api.base_api import APIError
from schemas.auth_schema import LoginResponse
from utils.config import settings


@pytest.fixture
def auth_api():
    return AuthAPI()


@allure.feature("Authentication")
@allure.story("Login with valid credentials")
def test_login_success(auth_api: AuthAPI):
    auth_data: LoginResponse = auth_api.login(
        settings.TEST_USERNAME, settings.TEST_PASSWORD.get_secret_value()
    )

    assert auth_data.token is not None, "JWT token is missing in the response"
    assert auth_data.username == settings.TEST_USERNAME
    assert "@" in auth_data.email


def test_login_invalid_credentials():
    api = AuthAPI()
    with pytest.raises(APIError):
        api.login("wrong_user", "wrong_pass")

