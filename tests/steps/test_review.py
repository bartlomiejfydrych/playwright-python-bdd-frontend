from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.home_page import HomePage
from src.pages.product_page import ProductPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "review.feature"))


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def product_page(page: Page) -> ProductPage:
    return ProductPage(page)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the user opens the store home page for review testing", target_fixture="home_page")
def open_home_page_for_review_testing(page: Page) -> HomePage:
    home_page = HomePage(page)
    home_page.open()
    home_page.expect_loaded()
    return home_page


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when(parsers.parse('the user opens the product "{product_name}"'))
def open_product(home_page: HomePage, product_page: ProductPage, product_name: str) -> None:
    home_page.open_product("featured", product_name)
    product_page.expect_product_name(product_name)


@when("the user opens the reviews tab")
def open_reviews_tab(product_page: ProductPage) -> None:
    product_page.open_reviews_tab()


@when("the user submits an empty review")
def submit_empty_review(product_page: ProductPage) -> None:
    product_page.submit_review()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then(parsers.parse('the review form shows the error message "{message}"'))
def review_form_shows_error_message(product_page: ProductPage, message: str) -> None:
    product_page.expect_review_error(message)

# endregion
# ==========================================================================================================
