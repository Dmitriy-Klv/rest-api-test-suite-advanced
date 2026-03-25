import random
import pytest
import allure
from faker import Faker
import time
from api.base_api import APIError
import threading

from api.products_api import ProductsAPI
from schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductListResponse, Product,
)

pytestmark = allure.feature("Products API")

fake = Faker()
STABLE_PRODUCT_ID = 1


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


@allure.story("Partial update should not override unspecified fields")
def test_partial_update_preserves_other_fields(products_api):
    product_id = 1

    with allure.step("Get original product data"):
        original = products_api.get_product_by_id(product_id)

    with allure.step("Update only title field"):
        update_payload = ProductUpdateRequest(title="Partial Update Title")
        updated = products_api.update_product(product_id, update_payload)

    with allure.step("Verify title updated"):
        assert updated.title == "Partial Update Title"

    with allure.step("Verify other fields remain unchanged"):
        assert updated.price == original.price
        assert updated.description == original.description


@allure.story("GET request should be idempotent and consistent")
def test_get_product_is_idempotent(products_api):
    product_id = 1

    with allure.step("First GET request"):
        first_response = products_api.get_product_by_id(product_id)

    with allure.step("Second GET request"):
        second_response = products_api.get_product_by_id(product_id)

    with allure.step("Verify responses are identical"):
        assert first_response.model_dump() == second_response.model_dump(), (
            "GET request is not idempotent — responses differ"
        )

@allure.story("Pagination consistency and data integrity")
def test_products_pagination_consistency(products_api):
    limit = 5

    with allure.step("Request first page of products"):
        first_page_response = products_api.get(
            "/products",
            params={"limit": limit, "skip": 0},
            expected_status=200,
        )
        first_page = ProductListResponse.model_validate(first_page_response.json())

    with allure.step("Request second page of products"):
        second_page_response = products_api.get(
            "/products",
            params={"limit": limit, "skip": limit},
            expected_status=200,
        )
        second_page = ProductListResponse.model_validate(second_page_response.json())

    with allure.step("Validate pagination metadata"):
        assert first_page.limit == limit
        assert second_page.limit == limit
        assert first_page.skip == 0
        assert second_page.skip == limit
        assert first_page.total == second_page.total

    with allure.step("Validate number of items per page"):
        assert len(first_page.products) <= limit
        assert len(second_page.products) <= limit

    with allure.step("Ensure no duplicated products between pages"):
        first_ids = {product.id for product in first_page.products}
        second_ids = {product.id for product in second_page.products}

        intersection = first_ids.intersection(second_ids)
        assert not intersection, f"Duplicated product IDs found: {intersection}"


@allure.story("Schema backward compatibility validation")
def test_products_schema_backward_compatibility(products_api):

    with allure.step("Request products list"):
        response = products_api.get("/products", expected_status=200)
        data = ProductListResponse.model_validate(response.json())

    with allure.step("Verify required product fields and types"):
        sample_product = data.products[0]

        expected_fields = {"id", "title", "description", "price"}
        actual_fields = set(sample_product.model_dump().keys())

        missing_fields = expected_fields - actual_fields
        assert not missing_fields, f"Missing core fields in API response: {missing_fields}"

    with allure.step("Check for unexpected schema evolution"):
        raw_product_data = response.json()["products"][0]
        model_fields = Product.model_fields.keys()

        new_fields = set(raw_product_data.keys()) - set(model_fields)
        if new_fields:
            allure.attach(
                str(new_fields),
                name="New undocumented fields detected",
                attachment_type=allure.attachment_type.TEXT
            )


@allure.story("Cross-endpoint data consistency validation")
def test_product_consistency_between_list_and_single(products_api):

    with allure.step("Get list of products"):
        response = products_api.get("/products", expected_status=200)
        products_list = ProductListResponse.model_validate(response.json())

    with allure.step("Select random product from list"):
        random_product = random.choice(products_list.products)

    with allure.step(f"Fetch same product by ID {random_product.id}"):
        product_by_id = products_api.get_product_by_id(random_product.id)

    with allure.step("Verify that both responses contain identical product data"):
        assert product_by_id.id == random_product.id
        assert product_by_id.title == random_product.title
        assert product_by_id.price == random_product.price
        assert product_by_id.description == random_product.description


