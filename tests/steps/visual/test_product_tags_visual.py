from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when
from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

from src.pages.product_page import ProductPage
from src.pages.search_results_page import SearchResultsPage
# NOTE FOR ME: Fixture z test_product_tags.py importujemy, bo w pytest-bdd fixture z innego modułu nie jest widoczny.
# Kroki (Given/When/Then) definiujemy tu od nowa, bo kroki z innego modułu też nie są widoczne.
from tests.steps.test_product_tags import (  # noqa: F401
    product_page,
    search_results_page,
)

scenarios(str(Path(__file__).resolve().parents[2] / "features" / "visual" / "product_tags_visual.feature"))

# ==========================================================================================================
# region TEST DATA
# ==========================================================================================================

# NOTE FOR ME: Wchodzimy bezpośrednio na stronę produktu (bez strony głównej): tu testujemy wygląd, nie nawigację.
# Product ID zweryfikowany w ProductPage (Skinsheen Bronzer Stick = 50).
PRODUCT_IDS = {
    "Skinsheen Bronzer Stick": 50,
}


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given(parsers.parse('the user is on the page of the product "{product_name}"'))
def user_is_on_product_page(product_page: ProductPage, product_name: str) -> None:
    product_page.goto_product(PRODUCT_IDS[product_name])
    product_page.expect_product_name(product_name)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

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

@then("the tags tab matches the visual snapshot")
def tags_tab_snapshot(product_page: ProductPage, assert_snapshot: AssertSnapshot) -> None:
    product_page.expect_tags_matches_snapshot(assert_snapshot, "product_tags_tab")


@then("the search criteria match the visual snapshot")
def search_criteria_snapshot(search_results_page: SearchResultsPage, assert_snapshot: AssertSnapshot) -> None:
    search_results_page.expect_search_criteria_matches_snapshot(assert_snapshot, "product_tags_search_criteria")


@then("the search results grid matches the visual snapshot")
def search_results_grid_snapshot(search_results_page: SearchResultsPage, assert_snapshot: AssertSnapshot) -> None:
    search_results_page.expect_results_grid_matches_snapshot(assert_snapshot, "product_tags_search_results")

# endregion
# ==========================================================================================================
