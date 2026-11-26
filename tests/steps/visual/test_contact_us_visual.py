from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when
from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

from src.pages.contact_us_page import ContactUsPage
# NOTE FOR ME: Z test_contact_us.py importujemy tylko fixture `contact_us_page`. Kroki (given/when/then) trzeba
# zdefiniować w tym pliku od nowa, bo pytest-bdd rejestruje krok w module, w którym stoi dekorator, a zaimportowana
# funkcja kroku nie jest widoczna jako krok. `valid_enquiry` celowo NIE jest importowany, bo niżej mamy jego wersję
# ze stałymi danymi (patrz TEST DATA).
from tests.steps.test_contact_us import contact_us_page  # noqa: F401

scenarios(str(Path(__file__).resolve().parents[2] / "features" / "visual" / "contact_us_visual.feature"))

# ==========================================================================================================
# region TEST DATA
# ==========================================================================================================

# NOTE FOR ME: W zwykłych testach imię jest losowe (Faker), ale wtedy strona sukcesu/formularz wyglądałyby inaczej
# przy każdym uruchomieniu. Tu dane są stałe, więc screeny zawsze się zgadzają.
FIXED_ENQUIRY = {
    "first_name": "VisualTest",
    "email": "contact.us.automation@example.com",
    "enquiry": "This is an automated visual test enquiry. Please disregard this message.",
}


@pytest.fixture
def fixed_enquiry() -> dict[str, str]:
    return FIXED_ENQUIRY


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and opens the Contact Us page")
def customer_opens_contact_us_page(contact_us_page: ContactUsPage) -> None:
    contact_us_page.open()
    contact_us_page.expect_logged_in()
    contact_us_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the customer fills in the Contact Us form with fixed data")
def fill_contact_form_with_fixed_data(contact_us_page: ContactUsPage, fixed_enquiry: dict[str, str]) -> None:
    contact_us_page.fill_form(**fixed_enquiry)


@when("the customer submits the enquiry")
def submit_enquiry(contact_us_page: ContactUsPage) -> None:
    contact_us_page.click_submit()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the Contact Us form matches the visual snapshot")
def form_snapshot(contact_us_page: ContactUsPage, assert_snapshot: AssertSnapshot) -> None:
    contact_us_page.expect_form_matches_snapshot(assert_snapshot, "contact_us_form_new")


@then("the Contact Us form with the validation errors matches the visual snapshot")
def form_with_errors_snapshot(contact_us_page: ContactUsPage, assert_snapshot: AssertSnapshot) -> None:
    contact_us_page.expect_empty_form_errors()
    contact_us_page.expect_form_matches_snapshot(assert_snapshot, "contact_us_form_errors")


@then("the enquiry success page matches the visual snapshot")
def success_snapshot(contact_us_page: ContactUsPage, assert_snapshot: AssertSnapshot) -> None:
    contact_us_page.expect_success_matches_snapshot(assert_snapshot, "contact_us_success")

# endregion
# ==========================================================================================================
