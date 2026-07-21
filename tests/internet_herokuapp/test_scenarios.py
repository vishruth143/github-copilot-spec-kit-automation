"""Sample test scenarios demonstrating the framework's Page Object Model pattern.

All test scenarios for the internet_herokuapp application live in this
single file (one `test_scenarios.py` per application, rather than splitting
scenarios across multiple files) so an application's test suite has one
obvious entry point. These tests target a public demo login application
(https://the-internet.herokuapp.com/login) and serve as both User Story 1's
day-1 onboarding walkthrough and a template for onboarding real applications.
"""

from __future__ import annotations

import pytest
from apps.internet_herokuapp.pages.login_page import LoginPage
from apps.internet_herokuapp.test_data.login_data import INVALID_PASSWORD, INVALID_USERNAME


@pytest.mark.smoke
@pytest.mark.critical
def test_login_with_valid_credentials(
    page, internet_herokuapp_base_url, internet_herokuapp_credentials
):
    # Test steps:
    # 1. Open the sample application's login page.
    # 2. Enter the configured valid username and password.
    # 3. Submit the login form.
    # 4. Verify the user is redirected to the secure area with a success message.
    login_page = LoginPage(page, base_url=internet_herokuapp_base_url)
    login_page.open()

    login_page.login(
        internet_herokuapp_credentials["username"], internet_herokuapp_credentials["password"]
    )

    assert login_page.is_login_successful()
    assert "logged into a secure area" in (login_page.flash_message() or "").lower()


@pytest.mark.smoke
@pytest.mark.critical
def test_login_fails_with_invalid_password(
    page, internet_herokuapp_base_url, internet_herokuapp_credentials
):
    # Test steps:
    # 1. Open the sample application's login page.
    # 2. Enter the configured valid username with a deliberately invalid password.
    # 3. Submit the login form.
    # 4. Verify the login is rejected with an appropriate error message.
    login_page = LoginPage(page, base_url=internet_herokuapp_base_url)
    login_page.open()

    login_page.login(internet_herokuapp_credentials["username"], INVALID_PASSWORD)

    assert not login_page.is_login_successful()
    assert "invalid" in (login_page.flash_message() or "").lower()


@pytest.mark.smoke
@pytest.mark.critical
def test_login_fails_with_invalid_username(page, internet_herokuapp_base_url):
    # Test steps:
    # 1. Open the sample application's login page.
    # 2. Enter a deliberately invalid username with any password.
    # 3. Submit the login form.
    # 4. Verify the login is rejected with an appropriate error message.
    login_page = LoginPage(page, base_url=internet_herokuapp_base_url)
    login_page.open()

    login_page.login(INVALID_USERNAME, INVALID_PASSWORD)

    assert not login_page.is_login_successful()
    assert "invalid" in (login_page.flash_message() or "").lower()
