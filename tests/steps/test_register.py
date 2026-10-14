import re

import pytest
from faker import Faker
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from src.configuration import config
from src.pages.account.account_success_page import AccountSuccessPage
from src.pages.register_page import RegisterPage

scenarios("../features/register.feature")

fake = Faker("en_GB")

# ==========================================================================================================
# region DATA
# ==========================================================================================================

# Label used in the feature file ➤ field name (id is AccountFrm_<name>)
LABEL_TO_FIELD = {
    "First Name": "firstname",
    "Last Name": "lastname",
    "E-Mail": "email",
    "Telephone": "telephone",
    "Fax": "fax",
    "Company": "company",
    "Address 1": "address_1",
    "Address 2": "address_2",
    "City": "city",
    "Region / State": "zone_id",
    "ZIP Code": "postcode",
    "Login name": "loginname",
    "Password": "password",
    "Password Confirm": "confirm",
}


def build_valid_user() -> dict:
    """Random, valid data of a new customer (e-mail, login and password come from RegisterPage generators)."""
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": RegisterPage.generate_email(),
        "telephone": fake.phone_number(),
        "fax": fake.phone_number(),
        "company": fake.company(),
        "address_1": fake.street_address(),
        "address_2": fake.secondary_address(),
        "city": fake.city(),
        "postcode": fake.postcode(),
        "country": "United Kingdom",
        "region": "Greater London",
        "login_name": RegisterPage.generate_login_name(),
        "password": RegisterPage.generate_password(),
    }


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def register_page(page: Page) -> RegisterPage:
    return RegisterPage(page)


@pytest.fixture
def valid_user() -> dict:
    return build_valid_user()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region HELPERS
# ==========================================================================================================

def _set_field(register_page: RegisterPage, label: str, value: str) -> None:
    name = LABEL_TO_FIELD[label]
    if name == "zone_id":
        # "--- Please Select ---" has value FALSE
        if value == "":
            register_page.region_select.select_option(value="FALSE")
        else:
            register_page.select_region(value)
    else:
        register_page.field(name).fill(value)
        # Changing the password alone would also trigger the "confirm" error - keep both in sync
        if name == "password":
            register_page.password_confirm_input.fill(value)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the registration page is open")
def registration_page_open(register_page: RegisterPage):
    register_page.goto()
    register_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("I fill in the required fields with valid data")
def fill_required_fields(register_page: RegisterPage, valid_user: dict):
    register_page.fill_personal_details(valid_user["first_name"], valid_user["last_name"], valid_user["email"])
    register_page.fill_address(
        valid_user["address_1"], valid_user["city"], valid_user["postcode"],
        valid_user["country"], valid_user["region"],
    )
    register_page.fill_login_details(valid_user["login_name"], valid_user["password"])


@when("I fill in the optional fields with valid data")
def fill_optional_fields(register_page: RegisterPage, valid_user: dict):
    register_page.telephone_input.fill(valid_user["telephone"])
    register_page.fax_input.fill(valid_user["fax"])
    register_page.company_input.fill(valid_user["company"])
    register_page.address_2_input.fill(valid_user["address_2"])


@when("I subscribe to the newsletter")
def subscribe_newsletter(register_page: RegisterPage):
    register_page.subscribe_newsletter(True)


@when("I accept the privacy policy")
def accept_privacy_policy(register_page: RegisterPage):
    register_page.accept_privacy_policy()


@when("I click Continue")
def click_continue(register_page: RegisterPage):
    register_page.click_continue()


@when(parsers.parse('I leave the "{label}" field empty'))
def leave_field_empty(register_page: RegisterPage, label: str):
    _set_field(register_page, label, "")


@when(parsers.parse('I set the "{label}" field to "{value}"'))
def set_field(register_page: RegisterPage, label: str, value: str):
    _set_field(register_page, label, value)


@when(parsers.parse('I set the "{label}" field to a value of {length} characters'))
def set_field_with_length(register_page: RegisterPage, label: str, length: str):
    _set_field(register_page, label, "a" * int(length))


@when("I use the e-mail address of the existing account")
def use_existing_email(register_page: RegisterPage):
    register_page.email_input.fill(config.get_account_e_mail())


@when("I use the login name of the existing account")
def use_existing_login_name(register_page: RegisterPage):
    register_page.login_name_input.fill(config.get_account_login_name())


@when("I open the privacy policy")
def open_privacy_policy(register_page: RegisterPage):
    register_page.open_privacy_policy()


@when("I close the privacy policy")
def close_privacy_policy(register_page: RegisterPage):
    register_page.close_privacy_policy()


@when("I click the login page link")
def click_login_page_link(register_page: RegisterPage):
    register_page.click_login_page_link()


@when(parsers.parse('I select the country "{country}"'))
def select_country(register_page: RegisterPage, country: str):
    register_page.select_country(country)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then("the account created page is displayed")
def account_created_page_displayed(register_page: RegisterPage):
    AccountSuccessPage(register_page.page).expect_loaded()


@then("I stay on the registration page")
def stay_on_registration_page(register_page: RegisterPage):
    expect(register_page.page).to_have_url(re.compile(r"rt=account/create"))
    register_page.expect_loaded()


@then("errors are shown under all required fields")
def errors_under_all_required_fields(register_page: RegisterPage):
    for name, message in RegisterPage.ERRORS.items():
        register_page.expect_field_error(name, message)
    expect(register_page.invalid_form_groups).to_have_count(len(RegisterPage.ERRORS))


@then("all required field errors are also listed in the alert")
def required_errors_listed_in_alert(register_page: RegisterPage):
    for message in RegisterPage.ERRORS.values():
        register_page.expect_error_alert(message)


@then("the privacy policy error is shown")
def privacy_policy_error_shown(register_page: RegisterPage):
    register_page.expect_privacy_policy_error()


@then("no field errors are shown")
def no_field_errors(register_page: RegisterPage):
    register_page.expect_no_field_errors()


@then(parsers.parse('the "{label}" field shows its validation error'))
def field_shows_validation_error(register_page: RegisterPage, label: str):
    name = LABEL_TO_FIELD[label]
    register_page.expect_field_error(name, RegisterPage.ERRORS[name])


@then(parsers.parse('only the "{label}" field has an error'))
def only_field_has_error(register_page: RegisterPage, label: str):
    assert register_page.fields_with_errors() == [LABEL_TO_FIELD[label]]


@then(parsers.parse('the error alert contains "{text}"'))
def error_alert_contains(register_page: RegisterPage, text: str):
    register_page.expect_error_alert(text)


@then("the privacy policy window is displayed")
def privacy_policy_window_displayed(register_page: RegisterPage):
    register_page.expect_privacy_policy_visible()


@then("the privacy policy window is not displayed")
def privacy_policy_window_not_displayed(register_page: RegisterPage):
    expect(register_page.privacy_policy_modal).not_to_be_visible()


@then("the login page is displayed")
def login_page_displayed(register_page: RegisterPage):
    expect(register_page.page).to_have_url(re.compile(r"rt=account/login"))


@then(parsers.parse('the region list contains "{region}"'))
def region_list_contains(register_page: RegisterPage, region: str):
    expect(register_page.region_select.locator("option", has_text=region)).to_have_count(1)


@then(parsers.parse('the region list does not contain "{region}"'))
def region_list_does_not_contain(register_page: RegisterPage, region: str):
    expect(register_page.region_select.locator("option", has_text=region)).to_have_count(0)

# endregion
# ==========================================================================================================
