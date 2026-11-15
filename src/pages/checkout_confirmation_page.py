import re

from playwright.sync_api import Locator, Page, expect

from src.configuration import config
from src.pages.base_page import BasePage


class CheckoutConfirmationPage(BasePage):
    """
    "Checkout Confirmation" page (rt=checkout/confirm).
    Sections: Shipping, Payment, Items in your cart, totals, Confirm Order button and the Order Summary side block.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=checkout/confirm")
    TITLE = "Checkout Confirmation"

    SHIPPING_METHOD = "Flat Shipping Rate"
    PAYMENT_METHOD = "Cash On Delivery"

    # Labels in the totals tables (the text includes a colon)
    SUBTOTAL_LABEL = "Sub-Total:"
    SHIPPING_LABEL = "Flat Shipping Rate:"
    TOTAL_LABEL = "Total:"

    # Confirming the order calls the payment extension via AJAX, so it can take longer than the default 5 s
    CONFIRM_READY_TIMEOUT = 15_000

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

        # Shipping: td 0 = name + phone, td 1 = address, td 2 = shipping method
        self.shipping_row = page.locator("table.confirm_shippment_options tbody tr")
        self.shipping_contact = self.shipping_row.locator("td").nth(0)
        self.shipping_address = self.shipping_row.locator("td address")
        self.shipping_method = self.shipping_row.locator("td").nth(2)

        # Payment: same layout as shipping, td 2 = payment method
        self.payment_row = page.locator("table.confirm_payment_options tbody tr")
        self.payment_contact = self.payment_row.locator("td").nth(0)
        self.payment_address = self.payment_row.locator("td address")
        self.payment_method = self.payment_row.locator("td").nth(2)

        # Items in your cart: td 0 = image, 1 = name, 2 = unit price, 3 = quantity, 4 = line total
        self.product_rows = page.locator("table.confirm_products tbody tr")
        self.totals_rows = page.locator(".confirm_total .cart-info table tr")

        # Confirm Order (#payment is filled by AJAX: first a spinner (.wait), then the buttons)
        self.payment_wait = page.locator("#payment .wait")
        self.action_buttons = page.locator("#payment .action-buttons")
        self.confirm_order_button = page.locator("#checkout_btn")

        # ------------------------
        # RIGHT: Order Summary box
        # ------------------------

        # First table = products ("3 x name" | price), second table = totals
        self.order_summary = page.locator(".column_right .sidewidt")
        self.order_summary_product_rows = self.order_summary.locator(":scope > table").first.locator("tbody tr")
        self.order_summary_totals_rows = self.order_summary.locator(":scope > table").nth(1).locator("tbody tr")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def product_row(self, name: str) -> Locator:
        # Exact match on the name link (has_text would also match a longer name containing this one)
        return self.product_rows.filter(
            has=self.page.locator("a.checkout_heading", has_text=re.compile(rf"^{re.escape(name)}$"))
        )

    def summary_product_row(self, name: str) -> Locator:
        return self.order_summary_product_rows.filter(
            has=self.page.locator("a", has_text=re.compile(rf"^{re.escape(name)}$"))
        )

    def total_value(self, label: str) -> Locator:
        # Anchored regex: a plain has_text="Total:" would also match the "Sub-Total:" row
        return self.totals_rows.filter(has_text=re.compile(rf"^\s*{re.escape(label)}")).locator("td").nth(1)

    def summary_total_value(self, label: str) -> Locator:
        return self.order_summary_totals_rows.filter(
            has_text=re.compile(rf"^\s*{re.escape(label)}")
        ).locator("td").nth(1)

    # -------------------------
    # Expected data (from .env)
    # -------------------------

    @staticmethod
    def expected_contact() -> str:
        return f"{config.get_account_first_name()} {config.get_account_last_name()} {config.get_account_telephone()}"

    @staticmethod
    def expected_address() -> str:
        # The company is not shown in the address block, only in the contact data; empty address 2 is skipped
        parts = [
            config.get_account_address_1(),
            config.get_account_address_2(),
            f"{config.get_account_city()} {config.get_account_region_state()} {config.get_account_zip_code()}",
            config.get_account_country(),
        ]
        return " ".join(part for part in parts if part)

    # --------------
    # Actions: order
    # --------------

    def wait_until_confirmation_is_ready(self) -> None:
        # The button is hidden and disabled (with a spinner inside) until the payment block is loaded
        expect(self.payment_wait).to_be_hidden(timeout=self.CONFIRM_READY_TIMEOUT)
        expect(self.confirm_order_button).to_be_visible(timeout=self.CONFIRM_READY_TIMEOUT)
        expect(self.confirm_order_button).to_be_enabled(timeout=self.CONFIRM_READY_TIMEOUT)

    def confirm_order(self) -> None:
        self.wait_until_confirmation_is_ready()
        self.confirm_order_button.click()

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
        expect(self.heading).to_have_text(self.TITLE)

    def expect_contact_details(self, contact: Locator, address: Locator) -> None:
        # to_have_text normalizes whitespace, so <br> and line breaks are not a problem
        expect(contact).to_have_text(self.expected_contact())
        expect(address).to_have_text(self.expected_address())

    def expect_shipping_and_payment(self) -> None:
        self.expect_contact_details(self.shipping_contact, self.shipping_address)
        expect(self.shipping_method).to_have_text(self.SHIPPING_METHOD)
        self.expect_contact_details(self.payment_contact, self.payment_address)
        expect(self.payment_method).to_have_text(self.PAYMENT_METHOD)

    def expect_products_count(self, count: int) -> None:
        expect(self.product_rows).to_have_count(count)

    def expect_product(self, name: str, unit_price: str, quantity: int, line_total: str) -> None:
        row = self.product_row(name)
        expect(row).to_have_count(1)
        expect(row.locator("td").nth(2)).to_have_text(unit_price)
        expect(row.locator("td").nth(3)).to_have_text(str(quantity))
        expect(row.locator("td").nth(4)).to_have_text(line_total)

    def expect_totals(self, subtotal: str, shipping: str, total: str) -> None:
        expected = {
            self.SUBTOTAL_LABEL: subtotal,
            self.SHIPPING_LABEL: shipping,
            self.TOTAL_LABEL: total,
        }
        for label, amount in expected.items():
            expect(self.total_value(label)).to_have_text(amount)

    def expect_order_summary_products_count(self, count: int) -> None:
        expect(self.order_summary_product_rows).to_have_count(count)

    def expect_order_summary_product(self, name: str, quantity: int, unit_price: str) -> None:
        row = self.summary_product_row(name)
        expect(row).to_have_count(1)
        expect(row.locator("td").nth(0)).to_contain_text(f"{quantity} x")
        expect(row.locator("td").nth(1)).to_have_text(unit_price)

    def expect_order_summary_totals(self, subtotal: str, shipping: str, total: str) -> None:
        expected = {
            self.SUBTOTAL_LABEL: subtotal,
            self.SHIPPING_LABEL: shipping,
            self.TOTAL_LABEL: total,
        }
        for label, amount in expected.items():
            expect(self.summary_total_value(label)).to_have_text(amount)

    # endregion
    # ==========================================================================================================
