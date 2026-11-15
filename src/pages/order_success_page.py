import re

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class OrderSuccessPage(BasePage):
    """Order success page (rt=checkout/success), "Your Order Has Been Processed!", shown after Confirm Order."""

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=checkout/success")
    TITLE = "Your Order Has Been Processed!"

    # The order number changes with every order, so only its format is checked
    ORDER_CREATED_PATTERN = re.compile(r"Your order #\d+ has been created!")

    # Order processing (spinner on the confirmation page) can take longer than the default 5 s
    PROCESSING_TIMEOUT = 30_000

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

        self.heading = page.locator("h1.heading1 .maintext")
        self.content = page.locator(".contentpanel section.mb40")
        self.paragraphs = self.content.locator("p")
        self.order_created_message = self.paragraphs.filter(has_text=self.ORDER_CREATED_PATTERN)
        self.invoice_message = self.paragraphs.filter(has_text="You can view your order details")
        self.invoice_link = self.invoice_message.locator("a")
        self.questions_message = self.paragraphs.filter(has_text="Please direct any questions")
        self.store_owner_link = self.questions_message.locator("a")
        self.thank_you_message = self.paragraphs.filter(has_text="Thank you for shopping with us!")
        self.continue_button = page.locator("a[title='Continue']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # -------------
    # Actions: page
    # -------------

    def continue_shopping(self) -> None:
        self.continue_button.click()

    # --------
    # Readings
    # --------

    def order_number(self) -> str:
        return re.search(r"#(\d+)", self.order_created_message.inner_text()).group(1)

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self, timeout: float | None = None) -> None:
        expect(self.page).to_have_url(self.URL_PATTERN, timeout=timeout)
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.TITLE)

    def expect_invoice_link_matches_order(self) -> None:
        # The invoice link must point to the order number shown in the message
        expect(self.invoice_link).to_have_attribute("href", re.compile(rf"order_id={self.order_number()}$"))

    def expect_order_processed(self) -> None:
        self.expect_loaded(timeout=self.PROCESSING_TIMEOUT)
        expect(self.order_created_message).to_have_text(self.ORDER_CREATED_PATTERN)
        expect(self.invoice_message).to_contain_text("You can view your order details by going to the")
        expect(self.invoice_link).to_have_text("invoice page")
        expect(self.questions_message).to_contain_text("Please direct any questions you have to the")
        expect(self.store_owner_link).to_have_text("store owner")
        expect(self.thank_you_message).to_have_text("Thank you for shopping with us!")
        self.expect_invoice_link_matches_order()

    # endregion
    # ==========================================================================================================
