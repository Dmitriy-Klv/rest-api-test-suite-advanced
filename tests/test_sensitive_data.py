import pytest
import allure

from api.products_api import ProductsAPI


SENSITIVE_FIELDS = {
    "password",
    "token",
    "accessToken",
    "refreshToken",
    "internalId",
    "debug",
    "secret",
}


@allure.story("Security: API should not expose sensitive data")
def test_no_sensitive_data_exposure(products_api: ProductsAPI):

    with allure.step("Fetch products list"):
        response = products_api.get("/products", expected_status=200)
        data = response.json()

    def check_for_sensitive_keys(obj, path="root"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in SENSITIVE_FIELDS, (
                    f"Sensitive field '{key}' exposed at {path}"
                )
                check_for_sensitive_keys(value, f"{path}.{key}")

        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                check_for_sensitive_keys(item, f"{path}[{index}]")

    with allure.step("Scan entire response for sensitive fields"):
        check_for_sensitive_keys(data)