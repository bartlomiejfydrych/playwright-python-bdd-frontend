from pathlib import Path

from pytest_bdd import given, scenarios, then, when
from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

from src.pages.account.account_change_password_page import AccountChangePasswordPage
# NOTE FOR ME: Fixture z test_change_password.py importujemy, bo w pytest-bdd fixture z innego modułu nie jest widoczny.
# Importowane fixture działają tak samo jak własne.
from tests.steps.test_change_password import change_password_page  # noqa: F401

scenarios(str(Path(__file__).resolve().parents[2] / "features" / "visual" / "change_password_visual.feature"))


# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and opens Change password")
def open_change_password(change_password_page: AccountChangePasswordPage) -> None:
    change_password_page.open()
    change_password_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the customer submits the empty Change password form")
def submit_empty_form(change_password_page: AccountChangePasswordPage) -> None:
    # NOTE FOR ME: Puste pola = nie zależymy od hasła z .env ani od liczby kropek w polach, więc wygląd jest stały.
    # Test nie zmienia hasła, więc nie potrzebuje sprzątania (restore_original_password).
    change_password_page.click_continue()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the Change password form matches the visual snapshot")
def form_snapshot(
        change_password_page: AccountChangePasswordPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    change_password_page.expect_form_matches_snapshot(assert_snapshot, "change_password_form_new")


@then("the password change error alert matches the visual snapshot")
def error_alert_snapshot(
        change_password_page: AccountChangePasswordPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    change_password_page.expect_error_alert_matches_snapshot(assert_snapshot, "change_password_error_alert")


@then("the Change password form with the validation errors matches the visual snapshot")
def error_form_snapshot(
        change_password_page: AccountChangePasswordPage,
        assert_snapshot: AssertSnapshot,
) -> None:
    change_password_page.expect_form_matches_snapshot(assert_snapshot, "change_password_form_errors")

# endregion
# ==========================================================================================================
