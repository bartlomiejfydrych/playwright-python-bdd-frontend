import re

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class OrderSuccessPage(BasePage):
    """Order success page (rt=checkout/success)."""

    PATH_PATTERN = re.compile(r"rt=checkout/success")
    TITLE = "Your Order Has Been Processed!"
    ORDER_CREATED_PATTERN = re.compile(r"Your order #\d+ has been created!")

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.locator("h1.heading1 .maintext")
        self.content = page.locator(".contentpanel section.mb40")
        self.paragraphs = self.content.locator("p")
        self.order_created_message = self.paragraphs.filter(has_text=self.ORDER_CREATED_PATTERN)
        self.invoice_message = self.paragraphs.filter(has_text="You can view your order details")
        self.questions_message = self.paragraphs.filter(has_text="Please direct any questions")
        self.thank_you_message = self.paragraphs.filter(has_text="Thank you for shopping with us!")
        self.continue_button = page.locator("a[title='Continue']")

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.PATH_PATTERN)
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.TITLE)

    def expect_order_processed(self) -> None:
        self.expect_loaded()
        expect(self.order_created_message).to_have_text(self.ORDER_CREATED_PATTERN)
        expect(self.invoice_message).to_contain_text(
            "You can view your order details by going to the"
        )
        expect(self.invoice_message.locator("a")).to_have_text("invoice page")
        expect(self.questions_message).to_contain_text(
            "Please direct any questions you have to the"
        )
        expect(self.questions_message.locator("a")).to_have_text("store owner")
        expect(self.thank_you_message).to_have_text("Thank you for shopping with us!")

    def continue_shopping(self) -> None:
        self.continue_button.click()
