import re

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    """Strona logowania /index.php?rt=account/login (tytuł: Account Login)."""

    PATH = "/index.php?rt=account/login"
    TITLE = "Account Login"

    def __init__(self, page: Page):
        super().__init__(page)

        # --- Nagłówek i okruszki ---
        self.heading = page.locator("h1.heading1 .maintext")
        self.breadcrumb_links = page.locator("ul.breadcrumb a")

        # --- Nowy klient (formularz #accountFrm) ---
        self.new_customer_heading = page.locator(".newcustomer h2.heading2")
        self.register_form = page.locator("#accountFrm")
        self.register_account_radio = page.locator("#accountFrm_accountregister")
        self.continue_button = page.locator("#accountFrm button[title='Continue']")

        # --- Powracający klient (formularz #loginFrm) ---
        self.returning_customer_heading = page.locator(".returncustomer h2.heading2")
        self.login_form = page.locator("#loginFrm")
        self.login_name_input = page.locator("#loginFrm_loginname")
        self.password_input = page.locator("#loginFrm_password")
        self.login_button = page.locator("#loginFrm button[title='Login']")
        self.forgot_password_link = page.locator("a[href*='forgotten/password']")
        self.forgot_login_link = page.locator("a[href*='forgotten/loginname']")

        # --- Komunikat błędu po nieudanym logowaniu ---
        # UWAGA: w statycznym HTML go nie ma, klasy to założenie AbanteCart
        # (div.alert.alert-error). Zweryfikuj po pierwszym nieudanym logowaniu.
        self.error_alert = page.locator(".alert-error, .alert-danger")

    # ------------------------------------------------------------------ #
    # Akcje
    # ------------------------------------------------------------------ #
    def open(self) -> "LoginPage":
        self.goto(self.PATH)
        return self

    def fill_login_name(self, login_name: str) -> None:
        self.login_name_input.fill(login_name)

    def fill_password(self, password: str) -> None:
        self.password_input.fill(password)

    def click_login(self) -> None:
        self.login_button.click()

    def login(self, login_name: str, password: str) -> None:
        self.fill_login_name(login_name)
        self.fill_password(password)
        self.click_login()

    def choose_register_account(self) -> None:
        self.register_account_radio.check()

    def click_continue(self) -> None:
        self.continue_button.click()

    def start_registration(self) -> None:
        self.choose_register_account()
        self.click_continue()

    def click_forgot_password(self) -> None:
        self.forgot_password_link.click()

    def click_forgot_login(self) -> None:
        self.forgot_login_link.click()

    # ------------------------------------------------------------------ #
    # Odczyty
    # ------------------------------------------------------------------ #
    def breadcrumb_texts(self) -> list[str]:
        return [t.strip() for t in self.breadcrumb_links.all_inner_texts()]

    def error_text(self) -> str:
        return self.error_alert.first.inner_text().strip()

    # ------------------------------------------------------------------ #
    # Asercje pomocnicze
    # ------------------------------------------------------------------ #
    def expect_loaded(self) -> None:
        expect(self.page).to_have_title(self.TITLE)
        expect(self.page).to_have_url(re.compile(r"rt=account/login"))
        expect(self.heading).to_contain_text("Account Login")
        expect(self.login_form).to_be_visible()
        expect(self.register_form).to_be_visible()

    def expect_error_visible(self) -> None:
        expect(self.error_alert.first).to_be_visible()
