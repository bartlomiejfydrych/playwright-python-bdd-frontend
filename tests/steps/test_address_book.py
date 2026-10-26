import time
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.account.account_manage_address_book_page import AccountManageAddressBookPage
from src.pages.account.account_manage_address_book_edit_address_page import AccountManageAddressBookEditAddressPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "address_book.feature"))

VALID_ADDRESS = {
    "firstname": "AddressTest",
    "lastname": "Customer",
    "company": "Automation QA",
    "address_1": "742 Evergreen Terrace",
    "address_2": "Apartment 2",
    "city": "Springfield",
    "postcode": "90210",
    "country": "United States",
    "region": "California",
}
UPDATED_ADDRESS = {
    "firstname": "UpdatedAddress",
    "lastname": "TestCustomer",
    "company": "Updated QA Ltd",
    "address_1": "1600 Pennsylvania Avenue",
    "address_2": "Suite 10",
    "city": "Washington",
    "postcode": "20500",
    "country": "United States",
    "region": "California",
}
FIELD_NAMES = {
    "firstname": "firstname", "lastname": "lastname", "company": "company",
    "address_1": "address_1", "address_2": "address_2", "city": "city",
    "postcode": "postcode", "zone_id": "zone_id",
}


@pytest.fixture
def address_book_page(logged_in_page: Page) -> AccountManageAddressBookPage:
    return AccountManageAddressBookPage(logged_in_page)


@pytest.fixture
def address_form_page(logged_in_page: Page) -> AccountManageAddressBookEditAddressPage:
    return AccountManageAddressBookEditAddressPage(logged_in_page)


@pytest.fixture
def original_addresses() -> dict[str, list[str]]:
    return {}


@pytest.fixture
def temporary_address_marker() -> str:
    return f"AddressTest{int(time.time())}"


@pytest.fixture
def address_count_before_form() -> list[int]:
    return []


@pytest.fixture
def address_cleanup(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        original_addresses: dict[str, list[str]],
        temporary_address_marker: str,
) -> Iterator[None]:
    yield
    # Best-effort cleanup: remove a temporary address if it was created, and restore the original default.
    try:
        address_book_page.open()
        address_book_page.expect_loaded()
        # Restore an original address as default first, so the temporary default can become deletable.
        for marker, lines in original_addresses.items():
            if address_book_page.entry_containing(marker).count():
                address_book_page.click_edit_address_containing(marker)
                address_form_page.expect_loaded()
                address_form_page.fill_form(default=True)
                address_form_page.click_continue()
                address_book_page.expect_loaded()
                break
        if address_book_page.entry_containing(temporary_address_marker).count():
            entry = address_book_page.entry_containing(temporary_address_marker)
            if entry.locator("a[title='Delete'], button[title='Delete']").count():
                address_book_page.page.once("dialog", lambda dialog: dialog.accept())
                address_book_page.click_delete_address_containing(temporary_address_marker)
    except Exception as exc:  # noqa: BLE001
        warnings.warn(f"Address-book cleanup was incomplete: {exc}", stacklevel=2)


def _valid_form(form: AccountManageAddressBookEditAddressPage, values: dict[str, str] = VALID_ADDRESS,
                default: bool = False) -> None:
    form.fill_form(
        first_name=values["firstname"], last_name=values["lastname"], company=values["company"],
        address_1=values["address_1"], address_2=values["address_2"], city=values["city"],
        postcode=values["postcode"], country=values["country"], region=values["region"], default=default,
    )


def _address_lines(values: dict[str, str]) -> list[str]:
    return [values["firstname"] + " " + values["lastname"], values["company"], values["address_1"],
            values["address_2"], values["city"], values["region"], values["postcode"], values["country"]]


def _resolve(value: str) -> str:
    return {"__EMPTY__": "", "__SHORT_1__": "1", "__SHORT_2__": "ab",
            "__LONG_33__": "a" * 33, "__LONG_11__": "1" * 11,
            "__LONG_129__": "a" * 129}.get(value, value)


@given("the customer is logged in and opens Manage Address Book from the account dashboard")
def open_address_book(address_book_page: AccountManageAddressBookPage,
                      account_dashboard_page: AccountDashboardPage) -> None:
    account_dashboard_page.open()
    account_dashboard_page.expect_loaded()
    account_dashboard_page.open_side_menu_item("Manage Address Book")
    address_book_page.expect_loaded()


