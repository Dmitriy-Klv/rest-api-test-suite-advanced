# REST API Test Suite Advanced

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/framework-pytest-0f0?logo=pytest)](https://pytest.org/)
[![Pydantic](https://img.shields.io/badge/validation-Pydantic--v2-red)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Overview
Advanced API test automation framework designed for the [DummyJSON](https://dummyjson.com/) ecosystem. This project demonstrates professional-grade engineering practices in Quality Assurance, focusing on scalable architecture, strict data contracts, and secure authentication flows.

**API Notice:** DummyJSON is a fake REST API for JSON data for development and testing purposes, provided as a publicly accessible service. No personal information is collected or distributed. (Documentation: [https://dummyjson.com](https://dummyjson.com))


---

## 🏗 Key Engineering Features

* **Modular Test Architecture:** Clean separation between API layer, schema validation, and test scenarios to ensure maintainability and scalability.

* **Schema-Based Contract Validation:** API responses are validated using **Pydantic v2 models**, ensuring strict response contracts.

* **Authentication Handling:** Automated JWT authentication flow with session reuse across requests.

* **Structured Logging:** Custom logging with automatic masking of sensitive data such as tokens, emails and passwords.

* **Allure Reporting:** Detailed test execution reports with step-level visibility.

* **CI/CD Integration:** Automated test execution through GitHub Actions pipeline.

---

## 🛠 Tech Stack
* **Core:** Python 3.10+
* **Test Engine:** `pytest`
* **Data Validation:** `Pydantic v2`
* **HTTP Client:** `requests`
* **Configuration:** `python-dotenv`

---

## 🚀 Installation, Environment & Running Tests

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/rest-api-test-suite-advanced.git](https://github.com/YourUsername/rest-api-test-suite-advanced.git)
   cd rest-api-test-suite-advanced

   cd rest-api-test-suite-advanced
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   Activate the virtual environment:
   ```
* Linux/macOS:
   ```bash
   source venv/bin/activate
   ```
   * Windows (PowerShell):

   ```bash
   venv\Scripts\activate
   ```
* Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. **Configure environment variables:**
Create a .env file in the project root with the following content:
   ```bash
   BASE_URL=https://dummyjson.com
   LOG_LEVEL=INFO
   ```

7. **Run all tests using pytest:**
   ```bash
   pytest -v
   ```
8. **Generate and view Allure reports:**
   ```bash
   pytest -v --alluredir=allure-results
   allure serve allure-results
   ```
