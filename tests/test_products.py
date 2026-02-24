import pytest
import allure
from api.products_api import ProductsAPI
from schemas.product_schema import ProductCreateRequest, ProductUpdateRequest, ProductListResponse
from faker import Faker


fake = Faker()

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


@allure.story("Data-driven product creation")
def test_create_random_product(products_api):
    payload = ProductCreateRequest(
        title=fake.catch_phrase(),
        description=fake.paragraph(nb_sentences=2),
        price=round(fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=1), 2)
    )

    with allure.step(f"Create product with random data: {payload.title}"):
        product = products_api.create_product(payload)
        assert product.title == payload.title
        assert product.price == payload.price


@allure.story("Search products by query")
@pytest.mark.parametrize("query", ["Phone", "Computers", "Laptop"])
def test_search_products(products_api, query):
    with allure.step(f"Search for '{query}'"):
        response = products_api.get(f"/products/search?q={query}", expected_status=200)
        data = ProductListResponse.model_validate(response.json())

        for product in data.products:
            assert query.lower() in product.title.lower() or query.lower() in product.description.lower(), \
                f"Product {product.id} does not match search query '{query}'"