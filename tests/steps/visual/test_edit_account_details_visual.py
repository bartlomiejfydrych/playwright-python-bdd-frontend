from pathlib import Path

from pytest_bdd import given, scenarios, then, when
from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

from src.pages.account.account_edit_account_details_page import AccountEditAccountDetailsPage
# NOTE FOR ME: Fixture z test_edit_account_details.py importujemy, bo w pytest-bdd fixture z innego modułu nie jest
# widoczny. Kroki (given/when/then) trzeba zdefiniować tu od nowa. Fixtures `original_account_details`,
# `new_account_details` i `restore_account_details` celowo NIE są importowane: te testy niczego nie zapisują,
# więc nie potrzebują sprzątania.
from tests.steps.test_edit_account_details import account_edit_page  # noqa: F401

scenarios(str(Path(__file__).resolve().parents[2] / "features" / "visual" / "edit_account_details_visual.feature"))

# ==========================================================================================================
# region TEST DATA
# ==========================================================================================================

# NOTE FOR ME: Formularz jest wypełniany stałymi wartościami i NIGDY nie zapisywany (przy błędach walidacji sklep
# nic nie zapisuje). Dzięki temu screeny nie zależą od danych konta z .env i nie trzeba sprzątać.
# Login name (tekst tylko do odczytu z .env) jest zakryty maską w page object (LOGIN_NAME_MASK_SELECTOR).
FIXED_ACCOUNT_DETAILS = {
    "first_name": "VisualTest",
    "last_name": "Customer",
    "email": "visual.test@example.com",
    "telephone": "+1 212 555 0100",
    "fax": "+1 212 555 0101",
}


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and opens Edit account details")
def open_account_edit(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.open()
    account_edit_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the customer fills the account details form with fixed values")
def fill_fixed_values(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.fill_form(**FIXED_ACCOUNT_DETAILS)


@when("the customer breaks the first name, last name and e-mail")
def break_required_fields(account_edit_page: AccountEditAccountDetailsPage) -> None:
    # NOTE FOR ME: Puste imię i nazwisko oraz e-mail bez "@" = trzy błędy walidacji naraz w jednym screenie.
    account_edit_page.fill_form(first_name="", last_name="", email="invalid.example.com")


@when("the customer submits the account details form")
def submit_account_details(account_edit_page: AccountEditAccountDetailsPage) -> None:
    account_edit_page.click_continue()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the Edit account details form matches the visual snapshot")
def form_snapshot(
        account_edit_page: AccountEditAccountDetailsPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    account_edit_page.expect_form_matches_snapshot(assert_snapshot, "edit_account_details_form_filled")


@then("the account details error alert matches the visual snapshot")
def error_alert_snapshot(
        account_edit_page: AccountEditAccountDetailsPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    account_edit_page.expect_error_alert_matches_snapshot(assert_snapshot, "edit_account_details_error_alert")


@then("the Edit account details form with the validation errors matches the visual snapshot")
def error_form_snapshot(
        account_edit_page: AccountEditAccountDetailsPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    account_edit_page.expect_form_matches_snapshot(assert_snapshot, "edit_account_details_form_errors")

# endregion
# ==========================================================================================================
