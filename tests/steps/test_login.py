import re
from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when
from playwright.sync_api import Page, expect

from src.configuration.config import get_account_login_name, get_account_password
from src.pages.login_page import LoginPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "login.feature"))


@given("the user opens the login page", target_fixture="login_page")
def open_login_page(page: Page) -> LoginPage:
    login_page = LoginPage(page)
    login_page.open()
    login_page.expect_loaded()
    return login_page


@when("the user logs in with the configured credentials")
def login_with_configured_credentials(login_page: LoginPage) -> None:
    login_page.login(
        get_account_login_name(),
        get_account_password(),
    )


@when(
    parsers.parse('the user submits login name "{login_name}" and password "{password}"')
)
def submit_login_credentials(
        login_page: LoginPage,
        login_name: str,
        password: str,
) -> None:
    # Feature-file tokens are resolved to the valid .env credentials here.
    if login_name == "<VALID_LOGIN_NAME>":
        login_name = get_account_login_name()
    if password == "<VALID_PASSWORD>":
        password = get_account_password()
    if login_name == "__EMPTY__":
        login_name = ""
    if password == "__EMPTY__":
        password = ""

    login_page.login(login_name, password)


@then("the customer account page is displayed")
def customer_account_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/account(?:&|$)"))
    expect(page.locator("h1")).to_contain_text("My Account")


@then("a login error is displayed")
def login_error_is_displayed(login_page: LoginPage) -> None:
    login_page.expect_error_visible()


@then("the login page remains displayed")
def login_page_remains_displayed(login_page: LoginPage) -> None:
    expect(login_page.page).to_have_url(re.compile(r"rt=account/login"))
    expect(login_page.login_form).to_be_visible()


@then("the login page is displayed")
def login_page_is_displayed(login_page: LoginPage) -> None:
    login_page.expect_loaded()


@then("the returning customer form is visible")
def returning_customer_form_is_visible(login_page: LoginPage) -> None:
    expect(login_page.returning_customer_heading).to_contain_text("Returning Customer")
    expect(login_page.login_form).to_be_visible()


@then("the login name and password fields are visible")
def login_fields_are_visible(login_page: LoginPage) -> None:
    expect(login_page.login_name_input).to_be_visible()
    expect(login_page.password_input).to_be_visible()
    expect(login_page.login_name_input).to_have_attribute("name", "loginname")
    expect(login_page.password_input).to_have_attribute("name", "password")
    expect(login_page.password_input).to_have_attribute("type", "password")


@then("the login button is visible")
def login_button_is_visible(login_page: LoginPage) -> None:
    expect(login_page.login_button).to_be_visible()
    expect(login_page.login_button).to_have_attribute("type", "submit")


@then("the password recovery links are visible")
def password_recovery_links_are_visible(login_page: LoginPage) -> None:
    expect(login_page.forgot_password_link).to_be_visible()
    expect(login_page.forgot_login_link).to_be_visible()


@then("the new customer registration form is visible")
def new_customer_registration_form_is_visible(login_page: LoginPage) -> None:
    expect(login_page.new_customer_heading).to_contain_text("I am a new customer.")
    expect(login_page.register_form).to_be_visible()
    expect(login_page.register_account_radio).to_be_visible()
    expect(login_page.continue_button).to_be_visible()


@when("the user opens password recovery")
def open_password_recovery(login_page: LoginPage) -> None:
    login_page.click_forgot_password()


@then("the password recovery page is displayed")
def password_recovery_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/forgotten/password"))


@when("the user opens login name recovery")
def open_login_name_recovery(login_page: LoginPage) -> None:
    login_page.click_forgot_login()


@then("the login name recovery page is displayed")
def login_name_recovery_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/forgotten/loginname"))


@when("the user starts account registration")
def start_account_registration(login_page: LoginPage) -> None:
    login_page.start_registration()


@then("the account registration page is displayed")
def account_registration_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/create"))
