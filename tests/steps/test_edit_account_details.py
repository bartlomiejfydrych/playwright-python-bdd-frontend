import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from src.configuration.config import (
    get_account_e_mail,
    get_account_fax,
    get_account_first_name,
    get_account_last_name,
    get_account_login_name,
    get_account_telephone,
)
from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.account.account_edit_account_details_page import AccountEditAccountDetailsPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "account_edit.feature"))

ACCOUNT_FIELDS = ("firstname", "lastname", "email", "telephone", "fax")
LONG_VALUE = "a" * 33


def resolve_value(value: str) -> str:
    if value == "__EMPTY__":
        return ""
    if value == "__LONG_33__":
        return LONG_VALUE
    return value


@pytest.fixture
def account_edit_page(logged_in_page: Page) -> AccountEditAccountDetailsPage:
    return AccountEditAccountDetailsPage(logged_in_page)


@pytest.fixture
def account_dashboard_page(logged_in_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_page)


@pytest.fixture
def original_account_details() -> dict[str, str]:
    return {
        "firstname": get_account_first_name(),
        "lastname": get_account_last_name(),
        "email": get_account_e_mail(),
        "telephone": get_account_telephone(),
        "fax": get_account_fax(),
    }


@pytest.fixture
def account_details_cleanup(
    account_edit_page: AccountEditAccountDetailsPage,
    original_account_details: dict[str, str],
) -> Iterator[None]:
    """Restore .env account details after the scenario, without masking its original failure."""
    yield
    try:
        account_edit_page.open()
        account_edit_page.expect_loaded()
        account_edit_page.fill_form(
            first_name=original_account_details["firstname"],
            last_name=original_account_details["lastname"],
            email=original_account_details["email"],
            telephone=original_account_details["telephone"],
            fax=original_account_details["fax"],
        )
        account_edit_page.click_continue()
        expect(account_edit_page.page).to_have_url(AccountDashboardPage.URL_PATTERN)
        expect(account_edit_page.page.locator(".alert.alert-success")).to_contain_text(
            "Success: Your account has been successfully updated."
        )
    except Exception as exc:  # cleanup must not mask a test failure
        warnings.warn(f"Account-details cleanup was incomplete: {exc}", stacklevel=2)


@given("the customer is logged in and opens Edit account details")
def customer_opens_account_edit(
    account_edit_page: AccountEditAccountDetailsPage,
    account_details_cleanup: None,
) -> None:
    account_edit_page.open()
    account_edit_page.expect_loaded()


@when("the customer changes all editable account details to new values")
def change_all_account_details(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.fill_form(
        first_name="Milhouse",
        last_name="Van Houten",
        email="milhouse.vanhouten@example.com",
        telephone="+1 212 555 0147",
        fax="+1 212 555 0188",
    )


@when(parsers.parse('the customer sets the first name to "{value}"'))
def set_first_name(account_edit_page: AccountEditAccountDetailsPage, value: str) -> None:
    account_edit_page.first_name_input.fill(resolve_value(value))


@when(parsers.parse('the customer sets the last name to "{value}"'))
def set_last_name(account_edit_page: AccountEditAccountDetailsPage, value: str) -> None:
    account_edit_page.last_name_input.fill(resolve_value(value))


@when(parsers.parse('the customer sets the e-mail to "{value}"'))
def set_email(account_edit_page: AccountEditAccountDetailsPage, value: str) -> None:
    account_edit_page.email_input.fill(resolve_value(value))


@when("the customer submits the account details form")
def submit_account_details(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.click_continue()


@when("the customer opens Edit account details again")
def reopen_account_edit(account_dashboard_page: AccountDashboardPage,
                        account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_dashboard_page.click_quick_link("Edit account details")
    account_edit_page.expect_loaded()


@then("the account dashboard confirms the account was successfully updated")
def account_update_success(
    account_dashboard_page: AccountDashboardPage,
    account_edit_page: AccountEditAccountDetailsPage,
) -> None:
    expect(account_dashboard_page.page).to_have_url(AccountDashboardPage.URL_PATTERN)
    expect(account_dashboard_page.page.locator(".alert.alert-success")).to_contain_text(
        "Success: Your account has been successfully updated."
    )


@then("the updated account details are displayed")
def updated_account_details_are_displayed(account_edit_page: AccountEditAccountDetailsPage) -> None:
    expected = {
        "firstname": "Milhouse",
        "lastname": "Van Houten",
        "email": "milhouse.vanhouten@example.com",
        "telephone": "+1 212 555 0147",
        "fax": "+1 212 555 0188",
    }
    for field, value in expected.items():
        account_edit_page.expect_field_value(field, value)


@then("the login name remains unchanged")
def login_name_unchanged(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.expect_login_name(get_account_login_name())


@then(parsers.parse('the account details form displays a validation error for "{field}"'))
def field_validation_error(account_edit_page: AccountEditAccountDetailsPage, field: str) -> None:
    expected_messages = {
        "firstname": "First Name must be between 1 and 32 characters!",
        "lastname": "Last Name must be between 1 and 32 characters!",
        "email": "E-Mail Address does not appear to be valid!",
    }
    account_edit_page.expect_field_error(field, expected_messages[field])


@then("the account details form stays open with an error alert")
def account_edit_validation_alert(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.expect_loaded()
    account_edit_page.expect_error_alert()
