import dataclasses
import uuid
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.account.account_manage_address_book_edit_address_page import AccountManageAddressBookEditAddressPage
from src.pages.account.account_manage_address_book_page import AccountManageAddressBookPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "address_book.feature"))

# ==========================================================================================================
# region TEST DATA
# ==========================================================================================================

# NOTE FOR ME: Imię tymczasowego adresu = unikalny znacznik (temporary_address_marker). Po nim znajdujemy nasz adres
# na liście i po nim sprzątamy. Limit imienia to 32 znaki: "AddrTest" + 8 znaków + "Updated" = 23.
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
# Every field differs from VALID_ADDRESS (also country and region)
# TODO: confirm that the store has the "Berlin" region for "Germany" (the region list is loaded per country)
UPDATED_ADDRESS = {
    "firstname": "UpdatedAddress",
    "lastname": "TestCustomer",
    "company": "Updated QA Ltd",
    "address_1": "Unter den Linden 77",
    "address_2": "Suite 10",
    "city": "Berlin",
    "postcode": "10117",
    "country": "Germany",
    "region": "Berlin",
}

UPDATED_SUFFIX = "Updated"

# NOTE FOR ME: Pusta wartość w tabeli Examples nie przejdzie przez parsers.parse("{value}"),
# dlatego używamy znaczników i zamieniamy je tutaj na prawdziwe dane.
VALUE_MARKERS = {
    "__EMPTY__": "",
    "__SHORT_1__": "1",
    "__SHORT_2__": "ab",
    "__LONG_11__": "1" * 11,
    "__LONG_33__": "a" * 33,
    "__LONG_129__": "a" * 129,
}


def resolve_value(value: str) -> str:
    return VALUE_MARKERS.get(value, value)


def expected_values(values: dict[str, str]) -> list[str]:
    """Texts that must appear in the listed address (order-agnostic, see expect_address_contains)."""
    return [
        f"{values['firstname']} {values['lastname']}", values["company"], values["address_1"],
        values["address_2"], values["city"], values["region"], values["postcode"], values["country"],
    ]


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region STATE AND FIXTURES
# ==========================================================================================================

@dataclasses.dataclass
class AddressBookState:
    """What the scenario remembered about the address book before it changed anything."""
    originals: dict[str, list[str]] = dataclasses.field(default_factory=dict)  # first line (name) -> all lines
    default_marker: str | None = None  # first line of the original default address
    count_before: int = 0


@pytest.fixture
def address_book_state() -> AddressBookState:
    return AddressBookState()


@pytest.fixture
def temporary_address_marker() -> str:
    return f"AddrTest{uuid.uuid4().hex[:8]}"


@pytest.fixture
def address_book_page(logged_in_page: Page) -> AccountManageAddressBookPage:
    return AccountManageAddressBookPage(logged_in_page)


@pytest.fixture
def address_form_page(logged_in_page: Page) -> AccountManageAddressBookEditAddressPage:
    return AccountManageAddressBookEditAddressPage(logged_in_page)


@pytest.fixture
def account_dashboard_page(logged_in_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_page)


@pytest.fixture
def address_cleanup(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        address_book_state: AddressBookState,
        temporary_address_marker: str,
) -> Iterator[None]:
    """
    [CLEANUP] Safety net for scenarios that failed halfway:
    1. makes the original default address default again (otherwise the temporary default can't be deleted),
    2. deletes the temporary address (its name starts with the marker both before and after the edit).
    Only browser/assertion errors are reported as warnings; programming errors (AttributeError etc.) are raised.
    """
    yield
    marker = temporary_address_marker
    default_marker = address_book_state.default_marker
    try:
        address_book_page.open()
        address_book_page.expect_loaded()

        if (default_marker
                and address_book_page.entry_containing(default_marker).count() == 1
                and address_book_page.has_delete_button_containing(default_marker)):
            address_book_page.click_edit_address_containing(default_marker)
            address_form_page.expect_loaded()
            address_form_page.fill_form(default=True)
            address_form_page.click_continue()
            address_book_page.expect_loaded()

        for _ in range(3):
            if address_book_page.entry_containing(marker).count() == 0:
                break
            if not address_book_page.has_delete_button_containing(marker):
                warnings.warn(f"Address-book cleanup: '{marker}' is still the default address", stacklevel=2)
                break
            address_book_page.click_delete_address_containing(marker)
            address_book_page.expect_loaded()
    except (PlaywrightError, AssertionError) as exc:
        warnings.warn(f"Address-book cleanup was incomplete: {exc}", stacklevel=2)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region HELPERS
# ==========================================================================================================

