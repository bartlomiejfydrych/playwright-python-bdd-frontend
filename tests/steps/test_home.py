import pytest
from pytest_bdd import scenarios, given, then, parsers

from src.pages.home_page import HomePage

scenarios("../features/home.feature")


@pytest.fixture
def home_page(page):
    return HomePage(page)


@given("the user opens the home page")
def open_home_page(home_page):
    home_page.open()


@then(parsers.parse('the page title should be "{expected_title}"'))
def check_title(home_page, expected_title):
    assert home_page.title() == expected_title
