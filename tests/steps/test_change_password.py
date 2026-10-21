import secrets
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Playwright, Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.api.auth import login_via_api
from src.configuration.config import get_account_password
from src.pages.account.account_change_password_page import AccountChangePasswordPage
from src.pages.account.account_dashboard_page import AccountDashboardPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "change_password.feature"))

# NOTE FOR ME: Znaczniki __X__ zamieniamy na prawdziwe wartości (pusta wartość w Examples nie przejdzie
# przez parsers.parse("{value}"), a hasło z .env nie może leżeć w pliku .feature).
LONG_PASSWORD = "P" * 21
WRONG_PASSWORD = "DefinitelyWrong123!"


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def account_dashboard_page(logged_in_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_page)


@pytest.fixture
def change_password_page(logged_in_page: Page) -> AccountChangePasswordPage:
    return AccountChangePasswordPage(logged_in_page)


@pytest.fixture
def original_password() -> str:
    """The password from .env, i.e. the state the account should have before and after every scenario."""
    return get_account_password()


@pytest.fixture
def generated_password() -> str:
    """
    New password for the positive scenario (the site accepts 4-20 characters).
    Generated once per test, so the steps and the cleanup fixture use the same value.
    """
    return "Qa@" + secrets.token_hex(5)


@pytest.fixture
def restore_original_password(
        playwright: Playwright,
        base_url: str,
        new_context,
        original_password: str,
        generated_password: str,
) -> Iterator[None]:
    """
    [CLEANUP] Safety net: guarantees that the account ends with the .env password, even when the scenario
    failed between "change" and "restore" (otherwise every later test would fail on API login).

    NOTE FOR ME: Sprawdzamy stan przez API, a nie przez UI - to działa niezależnie od tego, w którym kroku
    padł test. Błąd sprzątania nie może zamaskować błędu testu, więc zamiast wyjątku jest ostrzeżenie.
    """
    yield

    try:
        login_via_api(playwright, base_url)  # original password works -> nothing to restore
        return
    except RuntimeError:
        pass

    try:
        state = login_via_api(playwright, base_url, password=generated_password)
        page = new_context(storage_state=state).new_page()
        change_password_page = AccountChangePasswordPage(page)
        change_password_page.open()
        change_password_page.expect_loaded()
        change_password_page.change_password(generated_password, original_password)
        AccountDashboardPage(page).expect_password_updated_alert()
    except Exception as exc:  # noqa: BLE001 - teardown must not mask a test failure
        warnings.warn(
            f"Password cleanup FAILED: {exc}. The account may still have the generated password "
            f"'{generated_password}' - restore it manually to the .env value.",
            stacklevel=2,
        )


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region HELPERS
# ==========================================================================================================

def resolve_password(value: str, original_password: str) -> str:
    markers = {
        "__CURRENT__": original_password,
        "__WRONG__": WRONG_PASSWORD,
        "__LONG_21__": LONG_PASSWORD,
        "__EMPTY__": "",
    }
    return markers.get(value, value)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and opens Change password from the account dashboard")
def open_change_password_from_dashboard(
        account_dashboard_page: AccountDashboardPage,
        change_password_page: AccountChangePasswordPage,
        restore_original_password: None,
) -> None:
    account_dashboard_page.open()
    account_dashboard_page.expect_loaded()
    account_dashboard_page.click_quick_link("Change password")
    change_password_page.expect_loaded()


@given("the customer is logged in and opens Change password")
def open_change_password(change_password_page: AccountChangePasswordPage) -> None:
    change_password_page.open()
    change_password_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the customer changes the password to a generated new password")
def change_to_generated_password(
        change_password_page: AccountChangePasswordPage,
        original_password: str,
        generated_password: str,
) -> None:
    change_password_page.change_password(original_password, generated_password)


@when("the customer opens Change password again")
def reopen_change_password(
        account_dashboard_page: AccountDashboardPage,
        change_password_page: AccountChangePasswordPage,
) -> None:
    account_dashboard_page.expect_loaded()
    account_dashboard_page.click_quick_link("Change password")
    change_password_page.expect_loaded()


@when("the customer restores the original password from the environment")
def restore_original(
        change_password_page: AccountChangePasswordPage,
        generated_password: str,
        original_password: str,
) -> None:
    change_password_page.change_password(generated_password, original_password)


@when(parsers.parse(
    'the customer submits the password change with current password "{current}", '
    'new password "{new}" and confirmation "{confirm}"'
))
def submit_password_change(
        change_password_page: AccountChangePasswordPage,
        original_password: str,
        current: str,
        new: str,
        confirm: str,
) -> None:
    change_password_page.change_password(
        resolve_password(current, original_password),
        resolve_password(new, original_password),
        resolve_password(confirm, original_password),
    )


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the account dashboard confirms the password was successfully updated")
def password_change_success(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.expect_loaded()
    account_dashboard_page.expect_password_updated_alert()


@then("the customer can log in with the new password")
def can_log_in_with_new_password(
        playwright: Playwright, base_url: str, generated_password: str,
) -> None:
    # NOTE FOR ME: Nowy kontekst API (bez cookies przeglądarki) - raise RuntimeError, jeśli logowanie się nie uda.
    login_via_api(playwright, base_url, password=generated_password)


@then("the customer can log in with the original password")
def can_log_in_with_original_password(playwright: Playwright, base_url: str) -> None:
    login_via_api(playwright, base_url)


@then("the password change form stays open with an error alert")
def password_change_error_alert(change_password_page: AccountChangePasswordPage) -> None:
    change_password_page.expect_loaded()
    change_password_page.expect_error_alert()


@then(parsers.parse('the password change form displays the error "{message}" for "{field}"'))
def password_field_error(change_password_page: AccountChangePasswordPage, message: str, field: str) -> None:
    change_password_page.expect_field_error(field, message)

# endregion
# ==========================================================================================================
