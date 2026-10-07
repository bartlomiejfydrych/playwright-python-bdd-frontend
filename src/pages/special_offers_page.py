import re

from playwright.sync_api import Locator, Page, expect

from base_page import BasePage


class SpecialOffersPage(BasePage):
    """
    Special Offers page (?rt=product/special): sorting, product grid/list view,
    per-page limit, and pagination. Header, menu, and footer come from BasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    PATH = "/index.php?rt=product/special"

    # Sorting: label ➤ option value
    SORT_OPTIONS = {
        "Date Old > New": "date_modified-ASC",
        "Name A - Z": "pd.name-ASC",
        "Name Z - A": "pd.name-DESC",
        "Price Low > High": "p.price-ASC",
        "Price High > Low": "p.price-DESC",
        "Rating Highest": "rating-DESC",
        "Rating Lowest": "rating-ASC",
        "Date New > Old": "date_modified-DESC",
    }
    PER_PAGE_OPTIONS = (10, 20, 30, 40, 50)

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
        self.breadcrumb_items = page.locator("section.breadcrumbs ul.breadcrumb li")
        self.breadcrumb_home_link = page.locator("section.breadcrumbs ul.breadcrumb a[href$='/']")

        # Sorting bar (top): #sort appears once, the second bar (bottom) has #limit
        self.sort_select = page.locator("#sort")
        self.grid_view_button = page.locator("#grid")
        self.list_view_button = page.locator("#list")

        # Product grid (the default view)
        self.grid = page.locator(".thumbnails.grid")
        self.grid_products = page.locator(".thumbnails.grid > div")
        self.grid_product_names = page.locator(".thumbnails.grid a.prdocutname")
        self.grid_new_prices = page.locator(".thumbnails.grid .pricenew")
        self.grid_old_prices = page.locator(".thumbnails.grid .priceold")
        self.grid_sale_badges = page.locator(".thumbnails.grid .thumbnail span.sale")

        # Product list (both views are in the DOM, only one is visible)
        self.list = page.locator(".thumbnails.list")
        self.list_products = page.locator(".thumbnails.list .thumbnail")
        self.list_product_names = page.locator(".thumbnails.list a.prdocutname")
        self.list_new_prices = page.locator(".thumbnails.list .pricenew")
        self.list_old_prices = page.locator(".thumbnails.list .priceold")
        self.list_sale_badges = page.locator(".thumbnails.list span.sale")

        # Bottom bar: per-page limit, results summary, pagination
        self.per_page_select = page.locator("#limit")
        self.results_summary = page.locator("#limit").locator("xpath=ancestor::form")
        self.pagination = page.locator("ul.pagination")
        self.pagination_pages = page.locator("ul.pagination li")
        self.pagination_current_page = page.locator("ul.pagination li.disabled")

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

    def grid_product(self, name: str) -> Locator:
        return self.grid_products.filter(
            has=self.page.locator("a.prdocutname", has_text=name)
        )

    def list_product(self, name: str) -> Locator:
        # w widoku listy nazwa zawiera też kod produktu, np. "Absolue Eye Precious Cells (427847)"
        return self.list_products.filter(
            has=self.page.locator("a.prdocutname", has_text=name)
        )

    def pagination_page_link(self, number: int) -> Locator:
        return self.pagination.locator("a", has_text=str(number))

    # -----------------------------
    # Actions: sort, view, per-page
    # -----------------------------

    def sort_by(self, label: str) -> None:
        self.sort_select.select_option(self.SORT_OPTIONS[label])  # zmiana przeładowuje stronę

    def set_per_page(self, limit: int) -> None:
        self.per_page_select.select_option(str(limit))  # zmiana przeładowuje stronę

    def switch_to_grid_view(self) -> None:
        self.grid_view_button.click()

    def switch_to_list_view(self) -> None:
        self.list_view_button.click()

    # ----------------
    # Actions: product
    # ----------------

    def open_product(self, name: str) -> None:
        self.grid_product(name).locator("a.prdocutname").click()

    def view_product(self, name: str) -> None:
        card = self.grid_product(name)
        card.hover()  # View/Write Review links appear on hover
        card.locator("a.details").click()

    def write_review(self, name: str) -> None:
        card = self.grid_product(name)
        card.hover()
        card.locator("a.compare").click()

    def add_to_cart(self, name: str) -> None:
        self.grid_product(name).locator("a.productcart").click()

    def add_to_cart_from_list(self, name: str) -> None:
        self.list_product(name).locator("a.productcart").click()

    # -------------------
    # Actions: pagination
    # -------------------

    def go_to_page(self, number: int) -> None:
        self.pagination_page_link(number).click()

    # --------
    # Readings
    # --------

    @staticmethod
    def price_to_float(text: str) -> float:
        return float(re.sub(r"[^\d.]", "", text))

    def product_names(self) -> list[str]:
        return [t.strip() for t in self.grid_product_names.all_inner_texts()]

    def new_prices(self) -> list[float]:
        return [self.price_to_float(t) for t in self.grid_new_prices.all_inner_texts()]

    def old_prices(self) -> list[float]:
        return [self.price_to_float(t) for t in self.grid_old_prices.all_inner_texts()]

    def products_count(self) -> int:
        return self.grid_products.count()

    def selected_sort_text(self) -> str:
        return self.sort_select.locator("option:checked").inner_text().strip()

    def selected_per_page(self) -> int:
        return int(self.per_page_select.input_value())

    def results_summary_text(self) -> str:
        return " ".join(self.results_summary.inner_text().split())  # e.g. "Per Page 20 1 - 8 of 8"

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r"rt=product/special"))
        expect(self.heading).to_have_text("Special Offers")

    def expect_products_count(self, count: int) -> None:
        expect(self.grid_products).to_have_count(count)

    def expect_sort_selected(self, label: str) -> None:
        expect(self.sort_select).to_have_value(self.SORT_OPTIONS[label])

    def expect_per_page(self, limit: int) -> None:
        expect(self.per_page_select).to_have_value(str(limit))

    def expect_grid_view(self) -> None:
        expect(self.grid).to_be_visible()
        expect(self.list).to_be_hidden()

    def expect_list_view(self) -> None:
        expect(self.list).to_be_visible()
        expect(self.grid).to_be_hidden()

    def expect_product_visible(self, name: str) -> None:
        expect(self.grid_product(name)).to_be_visible()

    def expect_all_products_on_sale(self) -> None:
        # each card has a sale tag and the old and new price
        count = self.grid_products.count()
        expect(self.grid_sale_badges).to_have_count(count)
        expect(self.grid_old_prices).to_have_count(count)
        expect(self.grid_new_prices).to_have_count(count)

    def expect_results_summary(self, text: str) -> None:
        expect(self.results_summary).to_contain_text(text)

    # endregion
    # ==========================================================================================================
