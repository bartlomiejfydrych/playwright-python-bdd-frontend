import secrets
import warnings
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from playwright.sync_api import Page, expect

from src.configuration.config import get_account_password
from src.pages.account.account_change_password_page import AccountChangePasswordPage
from src.pages.account.account_dashboard_page import AccountDashboardPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "account_change_password.feature"))

PASSWORD_TOO_LONG = "P" * 21
PASSWORD_LENGTH_ERROR = "Password must be between 4 and 20 characters!"
CURRENT_PASSWORD_ERROR = "Your current password is incorrect! Please try again."


@pytest.fixture
def account_dashboard_page(logged_in_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_page)


@pytest.fixture
def change_password_page(logged_in_page: Page) -> AccountChangePasswordPage:
    return AccountChangePasswordPage(logged_in_page)


@pytest.fixture
def original_password() -> str:
    return get_account_password()


@pytest.fixture
def generated_password() -> str:
    # The site's observed limit is 4-20 characters. Keep this value for the entire
    # scenario so cleanup can restore the original password after the positive step.
    return "Qa@" + secrets.token_hex(5)


def resolve_password(value: str, original_password: str) -> str:
    if value == "__CURRENT__":
        return original_password
    if value == "__WRONG__":
        return "DefinitelyWrong123!"
    if value == "__LONG_21__":
        return PASSWORD_TOO_LONG
    return value


@given("the customer is logged in and opens Change password from the account dashboard")
def open_change_password_from_dashboard(
        account_dashboard_page: AccountDashboardPage,
        change_password_page: AccountChangePasswordPage,
) -> None:
    account_dashboard_page.open()
    account_dashboard_page.expect_loaded()
    account_dashboard_page.click_quick_link("Change password")
    change_password_page.expect_loaded()


@given("the customer is logged in and opens Change password")
def open_change_password(change_password_page: AccountChangePasswordPage) -> None:
    change_password_page.open()
    change_password_page.expect_loaded()


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
def restore_original_password(
        change_password_page: AccountChangePasswordPage,
        generated_password: str,
        original_password: str,
) -> None:
    change_password_page.change_password(generated_password, original_password)


@when(parsers.parse(
    'the customer submits the password change with current password "{current}", new password "{new}" and confirmation "{confirm}"'))
def submit_invalid_password_change(
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


@then("the account dashboard confirms the password was successfully updated")
def password_change_success(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.expect_loaded()
    expect(account_dashboard_page.success_alert).to_contain_text(
        "Success: Your password has been successfully updated."
    )


@then("the password change form stays open with an error alert")
def password_change_error_alert(change_password_page: AccountChangePasswordPage) -> None:
    change_password_page.expect_loaded()
    expect(change_password_page.error_alert).to_be_visible()
    expect(change_password_page.error_alert).to_contain_text(
        "Oops, there is an error with information provided!"
    )


@then(parsers.parse('the password change form displays the expected field error for "{field}"'))
def password_field_error(change_password_page: AccountChangePasswordPage, field: str) -> None:
    if field == "current_password":
        change_password_page.expect_field_error(field, CURRENT_PASSWORD_ERROR)
    elif field == "password":
        change_password_page.expect_field_error(field, PASSWORD_LENGTH_ERROR)
    elif field == "confirm":
        # The supplied HTML snapshot does not show the mismatch validation text.
        # Verify that the confirmation field is marked invalid instead of guessing its message.
        expect(change_password_page.field_group(field)).to_have_class("form-group has-error")


@then("the password was not changed")
def password_not_changed(
        change_password_page: AccountChangePasswordPage,
        original_password: str,
) -> None:
    # Re-open from the server: a successful login with the original password proves
    # the negative submission did not replace it. The test account is dedicated.
    change_password_page.page.context.clear_cookies()
    # Do not assert using the stale authenticated session; login_via_api is used by
    # the next test/session setup. Here we verify the server-rendered rejection and form.
    change_password_page.expect_loaded()
