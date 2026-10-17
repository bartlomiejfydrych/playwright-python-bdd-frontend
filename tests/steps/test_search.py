from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.home_page import HomePage
from src.pages.product_page import ProductPage
from src.pages.search_results_page import SearchResultsPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "search.feature"))


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def search_results_page(page: Page) -> SearchResultsPage:
    return SearchResultsPage(page)


@pytest.fixture
def product_page(page: Page) -> ProductPage:
    return ProductPage(page)


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

@when(parsers.parse('the user searches for "{phrase}"'))
def search_without_category(home_page: HomePage, phrase: str) -> None:
    home_page.search(phrase)


@when(parsers.parse('the user searches for "{phrase}" in category "{category}"'))
def search_with_category(home_page: HomePage, phrase: str, category: str) -> None:
    home_page.search(phrase, category)


@when(parsers.parse('the user searches for "{phrase}" using Enter'))
def search_using_enter(home_page: HomePage, phrase: str) -> None:
    home_page.search_with_enter(phrase)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then(parsers.parse('the user is taken to the page of the product "{product_name}"'))
def user_is_taken_to_product_page(product_page: ProductPage, product_name: str) -> None:
    # The store skips the results list and opens the product directly when the search has exactly one hit
    product_page.expect_product_name(product_name)


@then(parsers.parse('the product "{product_name}" is displayed in the search results'))
def product_is_displayed_in_search_results(search_results_page: SearchResultsPage, product_name: str) -> None:
    search_results_page.expect_product_displayed(product_name)


@then(parsers.parse('the product "{product_name}" is not displayed in the search results'))
def product_is_not_displayed_in_search_results(search_results_page: SearchResultsPage, product_name: str) -> None:
    search_results_page.expect_product_not_displayed(product_name)


@then(parsers.parse("at least {count:d} products are displayed in the search results"))
def at_least_n_products_are_displayed(search_results_page: SearchResultsPage, count: int) -> None:
    search_results_page.expect_at_least_products(count)


@then("no products are displayed in the search results")
def no_products_are_displayed(search_results_page: SearchResultsPage) -> None:
    search_results_page.expect_no_products()


@then(parsers.parse('the search results page shows the message "{message}"'))
def search_results_page_shows_message(search_results_page: SearchResultsPage, message: str) -> None:
    search_results_page.expect_message(message)

# endregion
# ==========================================================================================================