@pytest.fixture
def account_dashboard_page(logged_in_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_page)


@given("the original address book entries are remembered")
def remember_original_addresses(address_book_page: AccountManageAddressBookPage,
                                original_addresses: dict[str, list[str]],
                                address_cleanup: None) -> None:
    for i in range(address_book_page.addresses_count()):
        lines = address_book_page.address_lines(i)
        if lines:
            original_addresses[lines[0]] = lines


@given("the account has exactly one address")
def account_has_one_address(address_book_page: AccountManageAddressBookPage) -> None:
    assert address_book_page.addresses_count() == 1, (
        "This scenario requires a dedicated account with exactly one saved address."
    )


@given("the customer is logged in and opens a new address form")
def open_new_address(address_book_page: AccountManageAddressBookPage,
                     address_form_page: AccountManageAddressBookEditAddressPage,
                     address_count_before_form: list[int]) -> None:
    address_book_page.open()
    address_book_page.expect_loaded()
    address_count_before_form.append(address_book_page.addresses_count())
    address_book_page.click_new_address()
    address_form_page.expect_loaded()


@when("the customer adds a valid non-default address")
def add_non_default_address(address_book_page: AccountManageAddressBookPage,
                            address_form_page: AccountManageAddressBookEditAddressPage,
                            temporary_address_marker: str) -> None:
    values = {**VALID_ADDRESS, "firstname": temporary_address_marker}
    _valid_form(address_form_page, values, default=False)
    address_form_page.click_continue()


@when("the customer adds a valid default address")
def add_default_address(address_book_page: AccountManageAddressBookPage,
                        address_form_page: AccountManageAddressBookEditAddressPage,
                        temporary_address_marker: str) -> None:
    values = {**VALID_ADDRESS, "firstname": temporary_address_marker}
    _valid_form(address_form_page, values, default=True)
    address_form_page.click_continue()


@when("the customer edits the new address with different valid details")
def edit_new_address(address_book_page: AccountManageAddressBookPage,
                     address_form_page: AccountManageAddressBookEditAddressPage,
                     temporary_address_marker: str) -> None:
    address_book_page.click_edit_address_containing(temporary_address_marker)
    address_form_page.expect_loaded()
    values = {**UPDATED_ADDRESS, "firstname": temporary_address_marker + "Updated"}
    _valid_form(address_form_page, values, default=False)
    address_form_page.click_continue()


@when("the customer deletes the new address")
def delete_new_address(address_book_page: AccountManageAddressBookPage,
                       temporary_address_marker: str) -> None:
    marker = temporary_address_marker + "Updated"
    address_book_page.page.once("dialog", lambda dialog: dialog.accept())
    address_book_page.click_delete_address_containing(marker)


@when('the customer edits the only address and sets Default Address to "No"')
def set_only_address_non_default(address_book_page: AccountManageAddressBookPage,
                                 address_form_page: AccountManageAddressBookEditAddressPage) -> None:
    address_book_page.click_edit_address(0)
    address_form_page.expect_loaded()
    address_form_page.fill_form(default=False)
    address_form_page.click_continue()
    address_book_page.expect_loaded()


@when("the customer opens the only address for editing again")
def reopen_only_address(address_book_page: AccountManageAddressBookPage,
                        address_form_page: AccountManageAddressBookEditAddressPage) -> None:
    address_book_page.click_edit_address(0)
    address_form_page.expect_loaded()


@when("the customer restores the original address as default")
def restore_original_default(address_book_page: AccountManageAddressBookPage,
                             address_form_page: AccountManageAddressBookEditAddressPage,
                             original_addresses: dict[str, list[str]]) -> None:
    assert original_addresses, "Original address was not captured."
    marker = next(iter(original_addresses))
    address_book_page.click_edit_address_containing(marker)
    address_form_page.expect_loaded()
    address_form_page.fill_form(default=True)
    address_form_page.click_continue()
    address_book_page.expect_loaded()


