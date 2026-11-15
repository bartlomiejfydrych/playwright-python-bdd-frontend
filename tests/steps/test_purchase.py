from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from src.pages.cart_page import CartPage
from src.pages.checkout_confirmation_page import CheckoutConfirmationPage
from src.pages.home_page import HomePage
from src.pages.order_success_page import OrderSuccessPage
from src.pages.product_page import ProductPage
from src.pages.search_results_page import SearchResultsPage

scenarios(str(Path(__file__).resolve().parents[1] / "features" / "purchase.feature"))


@pytest.fixture

def home_page(logged_in_page: Page) -> HomePage:
    return HomePage(logged_in_page)


@pytest.fixture

def cart_page(logged_in_page: Page) -> CartPage:
    return CartPage(logged_in_page)


@pytest.fixture

def product_page(logged_in_page: Page) -> ProductPage:
    return ProductPage(logged_in_page)


@pytest.fixture

def checkout_confirmation_page(logged_in_page: Page) -> CheckoutConfirmationPage:
    return CheckoutConfirmationPage(logged_in_page)


@pytest.fixture

def order_success_page(logged_in_page: Page) -> OrderSuccessPage:
    return OrderSuccessPage(logged_in_page)


def _open_product_from_home(home_page: HomePage, page: Page, product_name: str) -> None:
    home_page.open()
    home_page.expect_loaded()
    home_page.search(product_name)

    # A search with one exact hit may navigate straight to the product page.
    product_heading = page.locator("#product_details h1.productname")
    if product_heading.count() == 0:
        results = SearchResultsPage(page)
        results.expect_loaded()
        results.open_product(product_name)
    expect(product_heading).to_have_text(product_name)


def _assert_cart_contents(cart_page: CartPage, rows: list[dict[str, str]]) -> None:
    cart_page.expect_loaded()
    cart_page.expect_products_count(len(rows))
    for row in rows:
        name = row["product"]
        cart_page.expect_product_in_cart(name)
        cart_page.expect_quantity(name, int(row["quantity"]))
        cart_page.expect_line_total(name, row["line total"])


@given("the customer is logged in and has an empty basket")
def customer_logged_in_with_empty_basket(
    logged_in_page: Page,
    home_page: HomePage,
    cart_page: CartPage,
) -> None:
    home_page.open()
    home_page.expect_loaded()
    expect(home_page.welcome_link).to_be_visible()

    cart_page.open()
    if cart_page.cart_rows.count():
        cart_page.remove_all_products()
    cart_page.expect_empty_cart()

    home_page.open()
    home_page.expect_loaded()


@when(parsers.parse('the customer adds {quantity:d} units of "{product_name}" to the basket'))
def customer_adds_product(
    logged_in_page: Page,
    home_page: HomePage,
    product_page: ProductPage,
    cart_page: CartPage,
    quantity: int,
    product_name: str,
) -> None:
    _open_product_from_home(home_page, logged_in_page, product_name)
    expect(product_page.price).to_be_visible()

    if product_name == "Skinsheen Bronzer Stick":
        product_page.expect_price("27.69€")
        product_page.set_quantity(quantity)
        product_page.expect_total_price("83.07€")
    elif product_name == "Benefit Bella Bamba":
        product_page.expect_price("26.28€")
        product_page.set_quantity(quantity)
        product_page.expect_total_price("52.56€")
    else:
        product_page.expect_price("17.83€")
        product_page.expect_quantity(quantity)

    product_page.add_to_cart_button.click()
    cart_page.expect_loaded()


@then(parsers.parse("the basket contains {count:d} product rows with:"))
def basket_contains_products(cart_page: CartPage, count: int, datatable) -> None:
    rows = [dict(zip(datatable[0], row)) for row in datatable[1:]]
    assert len(rows) == count
    _assert_cart_contents(cart_page, rows)


@then(parsers.parse('the basket totals are Sub-Total "{subtotal}", Shipping "{shipping}" and Total "{total}"'))
def basket_totals_are(cart_page: CartPage, subtotal: str, shipping: str, total: str) -> None:
    expect(cart_page.total_value(cart_page.SUBTOTAL_LABEL)).to_have_text(subtotal)
    expect(cart_page.total_value(cart_page.SHIPPING_LABEL)).to_have_text(shipping)
    expect(cart_page.total_value(cart_page.TOTAL_LABEL)).to_have_text(total)


@when(parsers.parse('the customer removes "{product_name}" from the basket'))
def customer_removes_product(cart_page: CartPage, product_name: str) -> None:
    cart_page.remove_product(product_name)
    expect(cart_page.cart_row(product_name)).to_have_count(0)


@when("the customer proceeds to checkout")
def customer_proceeds_to_checkout(cart_page: CartPage) -> None:
    cart_page.click_checkout_bottom()


@then("the checkout confirmation contains the expected shipping and payment details")
def checkout_confirmation_has_shipping_and_payment(
    checkout_confirmation_page: CheckoutConfirmationPage,
) -> None:
    checkout_confirmation_page.expect_loaded()
    checkout_confirmation_page.expect_shipping_and_payment()


@then("the checkout confirmation contains these products:")
def checkout_confirmation_has_products(checkout_confirmation_page: CheckoutConfirmationPage, datatable) -> None:
    rows = [dict(zip(datatable[0], row)) for row in datatable[1:]]
    expect(checkout_confirmation_page.product_rows).to_have_count(len(rows))
    for row in rows:
        checkout_confirmation_page.expect_product(
            row["product"], row["unit price"], int(row["quantity"]), row["line total"]
        )


@then(parsers.parse('the checkout confirmation totals are Sub-Total "{subtotal}", Shipping "{shipping}" and Total "{total}"'))
def checkout_confirmation_totals(
    checkout_confirmation_page: CheckoutConfirmationPage,
    subtotal: str,
    shipping: str,
    total: str,
) -> None:
    checkout_confirmation_page.expect_totals(subtotal, shipping, total)


@then("the order summary contains these products:")
def order_summary_has_products(checkout_confirmation_page: CheckoutConfirmationPage, datatable) -> None:
    rows = [dict(zip(datatable[0], row)) for row in datatable[1:]]
    expect(checkout_confirmation_page.order_summary_product_rows).to_have_count(len(rows))
    for row in rows:
        checkout_confirmation_page.expect_order_summary_product(
            row["product"], int(row["quantity"]), row["unit price"]
        )


@when("the customer confirms the order")
def customer_confirms_order(checkout_confirmation_page: CheckoutConfirmationPage) -> None:
    checkout_confirmation_page.confirm_order()


@then("the order success page confirms that the order has been processed")
def order_success_page_confirms_order(order_success_page: OrderSuccessPage) -> None:
    order_success_page.expect_order_processed()


@when("the customer continues shopping")
def customer_continues_shopping(order_success_page: OrderSuccessPage) -> None:
    order_success_page.continue_shopping()


@then("the home page is displayed")
def home_page_is_displayed(home_page: HomePage) -> None:
    home_page.expect_loaded()
    home_page.expect_root_url()


@when("the customer opens the basket")
def customer_opens_basket(home_page: HomePage, cart_page: CartPage) -> None:
    home_page.click_cart()
    cart_page.expect_loaded()


@then("the basket is empty")
def basket_is_empty(cart_page: CartPage) -> None:
    cart_page.expect_empty_cart()
