from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page, Playwright
from pytest_bdd import given, parsers, scenarios, then, when

from src.api.auth import login_via_api
from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage
from src.pages.logout_page import LogoutPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "logout.feature"))

# Ways of logging out: label used in the feature file ➤ action on the (logged-in) Account Dashboard
LOGOUT_METHODS = {
    "Account Dashboard side menu: Logoff": lambda page: page.click_logoff(),
    "ACCOUNT menu: LOGOUT": lambda page: page.click_logout_from_account_menu(),
    "welcome message menu: Logoff": lambda page: page.click_logoff_from_welcome_menu(),
    "footer: Logoff": lambda page: page.click_logoff_from_footer(),
}


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def own_session_page(playwright: Playwright, base_url: str, new_context, auth_session) -> Iterator[Page]:
    """
    A page logged in with its OWN session (a separate API login for every test).

    NOTE FOR ME: NIE używamy tu `logged_in_page`, bo ten korzysta z sesji współdzielonej przez wszystkie testy
    (`auth_session`). Wylogowanie kończy sesję po stronie serwera, więc mogłoby wylogować kolejne testy.
    """
    state = login_via_api(playwright, base_url)
    yield new_context(storage_state=state).new_page()

    # Safeguard: if the server ended ALL sessions of the account, refresh the shared one for the following tests
    # (when it did not, this is just one extra API request)
    auth_session.refresh()


@pytest.fixture
def account_dashboard_page(own_session_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(own_session_page)


@pytest.fixture
def logout_page(own_session_page: Page) -> LogoutPage:
    return LogoutPage(own_session_page)


@pytest.fixture
def home_page(own_session_page: Page) -> HomePage:
    return HomePage(own_session_page)


@pytest.fixture
def login_page(own_session_page: Page) -> LoginPage:
    return LoginPage(own_session_page)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and is on the Account Dashboard")
def customer_is_logged_in_on_account_dashboard(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.open()
    account_dashboard_page.expect_loaded()
    account_dashboard_page.expect_logged_in()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when(parsers.parse('the customer logs out using "{method}"'))
def customer_logs_out_using(account_dashboard_page: AccountDashboardPage, method: str) -> None:
    LOGOUT_METHODS[method](account_dashboard_page)


@when("the customer clicks Continue on the Account Logout page")
def click_continue_on_logout_page(logout_page: LogoutPage) -> None:
    logout_page.click_continue()


@when("the customer hovers over the ACCOUNT menu")
def hover_over_account_menu(home_page: HomePage) -> None:
    home_page.hover_account_menu()


@when("the customer goes back in the browser")
def go_back_in_browser(logout_page: LogoutPage) -> None:
    logout_page.go_back()


@when("the customer opens the Account Dashboard directly")
def open_account_dashboard_directly(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.open()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the Account Logout page is displayed with the confirmation messages")
def account_logout_page_is_displayed(logout_page: LogoutPage) -> None:
    logout_page.expect_logout_confirmed()


@then("the home page is displayed in the logged-out state")
def home_page_is_displayed_logged_out(home_page: HomePage) -> None:
    home_page.expect_root_url()  # Continue leads to the store root
    home_page.expect_loaded()
    home_page.expect_logged_out()


@then("the LOGIN option is displayed in the ACCOUNT menu")
def login_option_is_displayed_in_account_menu(home_page: HomePage) -> None:
    home_page.expect_login_link_visible()


@then("the LOGOUT option is not displayed in the ACCOUNT menu")
def logout_option_is_not_displayed_in_account_menu(home_page: HomePage) -> None:
    home_page.expect_logout_link_absent()


@then("the Login page is displayed")
def login_page_is_displayed(login_page: LoginPage) -> None:
    login_page.expect_loaded()


@then("the customer is not logged in")
def customer_is_not_logged_in(login_page: LoginPage) -> None:
    login_page.expect_logged_out()

# endregion
# ==========================================================================================================
