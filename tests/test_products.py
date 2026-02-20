import pytest
import allure
from api.products_api import ProductsAPI
from schemas.product_schema import ProductCreateRequest, ProductUpdateRequest


@pytest.fixture
def products_api():
    return ProductsAPI()


@allure.feature("Products")
@allure.story("Read + Simulated Write Operations")
def test_product_lifecycle(products_api):
    with allure.step("Create product (POST /products/add)"):
        product_request = ProductCreateRequest(title="Test Product", description="Test Desc", price=99.99)
        new_product = products_api.create_product(product_request)
        assert new_product.title == "Test Product"
        assert new_product.id is not None

    stable_id = 1

    with allure.step(f"Update product {stable_id} (simulated)"):
        update_data = ProductUpdateRequest(title="Updated Title")
        updated = products_api.update_product(stable_id, update_data)
        assert updated.title == "Updated Title"

    with allure.step(f"Delete product {stable_id} (simulated)"):
        delete_resp = products_api.delete_product(stable_id)
        assert delete_resp.get("isDeleted") is True

    with allure.step("Get all products"):
        products_list = products_api.get_all_products()
        assert products_list.total > 0
        assert len(products_list.products) > 0

    with allure.step("Get product by ID"):
        product = products_api.get_product_by_id(stable_id)
        assert product.id == stable_id
