import re

from playwright.sync_api import Locator, Page, expect

from src.pages.account.account_base_page import AccountBasePage


class AccountMyWishListPage(AccountBasePage):
    """
    Account wish list "My wish list" (rt=account/wishlist): table of added products
    (image, name, model, price, date, actions) and the Continue Shopping / View Cart buttons.
    Breadcrumbs, heading and the "My Account" side menu come from AccountBasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/wishlist")

    HEADING_TEXT = "My wish list"

    EMPTY_TEXT = "Wish list is empty"

    COLUMNS = ("Image", "Name", "Model", "Unit Price", "Added to wish list", "Actions")

    EMPTY_TEXT = "Wish list is empty"

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

        # Breadcrumbs: Home > Account > My wish list (the last item is specific to this page)
        self.breadcrumb_wish_list_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='account/wishlist']")

        # Empty state: the table is replaced by plain text (only Continue Shopping is left)
        self.empty_message = page.locator(".contentpanel", has_text=self.EMPTY_TEXT)

        # Wish list table (header row has no class, product rows have class wishlist_<product_id>)
        self.table = page.locator(".wishlist table")
        self.column_headers = page.locator(".wishlist table th")
        self.rows = page.locator(".wishlist table tr[class^='wishlist_']")
        self.product_name_links = page.locator(".wishlist table tr[class^='wishlist_'] td:nth-child(2) a")

        # Empty state: a message instead of the table
        self.empty_message = page.locator(".contentpanel").get_by_text(self.EMPTY_TEXT)

        # Buttons (Continue Shopping is present in both states, View Cart only when the list is not empty)
        self.continue_shopping_button = page.locator(".contentpanel a.btn", has_text="Continue Shopping")
        self.view_cart_button = page.locator(".wishlist a.btn-orange", has_text="View Cart")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def row(self, product_name: str) -> Locator:
        return self.rows.filter(
            has=self.page.get_by_role("link", name=product_name, exact=True)
        )

    def row_by_product_id(self, product_id: int | str) -> Locator:
        return self.page.locator(f".wishlist table tr.wishlist_{product_id}")

    def row_name_link(self, product_name: str) -> Locator:
        return self.row(product_name).locator("td:nth-child(2) a")

    def row_model(self, product_name: str) -> Locator:
        return self.row(product_name).locator("td:nth-child(3)")

    def row_price(self, product_name: str) -> Locator:
        return self.row(product_name).locator(".oneprice")

    def row_added_date(self, product_name: str) -> Locator:
        return self.row(product_name).locator("td:nth-child(5)")

    def row_add_to_cart_button(self, product_name: str) -> Locator:
        return self.row(product_name).locator("a.btn-primary")

    def row_remove_button(self, product_name: str) -> Locator:
        return self.row(product_name).locator("a.btn-remove")

    # ------------------
    # Actions: main part
    # ------------------

    def open_product(self, product_name: str) -> None:
        self.row_name_link(product_name).click()

    def add_to_cart(self, product_name: str) -> None:
        self.row_add_to_cart_button(product_name).click()

    def remove_from_wish_list(self, product_name: str) -> None:
        # Wiersz znika bez przeładowania strony (JS), więc po akcji używaj asercji z auto-wait
        self.row_remove_button(product_name).click()

    def click_continue_shopping(self) -> None:
        self.continue_shopping_button.click()

    def click_view_cart(self) -> None:
        self.view_cart_button.click()

    # --------
    # Readings
    # --------

    def products_count(self) -> int:
        return self.rows.count()

    def product_names(self) -> list[str]:
        return [t.strip() for t in self.product_name_links.all_inner_texts()]

    def model_text(self, product_name: str) -> str:
        return self.row_model(product_name).inner_text().strip()

    def price_text(self, product_name: str) -> str:
        return self.row_price(product_name).inner_text().strip()

    def added_date_text(self, product_name: str) -> str:
        return self.row_added_date(product_name).inner_text().strip()

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
        self.expect_side_menu_selected("My wish list")

    def expect_wish_list_empty(self) -> None:
        expect(self.empty_message).to_be_visible()
        expect(self.rows).to_have_count(0)

    def expect_empty(self) -> None:
        expect(self.empty_message).to_be_visible()
        expect(self.rows).to_have_count(0)
        expect(self.continue_shopping_button).to_be_visible()

    def expect_columns(self) -> None:
        expect(self.column_headers).to_have_text(list(self.COLUMNS))

    def expect_products_count(self, count: int) -> None:
        expect(self.rows).to_have_count(count)

    def expect_product_listed(self, product_name: str) -> None:
        expect(self.row(product_name)).to_be_visible()

    def expect_product_not_listed(self, product_name: str) -> None:
        expect(self.row(product_name)).to_have_count(0)

    def expect_product_price(self, product_name: str, price: str) -> None:
        expect(self.row_price(product_name)).to_have_text(price)

    # endregion
    # ==========================================================================================================
