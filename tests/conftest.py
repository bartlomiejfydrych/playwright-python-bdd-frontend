import pytest
from playwright.sync_api import Browser, Playwright, StorageState

from src.api.auth import login_via_api


@pytest.fixture(scope="session")
def auth_state(playwright: Playwright, base_url: str) -> StorageState:
    return login_via_api(playwright, base_url)


@pytest.fixture
def logged_in_page(browser: Browser, base_url: str, auth_state: StorageState):
    context = browser.new_context(base_url=base_url, storage_state=auth_state)
    page = context.new_page()
    yield page
    context.close()
