from playwright.sync_api import Locator, Page, expect

from base_page import BasePage


class CartPage(BasePage):
    """
    "Shopping Cart" page (Basket, rt=checkout/cart).
    Locators for the empty cart are verified on the provided HTML.
    Locators for a cart with products are marked "UNVERIFIED" - based on the AbanteCart default template,
    they need to be checked against a real page with products in the basket.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    PATH = "/index.php?rt=checkout/cart"
    TITLE = "Shopping Cart"
    EMPTY_CART_MESSAGE = "Your shopping cart is empty!"

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

        # Cart with products - UNVERIFIED
        self.cart_form = page.locator("#cart")
        self.cart_rows = page.locator("#cart table.table tr:has(input[name^='quantity'])")
        self.product_name_links = page.locator("#cart table.table tr td a[href*='product_id']:not(:has(img))")
        self.quantity_inputs = page.locator("#cart input[name^='quantity']")
        self.remove_links = page.locator("#cart a[href*='remove=']")
        self.update_button = page.locator("#cart_update")
        self.checkout_buttons = page.locator("a[id^='cart_checkout']")

        # Totals - UNVERIFIED
        self.totals_table = page.locator("#totals_table")
        self.total_rows = page.locator("#totals_table tr")

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

    # -------------
    # Actions: Cart
    # -------------

    def click_continue(self) -> None:
        self.continue_button.click()

    def set_quantity(self, product_name: str, quantity: int) -> None:
        self.quantity_input(product_name).fill(str(quantity))

    def click_update(self) -> None:
        self.update_button.click()

    def update_quantity(self, product_name: str, quantity: int) -> None:
        self.set_quantity(product_name, quantity)
        self.click_update()

    def remove_product(self, product_name: str) -> None:
        self.remove_link(product_name).click()

    def click_checkout_from_cart(self) -> None:
        self.checkout_buttons.first.click()

    # --------------------
    # Actions: Breadcrumbs
    # --------------------

    def click_breadcrumb_home(self) -> None:
        self.breadcrumb_home_link.click()

    # --------
    # Readings
    # --------

    def heading_text(self) -> str:
        return self.heading.inner_text().strip()

    def breadcrumb_names(self) -> list[str]:
        return [t.strip() for t in self.breadcrumbs.all_inner_texts()]

    def products_count(self) -> int:
        return self.cart_rows.count()

    def product_names(self) -> list[str]:
        return [t.strip() for t in self.product_name_links.all_inner_texts()]

    def quantity_of(self, product_name: str) -> int:
        return int(self.quantity_input(product_name).input_value())

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

    # endregion
    # ==========================================================================================================
