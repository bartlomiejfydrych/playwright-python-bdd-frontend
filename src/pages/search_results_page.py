import re

from playwright.sync_api import Locator, Page, expect

from src.pages.base_page import BasePage


class SearchResultsPage(BasePage):
    """
    Search results page (https://automationteststore.com/index.php?rt=product/search, AbanteCart).

    The search box itself lives in BasePage (search, search_with_enter). This page object only describes
    what the user sees AFTER the search was submitted.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=product/search")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region LOCATORS
    # ==========================================================================================================

    def __init__(self, page: Page):
        super().__init__(page)

        # -------
        # HEADING
        # -------

        self.heading = page.locator("#maincontainer h1.heading1 .maintext")

        # ---------------
        # SEARCH CRITERIA
        # ---------------

        # The results page has its own search form (separate from the header search box in BasePage)
        self.keyword_input = page.locator("#keyword")
        self.category_select = page.locator("#category_id")  # option values: "0" (all), "0,68", "0,36", ...
        self.description_checkbox = page.locator("#description")
        self.model_checkbox = page.locator("#model")
        self.search_button_in_form = page.locator("#search_button")

        # -------
        # RESULTS
        # -------

        # "prdocutname" is a typo in the store's HTML, not in our code
        self.product_names = page.locator("a.prdocutname")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def product_link(self, product_name: str) -> Locator:
        return self.product_names.filter(has_text=product_name)

    def displayed_product_names(self) -> list[str]:
        # The same product link can occur more than once in the DOM (see expect_product_displayed),
        # so we compare unique names (only visible ones, empty texts skipped).
        # NOTE FOR ME:
        # all_text_contents() zamiast all_inner_texts(): sklep wyświetla nazwy WIELKIMI literami przez CSS
        # (text-transform: uppercase), a inner_text zwraca tekst już po tej transformacji
        texts = self.product_names.filter(visible=True).all_text_contents()
        return sorted({text.strip() for text in texts if text.strip()})

    def message(self, text: str) -> Locator:
        # Scoped to the main container so the header/footer can never produce a false match
        return self.page.locator("#maincontainer").get_by_text(text)

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self) -> None:
        # Without this, a "not displayed" check can pass on the page we were on BEFORE the search finished loading
        expect(self.page).to_have_url(self.URL_PATTERN)
        expect(self.heading).to_have_text("Search")

    def expect_product_displayed(self, product_name: str) -> None:
        self.expect_loaded()
        # Not to_have_count(1): the same link was found twice on the results page (see error log)
        expect(self.product_link(product_name).filter(visible=True)).not_to_have_count(0)

    def expect_product_not_displayed(self, product_name: str) -> None:
        self.expect_loaded()
        expect(self.product_link(product_name)).to_have_count(0)

    def expect_at_least_products(self, count: int) -> None:
        self.expect_loaded()
        # nth() is lazy, so the assertion waits until the n-th result actually appears
        expect(self.product_names.nth(count - 1)).to_be_visible()

    def expect_only_products(self, product_names: list[str]) -> None:
        self.expect_loaded()
        # Wait for the first result, then read the whole list (the page is rendered server-side)
        expect(self.product_names.first).to_be_visible()
        actual = self.displayed_product_names()
        assert actual == sorted(product_names), f"Expected products: {sorted(product_names)}, displayed: {actual}"

    def expect_no_products(self) -> None:
        self.expect_loaded()
        expect(self.product_names).to_have_count(0)

    def expect_keyword(self, phrase: str) -> None:
        self.expect_loaded()
        expect(self.keyword_input).to_have_value(phrase)

    def expect_message(self, text: str) -> None:
        self.expect_loaded()
        expect(self.message(text)).to_be_visible()

    # endregion
    # ==========================================================================================================
