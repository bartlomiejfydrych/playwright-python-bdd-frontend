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


@pytest.fixture
def wishlist_page(logged_in_page: Page) -> Page:
    """A page with the authenticated storage state, isolated per test."""
    logged_in_page.goto("/")
    return logged_in_page


@pytest.fixture
def selected_wishlist_products(wishlist_page: Page) -> list[str]:
    """Track only products created by this scenario and remove them at teardown."""
    selected: list[str] = []
    yield selected

    # Cleanup is best-effort so it does not hide the original assertion failure.
    # The scenario requires an initially empty wishlist/cart, so these are test-owned items.
    try:
        cart = CartPage(wishlist_page)
        cart.open()
        for name in selected:
            if cart.cart_row(name).count():
                cart.remove_product(name)

        wish_list = AccountMyWishListPage(wishlist_page)
        wishlist_page.goto("/index.php?rt=account/wishlist")
        for name in selected:
            if wish_list.row(name).count():
                wish_list.remove_from_wish_list(name)
                wish_list.expect_product_not_listed(name)
        # Ensure the final state is empty before closing the context.
        wish_list.expect_wish_list_empty()
    except Exception as exc:  # noqa: BLE001 - teardown must not mask a test failure
        print(f"[WARNING] Wish-list test cleanup was incomplete: {exc}")


@given("the customer is logged in and opens the home page")
def customer_is_logged_in(wishlist_page: Page) -> None:
    HomePage(wishlist_page).expect_logged_in()
    HomePage(wishlist_page).expect_loaded()


@given("the wish list and shopping cart are empty")
def wish_list_and_cart_are_empty(wishlist_page: Page) -> None:
    wish_list = AccountMyWishListPage(wishlist_page)
    wishlist_page.goto("/index.php?rt=account/wishlist")
    if wish_list.rows.count():
        pytest.fail(
            "Precondition failed: the account's wish list is not empty. "
            "The test will not delete products that may belong to another test."
        )
    wish_list.expect_wish_list_empty()

    account = AccountDashboardPage(wishlist_page)
    wishlist_page.goto("/index.php?rt=account/account")
    account.expect_loaded()
    account.expect_quick_link_badge("My wish list", "0")

    cart = CartPage(wishlist_page)
    cart.open()
    cart.expect_empty_cart()
    HomePage(wishlist_page).open()


@when("the customer adds the first 3 featured products to the wish list")
def add_first_three_products(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    home = HomePage(wishlist_page)
    home.open()
    names = home.product_names_in("featured")[:3]
    assert len(names) == 3, f"Expected at least 3 featured products, found: {names}"
    assert len(set(names)) == 3, f"Featured product names are not unique: {names}"
    selected_wishlist_products.extend(names)

    product_page = ProductPage(wishlist_page)
    for name in names:
        home.open()
        home.open_product("featured", name)
        product_page.expect_product_name(name)
        product_page.add_to_wish_list()


@then(parsers.parse("the wish list counter should be {count:d}"))
def wish_list_counter_is(wishlist_page: Page, count: int) -> None:
    account = AccountDashboardPage(wishlist_page)
    wishlist_page.goto("/index.php?rt=account/account")
    account.expect_loaded()
    account.expect_quick_link_badge("My wish list", str(count))


@when("the customer opens the wish list")
def open_wish_list(wishlist_page: Page) -> None:
    AccountDashboardPage(wishlist_page).click_quick_link("My wish list")
    AccountMyWishListPage(wishlist_page).expect_loaded()


@then(parsers.parse("the wish list should contain the {count:d} selected products"))
def wish_list_contains_selected_products(
        wishlist_page: Page, selected_wishlist_products: list[str], count: int
) -> None:
    wish_list = AccountMyWishListPage(wishlist_page)
    expected = selected_wishlist_products[:count] if count == 3 else selected_wishlist_products[1:]
    wish_list.expect_products_count(count)
    assert set(wish_list.product_names()) == set(expected), (
        f"Expected wish-list products {expected}, got {wish_list.product_names()}"
    )
    for name in expected:
        wish_list.expect_product_listed(name)


@when("the customer removes the first selected product from the wish list")
def remove_first_product(wishlist_page: Page, selected_wishlist_products: list[str]) -> None:
    AccountMyWishListPage(wishlist_page).remove_from_wish_list(selected_wishlist_products[0])


@then("the first selected product should not be in the wish list")
def first_product_is_not_in_wish_list(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    AccountMyWishListPage(wishlist_page).expect_product_not_listed(selected_wishlist_products[0])


@then("the other 2 selected products should remain in the wish list")
def other_two_products_remain(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    wish_list = AccountMyWishListPage(wishlist_page)
    expected = selected_wishlist_products[1:]
    wish_list.expect_products_count(2)
    assert set(wish_list.product_names()) == set(expected)


@when("the customer adds the second selected product to the shopping cart from the wish list")
def add_second_product_to_cart(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    AccountMyWishListPage(wishlist_page).add_to_cart(selected_wishlist_products[1])


@then("the shopping cart page should be displayed")
def shopping_cart_page_is_displayed(wishlist_page: Page) -> None:
    CartPage(wishlist_page).expect_loaded()


@then("the shopping cart should contain the second selected product")
def shopping_cart_contains_second_product(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    cart = CartPage(wishlist_page)
    cart.expect_product_in_cart(selected_wishlist_products[1])
    assert selected_wishlist_products[1] in cart.product_names()


@when("the customer removes the second selected product from the shopping cart")
def remove_second_product_from_cart(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    cart = CartPage(wishlist_page)
    cart.remove_product(selected_wishlist_products[1])
    cart.expect_product_not_in_cart(selected_wishlist_products[1])


@when("the customer returns to My Account")
def return_to_my_account(wishlist_page: Page) -> None:
    AccountDashboardPage(wishlist_page).goto("/index.php?rt=account/account")
    AccountDashboardPage(wishlist_page).expect_loaded()


@then("the wish list should contain the 2 remaining selected products")
def two_remaining_products_are_listed(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    wish_list = AccountMyWishListPage(wishlist_page)
    expected = selected_wishlist_products[1:]
    wish_list.expect_loaded()
    wish_list.expect_products_count(2)
    assert set(wish_list.product_names()) == set(expected), (
        f"Expected remaining products {expected}, got {wish_list.product_names()}"
    )


@when("the customer cleans up the selected wish list products")
def clean_up_selected_products(
        wishlist_page: Page, selected_wishlist_products: list[str]
) -> None:
    wish_list = AccountMyWishListPage(wishlist_page)
    for name in selected_wishlist_products[1:]:
        if wish_list.row(name).count():
            wish_list.remove_from_wish_list(name)
            wish_list.expect_product_not_listed(name)


@then("the wish list should be empty")
def wish_list_is_empty(wishlist_page: Page) -> None:
    AccountMyWishListPage(wishlist_page).expect_wish_list_empty()
