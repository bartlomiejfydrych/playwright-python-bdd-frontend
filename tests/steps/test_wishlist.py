import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.account.account_dashboard_page import AccountDashboardPage
from src.pages.account.account_my_wish_list_page import AccountMyWishListPage
from src.pages.cart_page import CartPage
from src.pages.home_page import HomePage
from src.pages.product_page import ProductPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "wishlist.feature"))


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def logged_in_home_page(logged_in_page: Page) -> Page:
    """A logged-in page (authenticated storage state) opened on the home page."""
    logged_in_page.goto("/")
    return logged_in_page


@pytest.fixture
def home_page(logged_in_home_page: Page) -> HomePage:
    return HomePage(logged_in_home_page)


@pytest.fixture
def product_page(logged_in_home_page: Page) -> ProductPage:
    return ProductPage(logged_in_home_page)


@pytest.fixture
def account_page(logged_in_home_page: Page) -> AccountDashboardPage:
    return AccountDashboardPage(logged_in_home_page)


@pytest.fixture
def wish_list_page(logged_in_home_page: Page) -> AccountMyWishListPage:
    return AccountMyWishListPage(logged_in_home_page)


@pytest.fixture
def cart_page(logged_in_home_page: Page) -> CartPage:
    return CartPage(logged_in_home_page)


@pytest.fixture
def selected_wishlist_products(
        wish_list_page: AccountMyWishListPage, cart_page: CartPage
) -> Iterator[list[str]]:
    """
    Names of the products chosen by the scenario (filled in by the "adds the first 3 featured products" step).

    NOTE FOR ME: Po teście zawsze czyścimy wishlistę i koszyk (konto jest dedykowane do testów), żeby kolejny
    przebieg nie zaczynał z brudnym stanem. Błąd sprzątania nie może zamaskować błędu testu, więc zamiast
    wyjątku jest ostrzeżenie widoczne w podsumowaniu pytesta.
    """
    selected: list[str] = []
    yield selected

    try:
        cart_page.open()
        cart_page.remove_all_products()

        wish_list_page.open()
        wish_list_page.remove_all_products()
        wish_list_page.expect_wish_list_empty()
    except Exception as exc:  # noqa: BLE001 - teardown must not mask a test failure
        warnings.warn(f"Wish-list test cleanup was incomplete: {exc}", stacklevel=2)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and opens the home page")
def customer_is_logged_in(home_page: HomePage) -> None:
    home_page.expect_logged_in()
    home_page.expect_loaded()


@given("the wish list and shopping cart are empty")
def wish_list_and_cart_are_empty(
        wish_list_page: AccountMyWishListPage,
        cart_page: CartPage,
        account_page: AccountDashboardPage,
        home_page: HomePage,
) -> None:
    # NOTE FOR ME: Konto jest dedykowane do testów, więc zamiast padać na brudnym stanie (po przerwanym
    # przebiegu) czyścimy go na starcie. Nie uruchamiaj tych testów równolegle na tym samym koncie.
    wish_list_page.open()
    wish_list_page.remove_all_products()
    wish_list_page.expect_wish_list_empty()

    cart_page.open()
    cart_page.remove_all_products()
    cart_page.expect_empty_cart()

    account_page.open()
    account_page.expect_loaded()
    account_page.expect_quick_link_badge("My wish list", "0")

    home_page.open()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when("the customer adds the first 3 featured products to the wish list")
def add_first_three_products(
        home_page: HomePage,
        product_page: ProductPage,
        selected_wishlist_products: list[str],
) -> None:
    home_page.open()
    names = home_page.product_names_in("featured")[:3]
    assert len(names) == 3, f"Expected at least 3 featured products, found: {names}"
    assert len(set(names)) == 3, f"Featured product names are not unique: {names}"
    selected_wishlist_products.extend(names)

    for name in names:
        home_page.open()
        home_page.open_product("featured", name)
        product_page.expect_product_name(name)
        product_page.add_to_wish_list()
        product_page.expect_added_to_wish_list()


