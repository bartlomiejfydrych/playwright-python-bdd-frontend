from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.cart_page import CartPage
from src.pages.checkout_confirmation_page import CheckoutConfirmationPage
from src.pages.home_page import HomePage
from src.pages.order_success_page import OrderSuccessPage
from src.pages.product_page import ProductPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "purchase.feature"))


# ==========================================================================================================
# region FIXTURES
# ==========================================================================================================

@pytest.fixture
def home_page(logged_in_page: Page) -> HomePage:
    return HomePage(logged_in_page)


@pytest.fixture
def product_page(logged_in_page: Page) -> ProductPage:
    return ProductPage(logged_in_page)


@pytest.fixture
def cart_page(logged_in_page: Page) -> CartPage:
    return CartPage(logged_in_page)


@pytest.fixture
def checkout_confirmation_page(logged_in_page: Page) -> CheckoutConfirmationPage:
    return CheckoutConfirmationPage(logged_in_page)


@pytest.fixture
def order_success_page(logged_in_page: Page) -> OrderSuccessPage:
    return OrderSuccessPage(logged_in_page)


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region HELPERS
# ==========================================================================================================

def _table_rows(datatable) -> list[dict[str, str]]:
    # datatable: first row = header, the rest = data rows
    return [dict(zip(datatable[0], row)) for row in datatable[1:]]


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region GIVEN
# ==========================================================================================================

@given("the customer is logged in and has an empty basket")
def customer_logged_in_with_empty_basket(home_page: HomePage, cart_page: CartPage) -> None:
    # The currency is kept in the session and a fresh API login starts with the store default,
    # so the euro is selected explicitly (the same link the store's own currency menu uses)
    home_page.goto("/?currency=EUR")
    home_page.expect_loaded()
    home_page.expect_logged_in()
    home_page.expect_currency("€")

    # A basket left over from a previous run would break all the sums below
    cart_page.open()
    if cart_page.cart_rows.count():
        cart_page.remove_all_products()
    cart_page.expect_empty_cart()

    home_page.open()
    home_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region WHEN
# ==========================================================================================================

@when(parsers.parse('the customer opens the featured product "{product_name}"'))
def customer_opens_featured_product(home_page: HomePage, product_page: ProductPage, product_name: str) -> None:
    home_page.open()
    home_page.expect_loaded()
    home_page.open_product("featured", product_name)
    product_page.expect_product_name(product_name)


@when(parsers.parse("the customer sets the product quantity to {quantity:d}"))
def customer_sets_product_quantity(product_page: ProductPage, quantity: int) -> None:
    product_page.set_quantity(quantity)


@when("the customer adds the product to the basket")
def customer_adds_product_to_basket(product_page: ProductPage, cart_page: CartPage) -> None:
    product_page.add_to_cart()
    cart_page.expect_loaded()


@when(parsers.parse('the customer removes "{product_name}" from the basket'))
def customer_removes_product(cart_page: CartPage, product_name: str) -> None:
    cart_page.remove_product(product_name)
    cart_page.expect_product_not_in_cart(product_name)


@when("the customer proceeds to checkout")
def customer_proceeds_to_checkout(cart_page: CartPage) -> None:
    cart_page.click_checkout_bottom()


@when("the customer confirms the order")
def customer_confirms_order(checkout_confirmation_page: CheckoutConfirmationPage) -> None:
    checkout_confirmation_page.confirm_order()


@when("the customer continues shopping")
def customer_continues_shopping(order_success_page: OrderSuccessPage) -> None:
    order_success_page.continue_shopping()


@when("the customer opens the basket")
def customer_opens_basket(home_page: HomePage, cart_page: CartPage) -> None:
    home_page.click_cart()
    cart_page.expect_loaded()


# endregion
# ==========================================================================================================

# ==========================================================================================================
# region THEN
# ==========================================================================================================

# ------------
# Product page
# ------------

@then(parsers.parse('the product price is "{price}" and the total price is "{total}"'))
def product_price_and_total_price_are(product_page: ProductPage, price: str, total: str) -> None:
    product_page.expect_price(price)
    product_page.expect_total_price(total)


# ------
# Basket
# ------

@then("the basket contains exactly these products:")
def basket_contains_exactly_these_products(cart_page: CartPage, datatable) -> None:
    rows = _table_rows(datatable)
    cart_page.expect_loaded()
    cart_page.expect_products_count(len(rows))
    for row in rows:
        cart_page.expect_product_row(row["product"], int(row["quantity"]), row["line total"])


@then(parsers.parse('the basket totals are Sub-Total "{subtotal}", Shipping "{shipping}" and Total "{total}"'))
def basket_totals_are(cart_page: CartPage, subtotal: str, shipping: str, total: str) -> None:
    cart_page.expect_totals(subtotal, shipping, total)


@then("the basket is empty")
def basket_is_empty(cart_page: CartPage) -> None:
    cart_page.expect_empty_cart()


# ---------------------
# Checkout confirmation
# ---------------------

@then("the checkout confirmation contains the expected shipping and payment details")
def checkout_confirmation_has_shipping_and_payment(checkout_confirmation_page: CheckoutConfirmationPage) -> None:
    checkout_confirmation_page.expect_loaded()
    checkout_confirmation_page.expect_shipping_and_payment()


@then("the checkout confirmation contains these products:")
def checkout_confirmation_has_products(checkout_confirmation_page: CheckoutConfirmationPage, datatable) -> None:
    rows = _table_rows(datatable)
    checkout_confirmation_page.expect_products_count(len(rows))
    for row in rows:
        checkout_confirmation_page.expect_product(
            row["product"], row["unit price"], int(row["quantity"]), row["line total"]
        )


@then(parsers.parse(
    'the checkout confirmation totals are Sub-Total "{subtotal}", Shipping "{shipping}" and Total "{total}"'
))
def checkout_confirmation_totals_are(
        checkout_confirmation_page: CheckoutConfirmationPage, subtotal: str, shipping: str, total: str
) -> None:
    checkout_confirmation_page.expect_totals(subtotal, shipping, total)


@then("the order summary contains these products:")
def order_summary_has_products(checkout_confirmation_page: CheckoutConfirmationPage, datatable) -> None:
    rows = _table_rows(datatable)
    checkout_confirmation_page.expect_order_summary_products_count(len(rows))
    for row in rows:
        checkout_confirmation_page.expect_order_summary_product(
            row["product"], int(row["quantity"]), row["unit price"]
        )


@then(parsers.parse('the order summary totals are Sub-Total "{subtotal}", Shipping "{shipping}" and Total "{total}"'))
def order_summary_totals_are(
        checkout_confirmation_page: CheckoutConfirmationPage, subtotal: str, shipping: str, total: str
) -> None:
    checkout_confirmation_page.expect_order_summary_totals(subtotal, shipping, total)


# -------------
# Order success
# -------------

@then("the order success page confirms that the order has been processed")
def order_success_page_confirms_order(order_success_page: OrderSuccessPage) -> None:
    order_success_page.expect_order_processed()


@then("the home page is displayed")
def home_page_is_displayed(home_page: HomePage) -> None:
    home_page.expect_loaded()
    home_page.expect_root_url()

# endregion
# ==========================================================================================================
