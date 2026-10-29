from pathlib import Path

import pytest
from faker import Faker
from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.contact_us_page import ContactUsPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "contact_us.feature"))

fake = Faker("en_GB")

FIELD_LABELS = {
    "First name": "first_name",
    "Email": "email",
    "Enquiry": "enquiry",
}


@pytest.fixture
def contact_us_page(logged_in_page: Page) -> ContactUsPage:
    return ContactUsPage(logged_in_page)


@pytest.fixture
def valid_enquiry() -> dict[str, str]:
    return {
        "first_name": fake.first_name(),
        "email": "contact.us.automation@example.com",
        "enquiry": "This is an automated test enquiry. Please disregard this message.",
    }


@given("the customer is logged in and opens the Contact Us page")
def customer_opens_contact_us_page(contact_us_page: ContactUsPage) -> None:
    contact_us_page.expect_logged_in()
    contact_us_page.open()
    contact_us_page.expect_loaded()


@then("the store address and telephone number are correct")
def store_contact_details_are_correct(contact_us_page: ContactUsPage) -> None:
    contact_us_page.expect_store_contact_details()


@when("the customer fills in the Contact Us form with valid data")
def fill_contact_form(contact_us_page: ContactUsPage, valid_enquiry: dict[str, str]) -> None:
    contact_us_page.fill_form(**valid_enquiry)


@when("the customer submits the enquiry")
def submit_enquiry(contact_us_page: ContactUsPage) -> None:
    contact_us_page.click_submit()


@when("the customer resets the form")
def reset_contact_form(contact_us_page: ContactUsPage) -> None:
    contact_us_page.click_reset()


@when(parsers.parse('the customer clears the "{label}" field'))
def clear_contact_field(contact_us_page: ContactUsPage, label: str) -> None:
    contact_us_page.field_input(FIELD_LABELS[label]).fill("")


@when(parsers.parse('the customer sets the "{label}" field to "{value}"'))
def set_contact_field(contact_us_page: ContactUsPage, label: str, value: str) -> None:
    contact_us_page.field_input(FIELD_LABELS[label]).fill(value)


@when(parsers.parse("the customer sets the \"{label}\" field to a value of {length:d} characters"))
def set_contact_field_length(contact_us_page: ContactUsPage, label: str, length: int) -> None:
    contact_us_page.field_input(FIELD_LABELS[label]).fill("a" * length)


@then("the enquiry success page is displayed")
def enquiry_success_page_displayed(contact_us_page: ContactUsPage) -> None:
    contact_us_page.expect_success_loaded()


@then("all Contact Us form fields are empty")
def contact_form_fields_are_empty(contact_us_page: ContactUsPage) -> None:
    contact_us_page.expect_fields_empty()


@then("the Contact Us form remains open")
def contact_form_remains_open(contact_us_page: ContactUsPage) -> None:
    contact_us_page.expect_form_page_still_open()


@then("validation errors are displayed for all fields")
def validation_errors_displayed_for_all_fields(contact_us_page: ContactUsPage) -> None:
    for field in ContactUsPage.FIELDS:
        contact_us_page.expect_field_error_visible(field)


@then(parsers.parse('a validation error is displayed for the "{label}" field'))
def validation_error_displayed_for_field(contact_us_page: ContactUsPage, label: str) -> None:
    contact_us_page.expect_field_error_visible(FIELD_LABELS[label])