@allure.story("API response time SLA validation")
def test_products_response_time(products_api):

    with allure.step("Send request and measure response time"):
        start_time = time.perf_counter()

        response = products_api.get("/products", expected_status=200)

        duration = time.perf_counter() - start_time

    with allure.step("Validate response time"):
        MAX_RESPONSE_TIME = 1.5  # seconds

        assert duration < MAX_RESPONSE_TIME, (
            f"API response time too slow: {duration:.2f}s "
            f"(expected < {MAX_RESPONSE_TIME}s)"
        )

    with allure.step("Validate response structure"):
        data = ProductListResponse.model_validate(response.json())

        assert len(data.products) > 0

@allure.story("Search should return empty result for non-existing query")
def test_search_no_results(products_api):

    query = "asdkfjhasdkjfhaskdjfh"

    with allure.step(f"Search for non-existing query: {query}"):
        response = products_api.get(
            f"/products/search?q={query}",
            expected_status=200
        )

        data = ProductListResponse.model_validate(response.json())

    with allure.step("Verify search returns empty results"):
        assert data.total == 0 or len(data.products) == 0, (
            f"Expected no results for query '{query}', but got {len(data.products)}"
        )


@allure.story("Negative: Validation of field types during product creation")
def test_create_product_invalid_types(products_api):

    invalid_payload = {
        "title": "Invalid Product",
        "description": "Testing type mismatch",
        "price": "string_instead_of_number"
    }

    with allure.step("Send POST request with invalid 'price' type"):
        with pytest.raises(APIError) as excinfo:
            products_api.post("/products/add", json=invalid_payload, expected_status=400)

        assert "400" in str(excinfo.value), f"Expected status code 400 in APIError, but got: {excinfo.value}"


@allure.story("Negative: Request non-existing product")
def test_get_non_existing_product(products_api):

    non_existing_id = 999999

    with allure.step(f"Request product with non-existing ID {non_existing_id}"):

        response = products_api.get(
            f"/products/{non_existing_id}",
            expected_status=404
        )

    with allure.step("Verify API returns 404 status"):
        assert response.status_code == 404

@allure.story("Data mutation safety between resources")
def test_product_update_does_not_affect_other_products(products_api):

    first_product_id = 1
    second_product_id = 2

    with allure.step("Fetch original data for both products"):
        first_product_original = products_api.get_product_by_id(first_product_id)
        second_product_original = products_api.get_product_by_id(second_product_id)

    with allure.step("Update first product title"):
        update_payload = ProductUpdateRequest(title="Isolation Test Title")
        updated_first_product = products_api.update_product(first_product_id, update_payload)

    with allure.step("Fetch second product again after update"):
        second_product_after = products_api.get_product_by_id(second_product_id)

    with allure.step("Verify first product was updated"):
        assert updated_first_product.title == "Isolation Test Title"

    with allure.step("Verify second product remained unchanged"):
        assert second_product_after.model_dump() == second_product_original.model_dump(), (
            "Update of one product unexpectedly affected another product"
        )


@allure.story("Advanced Search: Contextual filtering within category")
def test_search_within_category_context(products_api):

    with allure.step("Pre-condition: Get a real product to define search criteria"):
        all_products = products_api.get_all_products()
        target_product = all_products.products[0]
        category = target_product.category
        search_query = target_product.title.split()[0]

    with allure.step(f"Search for '{search_query}' specifically in category '{category}'"):
        results = products_api.search_products(query=search_query)

    with allure.step("Verify search results integrity"):
        assert results.total > 0, f"Should find at least one product for query '{search_query}'"

        for product in results.products:
            assert search_query.lower() in product.title.lower(), \
                f"Product {product.id} does not contain search query in title"

            if product.id == target_product.id:
                assert product.category == category, \
                    f"Product {product.id} changed category in search results!"


