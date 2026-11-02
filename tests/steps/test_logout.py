import re
from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, scenarios, then, when

from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.home_page import HomePage
from src.pages.logout_page import LogoutPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "logout.feature"))


# FIXTURES

@pytest.fixture
def account_dashboard_page(logged_in_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_page)


@pytest.fixture
def logout_page(logged_in_page: Page) -> LogoutPage:
    return LogoutPage(logged_in_page)


@pytest.fixture
def home_page(logged_in_page: Page) -> HomePage:
    return HomePage(logged_in_page)


# GIVEN

@given("the customer is logged in and is on the Account Dashboard")
def customer_is_logged_in_on_account_dashboard(
        account_dashboard_page: AccountDashboardPage,
) -> None:
    account_dashboard_page.open()
    account_dashboard_page.expect_loaded()
    account_dashboard_page.expect_logged_in()


# WHEN

@when("the customer clicks Logoff in the Account Dashboard side menu")
def click_logoff_in_side_menu(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.click_logoff()


@when("the customer clicks LOGOUT in the ACCOUNT menu")
def click_logout_in_account_menu(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.click_logout_from_account_menu()


@when("the customer clicks Continue on the Account Logout page")
def click_continue_on_logout_page(logout_page: LogoutPage) -> None:
    logout_page.click_continue()


@when("the customer hovers over the ACCOUNT menu")
def hover_over_account_menu(home_page: HomePage) -> None:
    home_page.hover_account_menu()


# THEN

@then("the Account Logout page is displayed with the confirmation messages")
def account_logout_page_is_displayed(logout_page: LogoutPage) -> None:
    logout_page.expect_logout_confirmed()


@then("the home page is displayed in the logged-out state")
def home_page_is_displayed_logged_out(home_page: HomePage) -> None:
    home_page.expect_loaded()

    # The Continue button should return the browser to the store root.
    home_page.page.wait_for_url(re.compile(r"https?://[^/]+/?$"))

    home_page.expect_logged_out()


@then("the LOGIN option is displayed in the ACCOUNT menu")
def login_option_is_displayed_in_account_menu(home_page: HomePage) -> None:
    home_page.expect_login_link_visible()
