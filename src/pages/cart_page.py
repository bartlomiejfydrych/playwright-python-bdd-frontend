from playwright.sync_api import Locator, Page, expect

from base_page import BasePage


class CartPage(BasePage):
    """
    "Shopping Cart" page (Basket, rt=checkout/cart).
    Verified on two states: empty cart and cart with 5 products
    (product list, coupon, shipping estimate, totals, two Checkout buttons).
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    PATH = "/index.php?rt=checkout/cart"
    TITLE = "Shopping Cart"
    EMPTY_CART_MESSAGE = "Your shopping cart is empty!"

    # Labels in the totals table (the text includes a colon)
    SUBTOTAL_LABEL = "Sub-Total:"
    SHIPPING_LABEL = "Flat Shipping Rate:"
    TOTAL_LABEL = "Total:"

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

        # Heading and breadcrumbs
        self.heading = page.locator("h1.heading1 .maintext")
        self.breadcrumbs = page.locator("ul.breadcrumb li")
        self.breadcrumb_home_link = page.locator("ul.breadcrumb a[href$='/']")
        self.breadcrumb_basket_link = page.locator("ul.breadcrumb a[href*='rt=checkout/cart']")

        # Empty cart (the message is a bare text node in .contentpanel, so we check the panel text)
        self.content_panel = page.locator("#maincontainer .contentpanel")
        self.continue_button = page.locator("#maincontainer .contentpanel a.btn[title='Continue']")

        # Product list (cart form exists only when the cart is not empty)
        self.cart_form = page.locator("#cart")
        self.cart_rows = page.locator("#cart .product-list table tr:has(input[name^='quantity'])")
        self.product_name_links = self.cart_rows.locator("td:nth-child(2) > a")
        self.product_images = self.cart_rows.locator("td:nth-child(1) img")
        self.quantity_inputs = self.cart_rows.locator("input[name^='quantity']")
        self.remove_links = self.cart_rows.locator("a[href*='remove=']")
        self.update_button = page.locator("#cart_update")
        self.checkout_top_button = page.locator("#cart_checkout1")
        self.checkout_bottom_button = page.locator("#cart_checkout2")
        self.continue_shopping_button = page.locator(".cart_total a.btn", has_text="Continue Shopping")

        # Coupon
        self.coupon_input = page.locator("#coupon_coupon")
        self.apply_coupon_button = page.locator("#apply_coupon_btn")
        self.remove_coupon_button = page.locator(
            "#remove_coupon_btn")  # from the page script, appears after applying a coupon

        # Estimate shipping & taxes
        self.estimate_country_select = page.locator("#estimate_country")
        self.estimate_zone_select = page.locator("#estimate_country_zones")
        self.estimate_postcode_input = page.locator("#estimate_postcode")
        self.estimate_button = page.locator("#estimate button[title='Estimate']")
        self.shipping_select = page.locator("#shippings")

        # Totals (the table is reloaded by AJAX right after the page loads)
        self.totals_table = page.locator("#totals_table")
        self.total_rows = page.locator("#totals_table tr")

        # Error alert (added by the page script, e.g. on a failed action)
        self.error_alert = page.locator("#cart .alert-danger")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------
    # Navigation
    # ----------

    def open(self) -> None:
        self.goto(self.PATH)

    # ----------------
    # Dynamic locators
    # ----------------

    def cart_row(self, product_name: str) -> Locator:
        return self.cart_rows.filter(has_text=product_name)

    def quantity_input(self, product_name: str) -> Locator:
        return self.cart_row(product_name).locator("input[name^='quantity']")

    def remove_link(self, product_name: str) -> Locator:
        return self.cart_row(product_name).locator("a[href*='remove=']")

    def product_link(self, product_name: str) -> Locator:
        return self.cart_row(product_name).locator("td:nth-child(2) > a")

    def product_options(self, product_name: str) -> Locator:
        return self.cart_row(product_name).locator("td:nth-child(2) small")

    def total_row(self, label: str) -> Locator:
        return self.total_rows.filter(has_text=label)

    def total_value(self, label: str) -> Locator:
        return self.total_row(label).locator("td:nth-child(2)")

    # -------------
    # Actions: Cart
    # -------------

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_continue_shopping(self) -> None:
        self.continue_shopping_button.click()

    def set_quantity(self, product_name: str, quantity: int) -> None:
        self.quantity_input(product_name).fill(str(quantity))

    def click_update(self) -> None:
        self.update_button.click()

    def update_quantity(self, product_name: str, quantity: int) -> None:
        self.set_quantity(product_name, quantity)
        self.click_update()

    def remove_product(self, product_name: str) -> None:
        self.remove_link(product_name).click()

    def open_product(self, product_name: str) -> None:
        self.product_link(product_name).click()

    def click_checkout_top(self) -> None:
        self.checkout_top_button.click()

    def click_checkout_bottom(self) -> None:
        self.checkout_bottom_button.click()

    # ---------------
    # Actions: Coupon
    # ---------------

    def apply_coupon(self, code: str) -> None:
        self.coupon_input.fill(code)
        self.apply_coupon_button.click()

    def remove_coupon(self) -> None:
        self.remove_coupon_button.click()

    # -----------------
    # Actions: Estimate
    # -----------------

    def estimate_shipping(self, country: str, postcode: str = "", zone: str | None = None) -> None:
        self.estimate_country_select.select_option(label=country)
        if zone:
            self.estimate_zone_select.select_option(label=zone)
        self.estimate_postcode_input.fill(postcode)
        self.estimate_button.click()

    def select_shipping(self, label: str) -> None:
        self.shipping_select.select_option(label=label)

    # --------------------
    # Actions: Breadcrumbs
    # --------------------

    def click_breadcrumb_home(self) -> None:
        self.breadcrumb_home_link.click()

    # --------
    # Readings
    # --------

    @staticmethod
    def price_to_float(text: str) -> float:
        """'$1,029.50' ➤ 1029.5"""
        return float(text.replace("$", "").replace(",", "").strip())

    def heading_text(self) -> str:
        return self.heading.inner_text().strip()

    def breadcrumb_names(self) -> list[str]:
        return [t.strip() for t in self.breadcrumbs.all_inner_texts()]

    def products_count(self) -> int:
        return self.cart_rows.count()

    def product_names(self) -> list[str]:
        return [t.strip() for t in self.product_name_links.all_inner_texts()]

    def model_of(self, product_name: str) -> str:
        return self.cart_row(product_name).locator("td:nth-child(3)").inner_text().strip()

    def unit_price_of(self, product_name: str) -> float:
        return self.price_to_float(self.cart_row(product_name).locator("td:nth-child(4)").inner_text())

    def quantity_of(self, product_name: str) -> int:
        return int(self.quantity_input(product_name).input_value())

    def line_total_of(self, product_name: str) -> float:
        return self.price_to_float(self.cart_row(product_name).locator("td:nth-child(6)").inner_text())

    def line_totals_sum(self) -> float:
        """Sum of the 'Total' column for all products (to compare with Sub-Total)."""
        return round(sum(
            self.price_to_float(t)
            for t in self.cart_rows.locator("td:nth-child(6)").all_inner_texts()
        ), 2)

    def subtotal(self) -> float:
        return self.price_to_float(self.total_value(self.SUBTOTAL_LABEL).inner_text())

    def shipping_cost(self) -> float:
        return self.price_to_float(self.total_value(self.SHIPPING_LABEL).inner_text())

    def total(self) -> float:
        return self.price_to_float(self.total_value(self.TOTAL_LABEL).inner_text())

    def selected_shipping_text(self) -> str:
        return self.shipping_select.locator("option:checked").inner_text().strip()

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self) -> None:
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.TITLE)

    def expect_empty_cart(self) -> None:
        expect(self.content_panel).to_contain_text(self.EMPTY_CART_MESSAGE)
        expect(self.continue_button).to_be_visible()
        expect(self.cart_form).to_have_count(0)

    def expect_products_count(self, count: int) -> None:
        expect(self.cart_rows).to_have_count(count)

    def expect_product_in_cart(self, product_name: str) -> None:
        expect(self.cart_row(product_name)).to_be_visible()

    def expect_product_not_in_cart(self, product_name: str) -> None:
        expect(self.cart_row(product_name)).to_have_count(0)

    def expect_quantity(self, product_name: str, quantity: int) -> None:
        expect(self.quantity_input(product_name)).to_have_value(str(quantity))

    def expect_line_total(self, product_name: str, amount: str) -> None:
        """amount as on the page, e.g. '$56.00'"""
        expect(self.cart_row(product_name).locator("td:nth-child(6)")).to_have_text(amount)

    def expect_subtotal(self, amount: str) -> None:
        expect(self.total_value(self.SUBTOTAL_LABEL)).to_have_text(amount)

    def expect_total(self, amount: str) -> None:
        expect(self.total_value(self.TOTAL_LABEL)).to_have_text(amount)

    def expect_coupon_applied(self) -> None:
        expect(self.remove_coupon_button).to_be_visible()

    # endregion
    # ==========================================================================================================
