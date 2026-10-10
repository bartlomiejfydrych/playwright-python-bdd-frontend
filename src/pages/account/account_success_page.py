import re

from playwright.sync_api import Page, expect

from src.pages.account.account_base_page import AccountBasePage


class AccountSuccessPage(AccountBasePage):
    """
    Confirmation page shown after a successful registration (rt=account/success):
    heading, confirmation message and Continue button.
    Breadcrumbs and the "My Account" side menu come from AccountBasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/success")

    HEADING_TEXT = "Your Account Has Been Created!"
    CONGRATULATIONS_TEXT = "Congratulations! Your new account has been successfully created!"
    CONFIRMATION_SENT_TEXT = "A confirmation has been sent to the provided email address."

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

        # Breadcrumbs: Home > Account > Success (the last item is specific to this page)
        self.breadcrumb_success_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='account/success']")

        # Content panel
        self.heading_icon = page.locator("h1.heading1 .maintext i.fa-thumbs-up")
        self.message_paragraphs = page.locator(".contentpanel section p:not(:empty)")
        self.contact_us_link = page.locator(".contentpanel section p a[href*='content/contact']")
        self.continue_button = page.locator(".contentpanel a.btn[title='Continue']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ------------------
    # Actions: main part
    # ------------------

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_contact_us_in_message(self) -> None:
        self.contact_us_link.click()

    # --------
    # Readings
    # --------

    def message_text(self) -> str:
        return " ".join(t.strip() for t in self.message_paragraphs.all_inner_texts())

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
        expect(self.heading).to_have_text(self.HEADING_TEXT)

    def expect_confirmation_message(self) -> None:
        expect(self.message_paragraphs.first).to_contain_text(self.CONGRATULATIONS_TEXT)
        expect(self.message_paragraphs.nth(3)).to_contain_text(self.CONFIRMATION_SENT_TEXT)

    # endregion
    # ==========================================================================================================
