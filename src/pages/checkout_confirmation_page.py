import re

from playwright.sync_api import Locator, Page, expect

from src.pages.base_page import BasePage


class CheckoutConfirmationPage(BasePage):
    """Checkout confirmation page (rt=checkout/confirm)."""

    PATH_PATTERN = re.compile(r"rt=checkout/confirm")
    TITLE = "Checkout Confirmation"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.locator("h1.heading1 .maintext")

        self.shipping_row = page.locator("table.confirm_shippment_options tbody tr")
        self.shipping_contact = self.shipping_row.locator("td").nth(0)
        self.shipping_address = self.shipping_row.locator("td address")
        self.shipping_method = self.shipping_row.locator("td").nth(2)

        self.payment_row = page.locator("table.confirm_payment_options tbody tr")
        self.payment_contact = self.payment_row.locator("td").nth(0)
        self.payment_address = self.payment_row.locator("td address")
        self.payment_method = self.payment_row.locator("td").nth(2)

        self.product_rows = page.locator("table.confirm_products tbody tr")
        self.totals_rows = page.locator(".confirm_total .cart-info table tr")
        self.order_summary = page.locator(".column_right .sidewidt")
        self.order_summary_product_rows = self.order_summary.locator(":scope > table").first.locator("tbody tr")
        self.order_summary_totals_rows = self.order_summary.locator(":scope > table").nth(1).locator("tbody tr")

        self.payment_wait = page.locator("#payment .wait")
        self.action_buttons = page.locator("#payment .action-buttons")
        self.confirm_order_button = page.locator("#checkout_btn")

    @staticmethod
    def normalized_text(locator: Locator) -> str:
        return " ".join(locator.inner_text().split())

    def product_row(self, name: str) -> Locator:
        return self.product_rows.filter(has=self.page.locator("a.checkout_heading", has_text=re.compile(rf"^{re.escape(name)}$")))

    def summary_product_row(self, name: str) -> Locator:
        return self.order_summary_product_rows.filter(
            has=self.page.locator("a", has_text=re.compile(rf"^{re.escape(name)}$"))
        )

    def total_value(self, label: str) -> Locator:
        return self.totals_rows.filter(has_text=label).locator("td").nth(1)

    def summary_total_value(self, label: str) -> Locator:
        return self.order_summary_totals_rows.filter(has_text=label).locator("td").nth(1)

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.PATH_PATTERN)
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.TITLE)

    def expect_contact_details(self, contact: Locator, address: Locator) -> None:
        assert self.normalized_text(contact) == "Bart Simpson 1 (804) 222-1111"
        assert self.normalized_text(address) == "Porkland 123/4 Icberg 567/8 New York Slaskie 41-707 Poland"

    def expect_shipping_and_payment(self) -> None:
        self.expect_contact_details(self.shipping_contact, self.shipping_address)
        expect(self.shipping_method).to_have_text("Flat Shipping Rate")
        self.expect_contact_details(self.payment_contact, self.payment_address)
        expect(self.payment_method).to_have_text("Cash On Delivery")

    def expect_product(self, name: str, unit_price: str, quantity: int, line_total: str) -> None:
        row = self.product_row(name)
        expect(row).to_have_count(1)
        expect(row.locator("td").nth(2)).to_have_text(unit_price)
        expect(row.locator("td").nth(3)).to_have_text(str(quantity))
        expect(row.locator("td").nth(4)).to_have_text(line_total)

    def expect_order_summary_product(self, name: str, quantity: int, unit_price: str) -> None:
        row = self.summary_product_row(name)
        expect(row).to_have_count(1)
        expect(row.locator("td").nth(0)).to_contain_text(f"{quantity} x")
        expect(row.locator("td").nth(1)).to_have_text(unit_price)

    def expect_totals(self, subtotal: str, shipping: str, total: str) -> None:
        expected = {
            "Sub-Total:": subtotal,
            "Flat Shipping Rate:": shipping,
            "Total:": total,
        }
        for label, amount in expected.items():
            expect(self.total_value(label)).to_have_text(amount)
            expect(self.summary_total_value(label)).to_have_text(amount)

    def wait_until_confirmation_is_ready(self) -> None:
        expect(self.confirm_order_button).to_be_visible(timeout=15000)
        expect(self.confirm_order_button).to_be_enabled(timeout=15000)
        expect(self.payment_wait).to_be_hidden(timeout=15000)

    def confirm_order(self) -> None:
        self.wait_until_confirmation_is_ready()
        self.confirm_order_button.click()
