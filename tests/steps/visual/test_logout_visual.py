from pathlib import Path

from pytest_bdd import given, scenarios, then, when
from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.home_page import HomePage
from src.pages.logout_page import LogoutPage
# NOTE FOR ME: Fixture z test_logout.py importujemy, bo w pytest-bdd fixture z innego modułu nie jest widoczny.
# Ważne: `own_session_page` ma własną sesję i po teście odświeża współdzieloną (auth_session). Dzięki temu
# wylogowanie w testach wizualnych nie wylogowuje kolejnych testów. NIE używamy `logged_in_page`.
# Kroki (Given/When) definiujemy tu od nowa, bo kroki z innego modułu też nie są widoczne.
from tests.steps.test_logout import (  # noqa: F401
    account_dashboard_page,
    home_page,
    logout_page,
    own_session_page,
)

scenarios(str(Path(__file__).resolve().parents[2] / "features" / "visual" / "logout_visual.feature"))


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

@when("the customer logs out using the Account Dashboard side menu")
def customer_logs_out_using_side_menu(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.click_logoff()


@when("the customer clicks Continue on the Account Logout page")
def click_continue_on_logout_page(logout_page: LogoutPage) -> None:
    logout_page.expect_loaded()
    logout_page.click_continue()


@when("the customer hovers over the ACCOUNT menu")
def hover_over_account_menu(home_page: HomePage) -> None:
    # NOTE FOR ME: Czekamy na stronę główną w stanie wylogowanym, dopiero potem hover (inaczej menu bywa nieotwarte)
    home_page.expect_loaded()
    home_page.expect_logged_out()
    home_page.hover_account_menu()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the Account Logout heading matches the visual snapshot")
def logout_heading_snapshot(logout_page: LogoutPage, assert_snapshot: AssertSnapshot) -> None:
    logout_page.expect_heading_matches_snapshot(assert_snapshot, "logout_heading")


@then("the Account Logout messages with the Continue button match the visual snapshot")
def logout_content_snapshot(logout_page: LogoutPage, assert_snapshot: AssertSnapshot) -> None:
    logout_page.expect_content_matches_snapshot(assert_snapshot, "logout_content")


@then("the ACCOUNT menu matches the visual snapshot")
def account_menu_snapshot(home_page: HomePage, assert_snapshot: AssertSnapshot) -> None:
    home_page.expect_account_menu_matches_snapshot(assert_snapshot, "logout_account_menu_logged_out")

# endregion
# ==========================================================================================================
