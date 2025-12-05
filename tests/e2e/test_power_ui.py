import pytest
import requests
from uuid import uuid4
from playwright.sync_api import Page


def _build_unique_user() -> dict:
    suffix = uuid4().hex[:8]
    return {
        "first_name": "Power",
        "last_name": "Tester",
        "email": f"power.{suffix}@example.com",
        "username": f"power_user_{suffix}",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!"
    }


def register_user(base_url: str) -> dict:
    payload = _build_unique_user()
    response = requests.post(f"{base_url}/auth/register", json=payload)
    assert response.status_code == 201, f"User registration failed: {response.text}"
    return payload


def login_via_ui(page: Page, base_url: str, user: dict) -> None:
    page.goto(f"{base_url}/login")
    page.fill('#username', user['username'])
    page.fill('#password', user['password'])
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/dashboard", timeout=5000)
    page.wait_for_selector('#calculationForm')


@pytest.mark.e2e
def test_power_calculation_ui(page: Page, fastapi_server: str) -> None:
    base_url = fastapi_server.rstrip('/')
    user = register_user(base_url)
    login_via_ui(page, base_url, user)

    page.select_option('#calcType', 'power')
    page.fill('#calcBase', '2')
    page.fill('#calcExponent', '5')
    page.click('button[type="submit"]')

    page.wait_for_selector('#successAlert:not(.hidden)', timeout=5000)
    page.wait_for_selector('#calculationsTable tr:has-text("Power")', timeout=5000)

    row = page.locator('#calculationsTable tr:has-text("Power")').first
    assert row.locator('td').nth(0).inner_text().strip() == 'Power'
    assert 'Base: 2, Exponent: 5' in row.locator('td').nth(1).inner_text()

    result_text = row.locator('td').nth(2).inner_text().strip()
    assert float(result_text) == 32.0


@pytest.mark.e2e
def test_power_calculation_ui_invalid_input(page: Page, fastapi_server: str) -> None:
    base_url = fastapi_server.rstrip('/')
    user = register_user(base_url)
    login_via_ui(page, base_url, user)

    page.select_option('#calcType', 'power')
    page.fill('#calcBase', '4')
    # Leave exponent blank to trigger validation
    page.click('button[type="submit"]')

    page.wait_for_selector('#errorAlert:not(.hidden)', timeout=5000)
    error_text = page.locator('#errorMessage').inner_text()
    assert 'valid base and exponent' in error_text.lower()
    assert page.locator('#calculationsTable tr:has-text("Power")').count() == 0