@when("the customer deletes the temporary default address")
def delete_temporary_default(address_book_page: AccountManageAddressBookPage,
                             temporary_address_marker: str) -> None:
    address_book_page.page.once("dialog", lambda dialog: dialog.accept())
    address_book_page.click_delete_address_containing(temporary_address_marker)


@when(
    parsers.parse('the customer fills all required address fields with valid values except "{field}" set to "{value}"'))
def fill_invalid_field(address_form_page: AccountManageAddressBookEditAddressPage,
                       field: str, value: str) -> None:
    _valid_form(address_form_page, default=False)
    if field == "zone_id":
        address_form_page.region_select.select_option(value="FALSE")
    else:
        address_form_page.field_input(field).fill(_resolve(value))


@when("the customer submits the address form")
def submit_address_form(address_form_page: AccountManageAddressBookEditAddressPage) -> None:
    address_form_page.click_continue()


@then("the address book confirms the address was successfully inserted")
def address_inserted(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_success_alert("Your address has been successfully inserted")


@then("the address book confirms the address was successfully updated")
def address_updated(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_success_alert("Your address has been successfully updated")


@then("the address book confirms the address was successfully deleted")
def address_deleted(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_success_alert("Your address has been successfully deleted")


@then("the original addresses are unchanged")
def original_addresses_unchanged(address_book_page: AccountManageAddressBookPage,
                                 original_addresses: dict[str, list[str]]) -> None:
    for marker, lines in original_addresses.items():
        address_book_page.expect_address_listed(marker)
        address_book_page.expect_address_lines_containing(marker, lines)


@then("the new address is listed")
def new_address_listed(address_book_page: AccountManageAddressBookPage,
                       temporary_address_marker: str) -> None:
    address_book_page.expect_address_listed(temporary_address_marker)


@then("the updated address is listed")
def updated_address_listed(address_book_page: AccountManageAddressBookPage,
                           temporary_address_marker: str) -> None:
    address_book_page.expect_address_listed(temporary_address_marker + "Updated")
    address_book_page.expect_address_not_listed(temporary_address_marker + " " + VALID_ADDRESS["lastname"])


@then("the new address is not listed")
def new_address_not_listed(address_book_page: AccountManageAddressBookPage,
                           temporary_address_marker: str) -> None:
    address_book_page.expect_address_not_listed(temporary_address_marker)
    address_book_page.expect_address_not_listed(temporary_address_marker + "Updated")


@then("the temporary address is not listed")
def temporary_address_not_listed(address_book_page: AccountManageAddressBookPage,
                                 temporary_address_marker: str) -> None:
    address_book_page.expect_address_not_listed(temporary_address_marker)


@then("the original address has a Delete button")
def original_address_has_delete(address_book_page: AccountManageAddressBookPage,
                                original_addresses: dict[str, list[str]]) -> None:
    marker = next(iter(original_addresses))
    assert address_book_page.has_delete_button(marker)


@then("the new default address has no Delete button")
def new_default_has_no_delete(address_book_page: AccountManageAddressBookPage,
                              temporary_address_marker: str) -> None:
    assert not address_book_page.has_delete_button(temporary_address_marker)


@then(parsers.parse('Default Address is still set to "{value}"'))
def default_value_still_set(address_form_page: AccountManageAddressBookEditAddressPage, value: str) -> None:
    address_form_page.expect_default_address(value == "Yes")


@then("the address form stays open with an error alert")
def address_form_error_alert(address_form_page: AccountManageAddressBookEditAddressPage) -> None:
    address_form_page.expect_loaded()
    address_form_page.expect_error_alert()


@then(parsers.parse('the address form displays the validation error for "{field}"'))
def address_field_validation_error(address_form_page: AccountManageAddressBookEditAddressPage, field: str) -> None:
    address_form_page.expect_field_validation_error(field)


@then("the address was not saved")
def address_was_not_saved(address_book_page: AccountManageAddressBookPage,
                          address_form_page: AccountManageAddressBookEditAddressPage,
                          address_count_before_form: list[int]) -> None:
    address_book_page.open()
    address_book_page.expect_loaded()
    assert address_count_before_form, "Address count was not captured before opening the form."
    assert address_book_page.addresses_count() == address_count_before_form[0], (
        "An invalid address was unexpectedly saved."
    )
