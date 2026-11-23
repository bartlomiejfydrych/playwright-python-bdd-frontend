from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, scenarios, then, when
from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.account.account_manage_address_book_edit_address_page import AccountManageAddressBookEditAddressPage
from src.pages.account.account_manage_address_book_page import AccountManageAddressBookPage
# NOTE FOR ME: Fixtures z test_address_book.py importujemy, bo w pytest-bdd fixture z innego modułu nie jest widoczny.
# Importowane fixture działają tak samo jak własne. `temporary_address_marker` celowo NIE jest importowany,
# bo niżej mamy jego wersję ze stałą wartością (patrz TEST DATA).
from tests.steps.test_address_book import (  # noqa: F401
    VALID_ADDRESS,
    address_book_page,
    address_book_state,
    address_cleanup,
    address_form_page,
    account_dashboard_page,
    fill_valid_form,
    with_marker,
)

scenarios(str(Path(__file__).resolve().parents[2] / "features" / "visual" / "address_book_visual.feature"))

# ==========================================================================================================
# region TEST DATA
# ==========================================================================================================

# NOTE FOR ME: Normalnie marker jest losowy (uuid), ale wtedy imię w adresie zmieniałoby się przy każdym uruchomieniu
# i screeny nigdy by się nie zgadzały. Tu marker jest stały, dzięki temu wygląd wpisu jest zawsze taki sam.
# Limit imienia to 32 znaki.
VISUAL_ADDRESS_MARKER = "VisualAddress"


@pytest.fixture
def temporary_address_marker() -> str:
    return VISUAL_ADDRESS_MARKER


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and opens Manage Address Book from the account dashboard")
def open_address_book(
        address_book_page: AccountManageAddressBookPage,
        account_dashboard_page: AccountDashboardPage,
        address_cleanup: None,
) -> None:
    account_dashboard_page.open()
    account_dashboard_page.expect_loaded()
    account_dashboard_page.open_side_menu_item("Manage Address Book")
    address_book_page.expect_loaded()


@given("the customer is logged in and opens a new address form")
def open_new_address_form(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        address_cleanup: None,
) -> None:
    address_book_page.open()
    address_book_page.expect_loaded()
    address_book_page.click_new_address()
    address_form_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the customer adds a valid non-default address")
def add_non_default_address(
        address_form_page: AccountManageAddressBookEditAddressPage,
        address_book_page: AccountManageAddressBookPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.click_new_address()
    address_form_page.expect_loaded()
    fill_valid_form(address_form_page, with_marker(temporary_address_marker, VALID_ADDRESS), default=False)
    address_form_page.click_continue()


@when("the customer submits the address form with an empty first name")
def submit_form_with_empty_first_name(
        address_form_page: AccountManageAddressBookEditAddressPage,
        temporary_address_marker: str,
) -> None:
    # NOTE FOR ME: Pusty firstname = w formularzu po błędzie nie ma markera, więc wygląd formularza jest stały
    values = {**VALID_ADDRESS, "firstname": ""}
    fill_valid_form(address_form_page, values, default=False)
    address_form_page.click_continue()


@when("the customer deletes the new address")
def delete_new_address(
        address_book_page: AccountManageAddressBookPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.click_delete_address_containing(temporary_address_marker)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the new address form matches the visual snapshot")
def new_address_form_snapshot(
        address_form_page: AccountManageAddressBookEditAddressPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    address_form_page.expect_form_matches_snapshot(assert_snapshot, "address_form_new")


@then("the validation error alert matches the visual snapshot")
def validation_error_alert_snapshot(
        address_form_page: AccountManageAddressBookEditAddressPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    address_form_page.expect_error_alert_matches_snapshot(assert_snapshot, "address_form_error_alert")


@then("the address form with the validation error matches the visual snapshot")
def validation_error_form_snapshot(
        address_form_page: AccountManageAddressBookEditAddressPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    address_form_page.expect_form_matches_snapshot(assert_snapshot, "address_form_error_first_name")


@then("the address book confirms the address was successfully inserted")
def address_inserted(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_address_inserted_alert()


@then("the address book confirms the address was successfully deleted")
def address_deleted(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_address_deleted_alert()


@then("the new address entry matches the visual snapshot")
def new_address_entry_snapshot(
        address_book_page: AccountManageAddressBookPage,
        temporary_address_marker: str,
        assert_snapshot: AssertSnapshot,
) -> None:
    address_book_page.expect_entry_matches_snapshot(assert_snapshot, temporary_address_marker, "address_entry_new")

# endregion
# ==========================================================================================================
