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


@when("the user opens the reviews tab")
def open_reviews_tab(product_page: ProductPage) -> None:
    product_page.open_reviews_tab()


@when(parsers.parse(
    'the user fills in the review form with name "{name}", rating {rating:d}, '
    'text "{text}" and CAPTCHA code "{captcha}"'
))
def fill_review_form(product_page: ProductPage, name: str, rating: int, text: str, captcha: str) -> None:
    product_page.write_review(name, text, rating, captcha)


@when("the user submits the review form")
def submit_review_form(product_page: ProductPage) -> None:
    product_page.submit_review()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then(parsers.parse('the review form shows the error message "{message}"'))
def review_form_shows_error_message(product_page: ProductPage, message: str) -> None:
    product_page.expect_review_error(message)


@then("the product still has no reviews")
def product_still_has_no_reviews(product_page: ProductPage) -> None:
    product_page.expect_no_reviews()

# endregion
# ==========================================================================================================
