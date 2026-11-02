import re

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class LogoutPage(BasePage):
    """
    Confirmation page shown after logging out (rt=account/logout, title: Account Logout):
    heading, two messages and the Continue button.
    The page is displayed already in the logged-out state (header shows "Login or register"),
    so it inherits from BasePage, not from AccountBasePage (there is no "My Account" side menu).
    Everything else (header, footer, search box...) lives in BasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    # UWAGA: wejście na ten adres przy zalogowanej sesji WYLOGOWUJE użytkownika
    PATH = "/index.php?rt=account/logout"
    URL_PATTERN = re.compile(r"rt=account/logout")

    TITLE = "Account Logout"
    HEADING_TEXT = "Account Logout"

    LOGGED_OFF_MESSAGE = "You have been logged off your account. It is now safe to leave the computer."
    CART_SAVED_MESSAGE = (
        "Your shopping cart has been saved, the items inside it will be restored "
        "whenever you log back into your account."
    )

    # Breadcrumbs: Home > Account > Logout
    BREADCRUMB_TEXTS = ["Home", "Account", "Logout"]

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region LOCATORS
    # ==========================================================================================================

    def __init__(self, page: Page):
        super().__init__(page)

        # ---
        # MID
        # ---

        # Heading (icon: thumbs-up)
        self.heading = page.locator("h1.heading1 .maintext")
        self.heading_icon = page.locator("h1.heading1 .maintext i.fa-thumbs-up")

        # Breadcrumbs: Home > Account > Logout
        # (the "Account" link leads to account/account, which for a logged-out user redirects to the login page)
        self.breadcrumbs = page.locator("section.breadcrumbs ul.breadcrumb")
        self.breadcrumb_links = page.locator("section.breadcrumbs ul.breadcrumb a")
        self.breadcrumb_home_link = page.locator("section.breadcrumbs ul.breadcrumb a:has(i.fa-home)")
        self.breadcrumb_account_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='account/account']")
        self.breadcrumb_logout_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='account/logout']")

        # Content panel (są też puste <p></p>, dlatego :not(:empty))
        self.content_section = page.locator(".contentpanel section.mb40")
        self.message_paragraphs = page.locator(".contentpanel section.mb40 p:not(:empty)")
        self.logged_off_message = self.message_paragraphs.nth(0)
        self.cart_saved_message = self.message_paragraphs.nth(1)
        self.continue_button = page.locator(".contentpanel section.mb40 a.btn[title='Continue']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ------------------
    # Actions: main part
    # ------------------

    def open(self) -> None:
        self.goto(self.PATH)

    def click_continue(self) -> None:
        self.continue_button.click()

    # ---------------------
    # Actions: breadcrumbs
    # ---------------------

    def click_breadcrumb_home(self) -> None:
        self.breadcrumb_home_link.click()

    def click_breadcrumb_account(self) -> None:
        self.breadcrumb_account_link.click()

    # --------
    # Readings
    # --------

    def message_texts(self) -> list[str]:
        return [t.strip() for t in self.message_paragraphs.all_inner_texts()]

    def breadcrumb_texts(self) -> list[str]:
        return [t.strip() for t in self.breadcrumb_links.all_inner_texts()]

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.URL_PATTERN)
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.HEADING_TEXT)

    def expect_messages(self) -> None:
        expect(self.message_paragraphs).to_have_count(2)
        expect(self.logged_off_message).to_have_text(self.LOGGED_OFF_MESSAGE)
        expect(self.cart_saved_message).to_have_text(self.CART_SAVED_MESSAGE)

    def expect_breadcrumbs(self) -> None:
        expect(self.breadcrumb_links).to_have_text(self.BREADCRUMB_TEXTS)

    def expect_continue_button_visible(self) -> None:
        expect(self.continue_button).to_be_visible()

    def expect_logout_confirmed(self) -> None:
        # Whole page: the content of the logout page + the header in the logged-out state (from BasePage)
        self.expect_loaded()
        self.expect_messages()
        self.expect_continue_button_visible()
        self.expect_logged_out()

    # endregion
    # ==========================================================================================================
