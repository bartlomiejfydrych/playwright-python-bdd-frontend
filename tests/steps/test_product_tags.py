from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.home_page import HomePage
from src.pages.product_page import ProductPage
from src.pages.search_results_page import SearchResultsPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "product_tags.feature"))


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def product_page(page: Page) -> ProductPage:
    return ProductPage(page)


@pytest.fixture
def search_results_page(page: Page) -> SearchResultsPage:
    return SearchResultsPage(page)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the user opens the home page", target_fixture="home_page")
def open_home_page(page: Page) -> HomePage:
    home_page = HomePage(page)
    home_page.open()
    home_page.expect_loaded()
    return home_page


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when(parsers.parse('the user opens the featured product "{product_name}"'))
def open_featured_product(home_page: HomePage, product_page: ProductPage, product_name: str) -> None:
    home_page.open_product("featured", product_name)
    product_page.expect_product_name(product_name)


@when("the user opens the tags tab")
def open_tags_tab(product_page: ProductPage) -> None:
    product_page.open_tags_tab()


@when(parsers.parse('the user clicks the tag "{tag}"'))
def click_tag(product_page: ProductPage, tag: str) -> None:
    product_page.click_tag(tag)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then(parsers.parse('the search criteria contain "{phrase}"'))
def search_criteria_contain(search_results_page: SearchResultsPage, phrase: str) -> None:
    search_results_page.expect_keyword(phrase)


@then("only the following products are displayed in the search results")
def only_following_products_are_displayed(search_results_page: SearchResultsPage, datatable) -> None:
    # datatable: first row = header (product_name), the rest = expected product names
    expected = [row[0] for row in datatable[1:]]
    search_results_page.expect_only_products(expected)

# endregion
# ==========================================================================================================