@allure.story("Delete operation simulation validation")
def test_delete_product_response(products_api):

    product_id = 1

    with allure.step(f"Delete product {product_id}"):

        response = products_api.delete_product(product_id)

    with allure.step("Verify delete response structure"):

        assert response["id"] == product_id
        assert response["isDeleted"] is True
        assert "deletedOn" in response



@allure.story("Search products across multiple categories simultaneously")
def test_search_products_multiple_categories(products_api: ProductsAPI):
    categories_to_search = ["smartphones", "laptops", "home-decoration"]

    found_products = []

    for category in categories_to_search:
        with allure.step(f"Fetch products in category: {category}"):
            response: ProductListResponse = products_api.get_products_by_category(category)
            found_products.extend(response.products)

    with allure.step("Verify all returned products belong to one of the searched categories"):
        assert len(found_products) > 0, "No products found across the selected categories"

        for product in found_products:
            assert product.category in categories_to_search, (
                f"Product {product.id} belongs to unexpected category: {product.category}"
            )

    with allure.step("Optional: Attach product IDs for reference"):
        product_ids = [p.id for p in found_products]
        allure.attach(str(product_ids), name="Found Product IDs", attachment_type=allure.attachment_type.TEXT)



@allure.story("Concurrency: Simulated concurrent updates")
def test_concurrent_product_updates(products_api):
    product_id = 1

    update_titles = [
        "Concurrent Title 1",
        "Concurrent Title 2",
        "Concurrent Title 3",
        "Concurrent Title 4",
    ]

    results = []

    def update_product(title):
        payload = ProductUpdateRequest(title=title)
        updated = products_api.update_product(product_id, payload)
        results.append(updated.title)

    threads = []

    with allure.step("Run concurrent updates"):
        for title in update_titles:
            t = threading.Thread(target=update_product, args=(title,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    with allure.step("Validate all responses"):
        assert len(results) == len(update_titles)

        for title in results:
            assert title in update_titles


@allure.story("Pagination: Full dataset integrity validation")
def test_products_full_pagination_integrity(products_api):
    limit = 10
    all_products = []
    seen_ids = set()
    skip = 0

    with allure.step("Fetch all products page by page"):
        while True:
            response = products_api.get(
                "/products",
                params={"limit": limit, "skip": skip},
                expected_status=200,
            )

            data = ProductListResponse.model_validate(response.json())

            if not data.products:
                break

            for product in data.products:
                all_products.append(product)

                assert product.id not in seen_ids, (
                    f"Duplicate product detected during pagination: {product.id}"
                )
                seen_ids.add(product.id)

            skip += limit

    with allure.step("Validate total count matches collected data"):
        assert len(all_products) == data.total, (
            f"Mismatch in total products: collected={len(all_products)}, expected={data.total}"
        )

    with allure.step("Validate no data loss across pagination"):
        assert len(seen_ids) == len(all_products), (
            "Data inconsistency: duplicate IDs found or products lost"
        )


@allure.story("Boundary: Accept large product price")
def test_product_large_price(products_api):

    payload = ProductCreateRequest(
        title="Expensive Product",
        description="High price test",
        price=10**9
    )

    with allure.step("Create product with very large price"):
        product = products_api.create_product(payload)

    with allure.step("Verify API accepts large price values"):
        assert product.price == 10**9


@allure.story("Consistency: Dummy API does not persist data")
def test_product_update_is_not_persisted(products_api):
    product_id = 1
    new_title = f"Test {random.randint(1000, 9999)}"

    with allure.step("Update product"):
        updated = products_api.update_product(
            product_id,
            ProductUpdateRequest(title=new_title)
        )

        assert updated.title == new_title

    with allure.step("Fetch product again"):
        fetched = products_api.get_product_by_id(product_id)

    with allure.step("Verify data is NOT persisted (expected behavior)"):
        assert fetched.title != new_title, (
            "Dummy API unexpectedly persisted data"
        )