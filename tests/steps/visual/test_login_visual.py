from pathlib import Path

from playwright.sync_api import Page
from pytest_bdd import given, scenarios, then, when
from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

from src.pages.login_page import LoginPage

# NOTE FOR ME: Z test_login.py nie importujemy nic. Krok "the user opens the login page" tworzy tam fixture
# `login_page` przez target_fixture, a taki fixture nie jest zwykłą funkcją do zaimportowania. Dlatego krok Given
# definiujemy tutaj od nowa (bez `captured_dialogs`, bo testy wizualne nie sprawdzają okienek JS).
# Strona logowania jest dla gościa, więc nie potrzeba logowania ani sprzątania po teście.

scenarios(str(Path(__file__).resolve().parents[2] / "features" / "visual" / "login_visual.feature"))

# ==========================================================================================================
# region TEST DATA
# ==========================================================================================================

# NOTE FOR ME: Celowo NIE używamy prawdziwego loginu z .env. Błędne dane nie zwiększają licznika nieudanych prób
# logowania na prawdziwym koncie, a komunikat błędu jest zawsze ten sam, więc screeny się zgadzają.
FIXED_WRONG_LOGIN_NAME = "wrong_login_name"
FIXED_WRONG_PASSWORD = "wrong_password"


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the user opens the login page", target_fixture="login_page")
def open_login_page(page: Page) -> LoginPage:
    login_page = LoginPage(page)
    login_page.open()
    login_page.expect_loaded()
    return login_page


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the user submits the fixed wrong credentials")
def submit_fixed_wrong_credentials(login_page: LoginPage) -> None:
    login_page.login(FIXED_WRONG_LOGIN_NAME, FIXED_WRONG_PASSWORD)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the returning customer section matches the visual snapshot")
def returning_customer_snapshot(login_page: LoginPage, assert_snapshot: AssertSnapshot) -> None:
    login_page.expect_returning_customer_matches_snapshot(assert_snapshot, "login_returning_customer")


@then("the new customer section matches the visual snapshot")
def new_customer_snapshot(login_page: LoginPage, assert_snapshot: AssertSnapshot) -> None:
    login_page.expect_new_customer_matches_snapshot(assert_snapshot, "login_new_customer")


@then("the login error alert matches the visual snapshot")
def login_error_alert_snapshot(login_page: LoginPage, assert_snapshot: AssertSnapshot) -> None:
    login_page.expect_error_alert_matches_snapshot(assert_snapshot, "login_error_alert")


@then("the returning customer section with the login error matches the visual snapshot")
def returning_customer_with_error_snapshot(login_page: LoginPage, assert_snapshot: AssertSnapshot) -> None:
    login_page.expect_returning_customer_matches_snapshot(assert_snapshot, "login_returning_customer_error")

# endregion
# ==========================================================================================================