def fill_valid_form(
        form: AccountManageAddressBookEditAddressPage,
        values: dict[str, str],
        default: bool = False,
) -> None:
    form.fill_form(
        first_name=values["firstname"], last_name=values["lastname"], company=values["company"],
        address_1=values["address_1"], address_2=values["address_2"], city=values["city"],
        postcode=values["postcode"], country=values["country"], region=values["region"], default=default,
    )


def with_marker(marker: str, base: dict[str, str], suffix: str = "") -> dict[str, str]:
    return {**base, "firstname": marker + suffix}


def remember_addresses(book: AccountManageAddressBookPage, state: AddressBookState) -> None:
    state.count_before = book.addresses_count()
    for index in range(state.count_before):
        lines = book.address_lines(index)
        assert lines, f"Address #{index} has no text lines"
        name = lines[0]
        assert name not in state.originals, f"Two addresses share the name '{name}' - they can't be told apart"
        state.originals[name] = lines
        # The default address is the one without the Delete button
        if not book.entry_delete_button(index).count():
            state.default_marker = name


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


@given("the original address book entries are remembered")
def remember_original_addresses(
        address_book_page: AccountManageAddressBookPage,
        address_book_state: AddressBookState,
) -> None:
    remember_addresses(address_book_page, address_book_state)


@given("the account has exactly one address")
def account_has_one_address(address_book_page: AccountManageAddressBookPage) -> None:
    assert address_book_page.addresses_count() == 1, (
        "This scenario requires an account with exactly one saved address (is there a leftover from another test?)."
    )


@given("the customer is logged in and opens a new address form")
def open_new_address_form(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        address_book_state: AddressBookState,
        address_cleanup: None,
) -> None:
    address_book_page.open()
    address_book_page.expect_loaded()
    address_book_state.count_before = address_book_page.addresses_count()
    address_book_page.click_new_address()
    address_form_page.expect_loaded()


