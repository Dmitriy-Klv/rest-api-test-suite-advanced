import pytest
import allure
from faker import Faker

from api.products_api import ProductsAPI
from schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductListResponse,
)

pytestmark = allure.feature("Products API")

fake = Faker()
STABLE_PRODUCT_ID = 1


@pytest.fixture
def products_api():
    return ProductsAPI()


@allure.story("Read + Simulated Write Operations")
def test_product_lifecycle(products_api):
    with allure.step("Create product (POST /products/add)"):
        product_request = ProductCreateRequest(
            title="Test Product",
            description="Test Desc",
            price=99.99,
        )
        new_product = products_api.create_product(product_request)

        assert new_product.title == "Test Product"
        assert new_product.id is not None

    with allure.step(f"Update product {STABLE_PRODUCT_ID} (simulated)"):
        update_data = ProductUpdateRequest(title="Updated Title")
        updated = products_api.update_product(STABLE_PRODUCT_ID, update_data)

        assert updated.title == "Updated Title"

    with allure.step(f"Delete product {STABLE_PRODUCT_ID} (simulated)"):
        delete_resp = products_api.delete_product(STABLE_PRODUCT_ID)

        assert delete_resp.get("isDeleted") is True

    with allure.step("Get all products"):
        products_list = products_api.get_all_products()

        assert products_list.total > 0
        assert len(products_list.products) > 0

    with allure.step("Get product by ID"):
        product = products_api.get_product_by_id(STABLE_PRODUCT_ID)

        assert product.id == STABLE_PRODUCT_ID


@allure.story("Data-driven product creation")
def test_create_random_product(products_api):
    payload = ProductCreateRequest(
        title=fake.catch_phrase(),
        description=fake.paragraph(nb_sentences=2),
        price=round(
            fake.pyfloat(
                left_digits=2,
                right_digits=2,
                positive=True,
                min_value=1,
            ),
            2,
        ),
    )

    with allure.step(f"Create product with random data: {payload.title}"):
        product = products_api.create_product(payload)

        assert product.title == payload.title
        assert product.price == payload.price


@allure.story("Search products by query")
@pytest.mark.parametrize("query", ["Phone", "Computers", "Laptop"])
def test_search_products(products_api, query):
    with allure.step(f"Search for '{query}'"):
        response = products_api.get(
            f"/products/search?q={query}",
            expected_status=200,
        )
        data = ProductListResponse.model_validate(response.json())

        for product in data.products:
            assert (
                query.lower() in product.title.lower()
                or query.lower() in product.description.lower()
            ), f"Product {product.id} does not match search query '{query}'"


@allure.story("Filter products by category")
def test_filter_products_by_category(products_api):
    category = "smartphones"

    with allure.step(f"Request products in category: {category}"):
        data = products_api.get_products_by_category(category)

    with allure.step("Verify all returned products belong to the category"):
        assert data.total > 0, f"No products found in category {category}"

        for product in data.products:
            assert (
                product.category == category
            ), f"Product {product.id} has wrong category: {product.category}"


@allure.story("Sort products by price descending")
def test_sort_products_by_price_desc(products_api):
    params = {
        "sortBy": "price",
        "order": "desc",
    }

    with allure.step("Request products sorted by price (descending)"):
        response = products_api.get(
            "/products",
            params=params,
            expected_status=200,
        )
        data = ProductListResponse.model_validate(response.json())

    with allure.step("Verify that prices are in descending order"):
        prices = [product.price for product in data.products]

        assert prices == sorted(prices, reverse=True), (
            f"Prices are not sorted correctly: {prices}"
        )


@allure.story("Validate product list response contract integrity")
def test_products_response_contract(products_api):
    with allure.step("Request product list"):
        response = products_api.get("/products", expected_status=200)
        data = ProductListResponse.model_validate(response.json())

    with allure.step("Validate pagination metadata"):
        assert data.total >= len(data.products), (
            "Total count is less than actual number of returned products"
        )
        assert data.limit > 0, "Limit should be greater than zero"
        assert data.skip >= 0, "Skip cannot be negative"

    with allure.step("Validate each product structure"):
        for product in data.products:
            assert product.id > 0, "Product ID must be positive"
            assert product.title.strip(), "Product title cannot be empty"
            assert product.price > 0, "Product price must be positive"