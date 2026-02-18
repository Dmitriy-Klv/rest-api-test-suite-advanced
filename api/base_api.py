import json
import logging
import random
import time
from typing import Any, Dict, Optional

import requests

from utils.config import settings

logger = logging.getLogger(__name__)


class APIError(Exception):
    pass


class BaseAPI:
    SENSITIVE_HEADERS = {"Authorization", "Cookie", "Set-Cookie", "X-Api-Key", "Token"}
    SENSITIVE_DATA_KEYS = {
        "email",
        "phone",
        "password",
        "address",
        "zipcode",
        "street",
        "city",
        "iban",
        "bic",
        "birthday",
    }

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.BASE_API_URL).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "REST-API-Test-Suite-Advanced/1.0",
            }
        )

    def _mask_headers(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        masked = dict(headers)
        for header in masked:
            if any(
                sensitive.lower() == header.lower()
                for sensitive in self.SENSITIVE_HEADERS
            ):
                masked[header] = "********"
        return masked

    def _mask_body(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: (
                    "********"
                    if k.lower() in self.SENSITIVE_DATA_KEYS
                    else self._mask_body(v)
                )
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._mask_body(item) for item in data]
        return data

    def _send_request(
        self,
        method: str,
        endpoint: str,
        expected_status: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", settings.REQUEST_TIMEOUT)

        delay = random.uniform(0.1, 0.8)
        time.sleep(delay)

        logger.info(f"Sending {method} request to: {url} after {delay:.2f}s delay")

        try:
            response = self.session.request(method, url, **kwargs)
            logger.info(f"Received response: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            raise APIError(f"Could not connect to API: {e}")

        if expected_status and response.status_code != expected_status:
            raise APIError(
                f"Expected status {expected_status}, got {response.status_code}. "
                f"Response body: {response.text}"
            )

        return response

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._send_request("GET", endpoint, **kwargs)

    def post(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> requests.Response:
        return self._send_request("POST", endpoint, json=json, **kwargs)

    def put(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> requests.Response:
        return self._send_request("PUT", endpoint, json=json, **kwargs)

    def patch(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> requests.Response:
        return self._send_request("PATCH", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._send_request("DELETE", endpoint, **kwargs)