@when("the customer goes to My Account")
def go_to_my_account(account_page: AccountDashboardPage) -> None:
    account_page.open()
    account_page.expect_loaded()


@when("the customer opens the wish list")
def open_wish_list(
        account_page: AccountDashboardPage, wish_list_page: AccountMyWishListPage
) -> None:
    account_page.click_quick_link("My wish list")
    wish_list_page.expect_loaded()


@when("the customer removes the first selected product from the wish list")
def remove_first_product(
        wish_list_page: AccountMyWishListPage, selected_wishlist_products: list[str]
) -> None:
    wish_list_page.remove_from_wish_list(selected_wishlist_products[0])


@when("the customer adds the second selected product to the shopping cart from the wish list")
def add_second_product_to_cart(
        wish_list_page: AccountMyWishListPage, selected_wishlist_products: list[str]
) -> None:
    wish_list_page.add_to_cart(selected_wishlist_products[1])


@when("the customer removes the second selected product from the shopping cart")
def remove_second_product_from_cart(
        cart_page: CartPage, selected_wishlist_products: list[str]
) -> None:
    cart_page.remove_product(selected_wishlist_products[1])
    cart_page.expect_product_not_in_cart(selected_wishlist_products[1])


@when(parsers.parse("the customer removes the {count:d} remaining selected products from the wish list"))
def remove_remaining_products(
        wish_list_page: AccountMyWishListPage, selected_wishlist_products: list[str], count: int
) -> None:
    remaining = selected_wishlist_products[1:]
    assert len(remaining) == count, f"Expected {count} remaining products, scenario tracks: {remaining}"
    for name in remaining:
        wish_list_page.remove_from_wish_list(name)
        wish_list_page.expect_product_not_listed(name)


@when("the customer reloads the page")
def reload_page(wish_list_page: AccountMyWishListPage) -> None:
    wish_list_page.reload()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

@then(parsers.parse("the wish list counter should be {count:d}"))
def wish_list_counter_is(account_page: AccountDashboardPage, count: int) -> None:
    account_page.expect_quick_link_badge("My wish list", str(count))


@then("the wish list should contain all 3 selected products")
def wish_list_contains_all_selected_products(
        wish_list_page: AccountMyWishListPage, selected_wishlist_products: list[str]
) -> None:
    expected = selected_wishlist_products
    wish_list_page.expect_products_count(len(expected))
    assert sorted(wish_list_page.product_names()) == sorted(expected), (
        f"Expected wish-list products {expected}, got {wish_list_page.product_names()}"
    )


@then("the wish list should contain the 2 remaining selected products")
def wish_list_contains_remaining_products(
        wish_list_page: AccountMyWishListPage, selected_wishlist_products: list[str]
) -> None:
    expected = selected_wishlist_products[1:]
    wish_list_page.expect_products_count(len(expected))
    assert sorted(wish_list_page.product_names()) == sorted(expected), (
        f"Expected remaining products {expected}, got {wish_list_page.product_names()}"
    )


@then("the first selected product should not be in the wish list")
def first_product_is_not_in_wish_list(
        wish_list_page: AccountMyWishListPage, selected_wishlist_products: list[str]
) -> None:
    wish_list_page.expect_product_not_listed(selected_wishlist_products[0])


@then("the shopping cart page should be displayed")
def shopping_cart_page_is_displayed(cart_page: CartPage) -> None:
    cart_page.expect_loaded()


@then("the shopping cart should contain the second selected product")
def shopping_cart_contains_second_product(
        cart_page: CartPage, selected_wishlist_products: list[str]
) -> None:
    cart_page.expect_product_in_cart(selected_wishlist_products[1])
    cart_page.expect_products_count(1)


@then("the wish list table should be empty")
def wish_list_table_is_empty(wish_list_page: AccountMyWishListPage) -> None:
    wish_list_page.expect_wish_list_table_empty()


@then("the wish list should be empty")
def wish_list_is_empty(wish_list_page: AccountMyWishListPage) -> None:
    wish_list_page.expect_wish_list_empty()

# endregion
# ==========================================================================================================
