import pytest
from api.products_api import ProductsAPI


@pytest.fixture(scope="session")
def products_api():
    return ProductsAPI()