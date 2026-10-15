import re
from pathlib import Path

import pytest
from playwright.sync_api import Dialog, Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from src.configuration.config import get_account_login_name, get_account_password
from src.pages.login_page import LoginPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "login.feature"))

# ==========================================================================================================
# region HELPERS & FIXTURES
# ==========================================================================================================

ACCOUNT_PATH = "/index.php?rt=account/account"
LONG_VALUE_LENGTH = 1000


def resolve_token(value: str) -> str:
    """Translate placeholders from the feature file into real values."""
    if value == "__VALID_LOGIN_NAME__":
        return get_account_login_name()
    if value == "__VALID_PASSWORD__":
        return get_account_password()
    if value == "__VALID_PASSWORD_UPPER__":
        password = get_account_password()
        # Without lowercase letters the "changed" password would be the valid one -> the test would be meaningless
        if password.upper() == password:
            pytest.skip("Configured password has no lowercase letters - case sensitivity cannot be checked")
        return password.upper()
    if value == "__EMPTY__":
        return ""
    if value == "__SPACES__":
        return "   "
    if value == "__LONG_1000__":
        return "a" * LONG_VALUE_LENGTH
    return value


@pytest.fixture
def captured_dialogs(page: Page) -> list[str]:
    """Collects messages of JS dialogs (alert/confirm/prompt) - used by the XSS checks."""
    captured: list[str] = []

    def on_dialog(dialog: Dialog) -> None:
        captured.append(dialog.message)
        dialog.dismiss()

    page.on("dialog", on_dialog)
    return captured


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================


@given("the user opens the login page", target_fixture="login_page")
def open_login_page(page: Page, captured_dialogs: list[str]) -> LoginPage:
    # captured_dialogs is requested here so the dialog listener is registered before any navigation
    login_page = LoginPage(page)
    login_page.open()
    login_page.expect_loaded()
    return login_page


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================


@when("the user logs in with the configured credentials")
def login_with_configured_credentials(login_page: LoginPage) -> None:
    login_page.login(get_account_login_name(), get_account_password())


@when(
    parsers.parse('the user submits login name "{login_name}" and password "{password}"')
)
def submit_login_credentials(login_page: LoginPage, login_name: str, password: str) -> None:
    login_page.login(resolve_token(login_name), resolve_token(password))


@when(
    parsers.parse(
        'the user types login name "{login_name}" and password "{password}" and presses Enter'
    )
)
def submit_login_credentials_with_enter(login_page: LoginPage, login_name: str, password: str) -> None:
    login_page.login_with_enter(resolve_token(login_name), resolve_token(password))


@when("the user opens the My Account page directly")
def open_account_page_directly(login_page: LoginPage) -> None:
    login_page.goto(ACCOUNT_PATH)


@when("the user opens password recovery")
def open_password_recovery(login_page: LoginPage) -> None:
    login_page.click_forgot_password()


@when("the user opens login name recovery")
def open_login_name_recovery(login_page: LoginPage) -> None:
    login_page.click_forgot_login()


@when("the user starts account registration")
def start_account_registration(login_page: LoginPage) -> None:
    login_page.start_registration()


@when("the user clicks the Home breadcrumb")
def click_home_breadcrumb(login_page: LoginPage) -> None:
    login_page.breadcrumb_links.first.click()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN: login result
# ==========================================================================================================


@then("the customer account page is displayed")
def customer_account_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/account(?:&|$)"))
    expect(page.locator("h1.heading1 .maintext")).to_contain_text("My Account")


@then("the logoff link is available")
def logoff_link_is_available(page: Page) -> None:
    # Proof that a session was really created
    expect(page.get_by_role("link", name="Logoff").first).to_be_visible()


@then("a login error is displayed")
def login_error_is_displayed(login_page: LoginPage) -> None:
    login_page.expect_error_visible()


@then("the login error informs about incorrect login or password")
def login_error_text(login_page: LoginPage) -> None:
    login_page.expect_error_contains("Incorrect login or password provided")


@then("the login page remains displayed")
def login_page_remains_displayed(login_page: LoginPage) -> None:
    login_page.expect_loaded()


@then("no JavaScript dialog was triggered")
def no_javascript_dialog_triggered(captured_dialogs: list[str]) -> None:
    assert captured_dialogs == [], f"Unexpected JS dialog(s): {captured_dialogs}"


@then(parsers.parse('the URL does not contain "{text}"'))
def url_does_not_contain(page: Page, text: str) -> None:
    assert text not in page.url, f"'{text}' found in URL: {page.url}"


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN: page content (UI)
# ==========================================================================================================


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
    # Password must be masked
    expect(login_page.password_input).to_have_attribute("type", "password")


@then("the login fields are empty")
def login_fields_are_empty(login_page: LoginPage) -> None:
    expect(login_page.login_name_input).to_have_value("")
    expect(login_page.password_input).to_have_value("")


@then("the login button is visible")
def login_button_is_visible(login_page: LoginPage) -> None:
    expect(login_page.login_button).to_be_visible()
    expect(login_page.login_button).to_have_attribute("type", "submit")


@then("the login form uses POST and contains a CSRF token")
def login_form_uses_post_and_csrf(login_page: LoginPage) -> None:
    expect(login_page.login_form).to_have_attribute("method", "post")
    expect(login_page.login_csrf_input).to_have_value(re.compile(r".+"))


@then("the password recovery links are visible")
def password_recovery_links_are_visible(login_page: LoginPage) -> None:
    expect(login_page.forgot_password_link).to_be_visible()
    expect(login_page.forgot_password_link).to_contain_text("Forgot your password?")
    expect(login_page.forgot_login_link).to_be_visible()
    expect(login_page.forgot_login_link).to_contain_text("Forgot your login?")


@then("the new customer registration form is visible")
def new_customer_registration_form_is_visible(login_page: LoginPage) -> None:
    expect(login_page.new_customer_heading).to_contain_text("I am a new customer.")
    expect(login_page.register_form).to_be_visible()
    expect(login_page.register_account_radio).to_be_visible()
    expect(login_page.continue_button).to_be_visible()


@then("the register account option is selected by default")
def register_account_option_selected_by_default(login_page: LoginPage) -> None:
    expect(login_page.register_account_radio).to_be_checked()


@then(parsers.parse('the breadcrumb trail is "{trail}"'))
def breadcrumb_trail_is(login_page: LoginPage, trail: str) -> None:
    expect(login_page.breadcrumb_links).to_have_text(trail.split(" > "))


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN: navigation
# ==========================================================================================================


@then("the password recovery page is displayed")
def password_recovery_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/forgotten/password"))


@then("the login name recovery page is displayed")
def login_name_recovery_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/forgotten/loginname"))


@then("the account registration page is displayed")
def account_registration_page_is_displayed(page: Page) -> None:
    expect(page).to_have_url(re.compile(r"rt=account/create"))


@then("the home page is displayed")
def home_page_is_displayed(page: Page) -> None:
    # Home has no "rt=" route in the URL
    expect(page).not_to_have_url(re.compile(r"rt="))

# endregion
# ==========================================================================================================
