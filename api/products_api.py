from api.base_api import BaseAPI
from schemas.product_schema import (
    ProductListResponse, Product, ProductCreateRequest, ProductUpdateRequest
)


class ProductsAPI(BaseAPI):

    def get_all_products(self) -> ProductListResponse:
        response = self.get("/products", expected_status=200)
        return ProductListResponse.model_validate(response.json())

    def get_product_by_id(self, product_id: int) -> Product:
        response = self.get(f"/products/{product_id}", expected_status=200)
        return Product.model_validate(response.json())

    def create_product(self, product_data: ProductCreateRequest) -> Product:
        response = self.post("/products/add", json=product_data.model_dump(), expected_status=201)
        return Product.model_validate(response.json())

    def update_product(self, product_id: int, product_data: ProductUpdateRequest) -> Product:
        response = self.put(
            f"/products/{product_id}",
            json=product_data.model_dump(exclude_unset=True),
            expected_status=200
        )
        return Product.model_validate(response.json())

    def delete_product(self, product_id: int) -> dict:
        response = self.delete(f"/products/{product_id}", expected_status=200)
        return response.json()

    def get_products_by_category(self, category_name: str) -> ProductListResponse:
        response = self.get(f"/products/category/{category_name}", expected_status=200)
        return ProductListResponse.model_validate(response.json())