import time
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page
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

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "edit_account_details.feature"))

LONG_VALUE = "a" * 33


def resolve_value(value: str) -> str:
    # NOTE FOR ME: Pusta wartość w tabeli Examples nie przejdzie przez parsers.parse("{value}"),
    # dlatego używamy znaczników __EMPTY__ i __LONG_33__ i zamieniamy je tutaj na prawdziwe dane.
    if value == "__EMPTY__":
        return ""
    if value == "__LONG_33__":
        return LONG_VALUE
    return value


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def account_edit_page(logged_in_page: Page) -> AccountEditAccountDetailsPage:
    return AccountEditAccountDetailsPage(logged_in_page)


@pytest.fixture
def account_dashboard_page(logged_in_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_page)


@pytest.fixture
def original_account_details() -> dict[str, str]:
    """Account data from .env, i.e. the state the account should have before and after every scenario."""
    return {
        "firstname": get_account_first_name(),
        "lastname": get_account_last_name(),
        "email": get_account_e_mail(),
        "telephone": get_account_telephone(),
        "fax": get_account_fax(),
    }


@pytest.fixture
def new_account_details() -> dict[str, str]:
    """
    New values for the positive scenario (one source of truth for both filling and verifying the form).

    NOTE FOR ME: E-mail jest unikalny (timestamp), bo sklep sprawdza, czy adres nie należy do innego konta.
    Bez znaku "+" w adresie, bo walidacja sklepu uznaje go za niepoprawny.
    """
    return {
        "firstname": "Milhouse",
        "lastname": "Van Houten",
        "email": f"milhouse.vanhouten{int(time.time())}@example.com",
        "telephone": "+1 212 555 0147",
        "fax": "+1 212 555 0188",
    }


@pytest.fixture
def restore_account_details(
        account_edit_page: AccountEditAccountDetailsPage,
        account_dashboard_page: AccountDashboardPage,
        original_account_details: dict[str, str],
) -> Iterator[None]:
    """
    [CLEANUP] Restores the .env account details after the scenario.

    NOTE FOR ME: Używana tylko w scenariuszach pozytywnych (negatywne nic nie zapisują). Błąd sprzątania nie może
    zamaskować błędu testu, więc zamiast wyjątku jest ostrzeżenie widoczne w podsumowaniu pytesta.
    """
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
        account_dashboard_page.expect_loaded()
        account_dashboard_page.expect_account_updated_alert()
    except Exception as exc:  # noqa: BLE001 - teardown must not mask a test failure
        warnings.warn(f"Account-details cleanup was incomplete: {exc}", stacklevel=2)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and opens Edit account details from the account dashboard")
def customer_opens_account_edit_from_dashboard(
        account_dashboard_page: AccountDashboardPage,
        account_edit_page: AccountEditAccountDetailsPage,
        restore_account_details: None,
) -> None:
    account_dashboard_page.open()
    account_dashboard_page.expect_loaded()
    account_dashboard_page.click_quick_link("Edit account details")
    account_edit_page.expect_loaded()


@given("the customer is logged in and opens Edit account details")
def customer_opens_account_edit(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.open()
    account_edit_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the customer changes all editable account details to new values")
def change_all_account_details(
        account_edit_page: AccountEditAccountDetailsPage,
        new_account_details: dict[str, str],
) -> None:
    account_edit_page.fill_form(
        first_name=new_account_details["firstname"],
        last_name=new_account_details["lastname"],
        email=new_account_details["email"],
        telephone=new_account_details["telephone"],
        fax=new_account_details["fax"],
    )


@when("the customer clears the optional telephone and fax")
def clear_optional_fields(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.fill_form(telephone="", fax="")


@when(parsers.parse('the customer sets the first name to "{value}"'))
def set_first_name(account_edit_page: AccountEditAccountDetailsPage, value: str) -> None:
    account_edit_page.set_first_name(resolve_value(value))


@when(parsers.parse('the customer sets the last name to "{value}"'))
def set_last_name(account_edit_page: AccountEditAccountDetailsPage, value: str) -> None:
    account_edit_page.set_last_name(resolve_value(value))


@when(parsers.parse('the customer sets the e-mail to "{value}"'))
def set_email(account_edit_page: AccountEditAccountDetailsPage, value: str) -> None:
    account_edit_page.set_email(resolve_value(value))


@when("the customer submits the account details form")
def submit_account_details(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.click_continue()


@when("the customer opens Edit account details again")
def reopen_account_edit(
        account_dashboard_page: AccountDashboardPage,
        account_edit_page: AccountEditAccountDetailsPage,
) -> None:
    account_dashboard_page.click_quick_link("Edit account details")
    account_edit_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the account dashboard confirms the account was successfully updated")
def account_update_success(account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.expect_loaded()
    account_dashboard_page.expect_account_updated_alert()


@then("the updated account details are displayed")
def updated_account_details_are_displayed(
        account_edit_page: AccountEditAccountDetailsPage,
        new_account_details: dict[str, str],
) -> None:
    account_edit_page.expect_field_values(new_account_details)


@then("the telephone and fax fields are empty")
def optional_fields_are_empty(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.expect_field_values({"telephone": "", "fax": ""})


@then("the first name, last name and e-mail are unchanged")
def required_fields_unchanged(
        account_edit_page: AccountEditAccountDetailsPage,
        original_account_details: dict[str, str],
) -> None:
    account_edit_page.expect_field_values({
        field: original_account_details[field] for field in account_edit_page.REQUIRED_FIELDS
    })


@then("the login name remains unchanged")
def login_name_unchanged(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.expect_login_name(get_account_login_name())


@then(parsers.parse('the account details form displays a validation error for "{field}"'))
def field_validation_error(account_edit_page: AccountEditAccountDetailsPage, field: str) -> None:
    account_edit_page.expect_field_validation_error(field)


@then("the account details form stays open with an error alert")
def account_edit_validation_alert(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.expect_loaded()
    account_edit_page.expect_error_alert()


@then("the account details were not saved")
def account_details_not_saved(
        account_edit_page: AccountEditAccountDetailsPage,
        original_account_details: dict[str, str],
) -> None:
    # NOTE FOR ME: Otwieramy formularz od nowa (z serwera), bo po błędzie strona potrafi pokazać wpisane,
    # niezapisane wartości. Jeśli ten krok pada, sprawdź czy poprzednie sprzątanie nie zostawiło brudnych danych.
    account_edit_page.open()
    account_edit_page.expect_loaded()
    account_edit_page.expect_field_values(original_account_details)

# endregion
# ==========================================================================================================