@given("the customer has a temporary non-default address")
def temporary_address_exists(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.click_new_address()
    address_form_page.expect_loaded()
    fill_valid_form(address_form_page, with_marker(temporary_address_marker, VALID_ADDRESS), default=False)
    address_form_page.click_continue()
    address_book_page.expect_loaded()
    address_book_page.expect_address_inserted_alert()


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


@when("the customer adds a valid default address")
def add_default_address(
        address_form_page: AccountManageAddressBookEditAddressPage,
        address_book_page: AccountManageAddressBookPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.click_new_address()
    address_form_page.expect_loaded()
    fill_valid_form(address_form_page, with_marker(temporary_address_marker, VALID_ADDRESS), default=True)
    address_form_page.click_continue()


@when("the customer edits the new address with different valid details")
def edit_new_address(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.click_edit_address_containing(temporary_address_marker)
    address_form_page.expect_loaded()
    fill_valid_form(
        address_form_page, with_marker(temporary_address_marker, UPDATED_ADDRESS, UPDATED_SUFFIX), default=False)
    address_form_page.click_continue()


@when("the customer deletes the new address")
def delete_new_address(
        address_book_page: AccountManageAddressBookPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.click_delete_address_containing(temporary_address_marker)


@when('the customer edits the only address and sets Default Address to "No"')
def set_only_address_non_default(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
) -> None:
    address_book_page.click_edit_address(0)
    address_form_page.expect_loaded()
    address_form_page.fill_form(default=False)
    address_form_page.click_continue()
    address_book_page.expect_loaded()


@when("the customer opens the only address for editing again")
def reopen_only_address(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
) -> None:
    address_book_page.click_edit_address(0)
    address_form_page.expect_loaded()


@when("the customer restores the original address as default")
def restore_original_default(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        address_book_state: AddressBookState,
) -> None:
    assert address_book_state.default_marker, "The original default address was not captured."
    address_book_page.click_edit_address_containing(address_book_state.default_marker)
    address_form_page.expect_loaded()
    address_form_page.fill_form(default=True)
    address_form_page.click_continue()
    address_book_page.expect_loaded()


@when("the customer opens the temporary address for editing")
def open_temporary_address_for_editing(
        address_book_page: AccountManageAddressBookPage,
        address_form_page: AccountManageAddressBookEditAddressPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.click_edit_address_containing(temporary_address_marker)
    address_form_page.expect_loaded()


@when(
    parsers.parse('the customer fills all required address fields with valid values except "{field}" set to "{value}"'))
def fill_invalid_field_in_new_form(
        address_form_page: AccountManageAddressBookEditAddressPage,
        temporary_address_marker: str,
        field: str,
        value: str,
) -> None:
    fill_valid_form(address_form_page, with_marker(temporary_address_marker, VALID_ADDRESS), default=False)
    set_field(address_form_page, field, value)


@when(parsers.parse('the customer changes only "{field}" to "{value}"'))
def change_only_field(
        address_form_page: AccountManageAddressBookEditAddressPage,
        field: str,
        value: str,
) -> None:
    set_field(address_form_page, field, value)


@when("the customer submits the address form")
def submit_address_form(address_form_page: AccountManageAddressBookEditAddressPage) -> None:
    address_form_page.click_continue()


def set_field(form: AccountManageAddressBookEditAddressPage, field: str, value: str) -> None:
    if field == "zone_id":
        form.clear_region()
    else:
        form.fill_field(field, resolve_value(value))


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the address book confirms the address was successfully inserted")
def address_inserted(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_address_inserted_alert()


@then("the address book confirms the address was successfully updated")
def address_updated(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_address_updated_alert()


@then("the address book confirms the address was successfully deleted")
def address_deleted(address_book_page: AccountManageAddressBookPage) -> None:
    address_book_page.expect_loaded()
    address_book_page.expect_address_deleted_alert()


@then("the original addresses are unchanged")
def original_addresses_unchanged(
        address_book_page: AccountManageAddressBookPage,
        address_book_state: AddressBookState,
) -> None:
    assert address_book_state.originals, "The original addresses were not captured."
    for name, lines in address_book_state.originals.items():
        address_book_page.expect_address_listed(name)
        address_book_page.expect_address_lines_containing(name, lines)


@then("the address book has one more address than before")
def one_more_address(address_book_page: AccountManageAddressBookPage, address_book_state: AddressBookState) -> None:
    address_book_page.expect_addresses_count(address_book_state.count_before + 1)


@then("the address book has the same number of addresses as before")
def same_number_of_addresses(
        address_book_page: AccountManageAddressBookPage,
        address_book_state: AddressBookState,
) -> None:
    address_book_page.expect_addresses_count(address_book_state.count_before)


@then("the new address is listed with the entered details")
def new_address_listed(address_book_page: AccountManageAddressBookPage, temporary_address_marker: str) -> None:
    values = with_marker(temporary_address_marker, VALID_ADDRESS)
    address_book_page.expect_address_listed(temporary_address_marker)
    address_book_page.expect_address_contains(temporary_address_marker, expected_values(values))


@then("the updated address is listed with the entered details")
def updated_address_listed(address_book_page: AccountManageAddressBookPage, temporary_address_marker: str) -> None:
    values = with_marker(temporary_address_marker, UPDATED_ADDRESS, UPDATED_SUFFIX)
    address_book_page.expect_address_listed(temporary_address_marker + UPDATED_SUFFIX)
    address_book_page.expect_address_contains(temporary_address_marker, expected_values(values))
    # None of the old details may be left behind
    address_book_page.expect_address_not_listed(VALID_ADDRESS["address_1"])


@then("the new address is not listed")
def new_address_not_listed(address_book_page: AccountManageAddressBookPage, temporary_address_marker: str) -> None:
    # The marker is a prefix of the name both before and after the edit
    address_book_page.expect_address_not_listed(temporary_address_marker)


@then("the new address has no Delete button")
def new_address_has_no_delete(address_book_page: AccountManageAddressBookPage, temporary_address_marker: str) -> None:
    address_book_page.expect_address_listed(temporary_address_marker)
    address_book_page.expect_no_delete_button(temporary_address_marker)


@then("the new address has a Delete button")
def new_address_has_delete(address_book_page: AccountManageAddressBookPage, temporary_address_marker: str) -> None:
    address_book_page.expect_delete_button_visible(temporary_address_marker)


@then("the original default address has a Delete button")
def original_default_has_delete(
        address_book_page: AccountManageAddressBookPage,
        address_book_state: AddressBookState,
) -> None:
    assert address_book_state.default_marker, "The original default address was not captured."
    address_book_page.expect_delete_button_visible(address_book_state.default_marker)


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
def address_was_not_saved(
        address_book_page: AccountManageAddressBookPage,
        address_book_state: AddressBookState,
) -> None:
    address_book_page.open()
    address_book_page.expect_loaded()
    address_book_page.expect_addresses_count(address_book_state.count_before)


@then("the temporary address keeps its original details")
def temporary_address_unchanged(
        address_book_page: AccountManageAddressBookPage,
        temporary_address_marker: str,
) -> None:
    address_book_page.open()
    address_book_page.expect_loaded()
    values = with_marker(temporary_address_marker, VALID_ADDRESS)
    address_book_page.expect_address_contains(temporary_address_marker, expected_values(values))

# endregion
# ==========================================================================================================
