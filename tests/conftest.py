import pytest
from playwright.sync_api import Page, Playwright, StorageState

from src.api.auth import login_via_api


@pytest.fixture(scope="session")
def auth_state(playwright: Playwright, base_url: str) -> StorageState:
    return login_via_api(playwright, base_url)


@pytest.fixture
def logged_in_page(new_context, auth_state: StorageState) -> Page:
    """
    A page with the authenticated storage state, isolated per test.

    NOTE FOR ME: Kontekst tworzymy przez fixture `new_context` z pytest-playwright (a nie przez `browser.new_context`),
    dzięki temu działają `--tracing`, `--screenshot`, `--video`, `base_url` i automatyczne zamykanie kontekstu.
    """
    context = new_context(storage_state=auth_state)
    return context.new_page()
