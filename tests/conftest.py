import pytest
from playwright.sync_api import Page, Playwright, StorageState

from src.api.auth import login_via_api


class AuthSession:
    """
    Storage state shared by all tests (one API login per run) that can be refreshed.

    NOTE FOR ME: Wylogowanie (test_logout) może po stronie serwera unieważnić sesję współdzieloną przez wszystkie testy.
    Dlatego test wylogowania po sobie wywołuje `refresh()`, a kolejne testy dostają świeżo zalogowany stan.
    """

    def __init__(self, playwright: Playwright, base_url: str):
        self._playwright = playwright
        self._base_url = base_url
        self.state: StorageState = login_via_api(playwright, base_url)

    def refresh(self) -> None:
        self.state = login_via_api(self._playwright, self._base_url)


@pytest.fixture(scope="session")
def auth_session(playwright: Playwright, base_url: str) -> AuthSession:
    return AuthSession(playwright, base_url)


@pytest.fixture
def logged_in_page(new_context, auth_session: AuthSession) -> Page:
    """
    A page with the authenticated storage state, isolated per test.

    NOTE FOR ME: Kontekst tworzymy przez fixture `new_context` z pytest-playwright (a nie przez `browser.new_context`),
    dzięki temu działają `--tracing`, `--screenshot`, `--video`, `base_url` i automatyczne zamykanie kontekstu.
    """
    context = new_context(storage_state=auth_session.state)
    return context.new_page()


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # Scenarios tagged @known_bug describe the CORRECT behaviour that the store currently violates.
    # strict=True: once the store is fixed the test starts passing (XPASS) and fails the run,
    # which is the signal to remove the tag and the workaround steps in the other scenarios.
    # raises=AssertionError: an xfail must not hide unrelated errors (timeouts, missing elements, typos).
    for item in items:
        if item.get_closest_marker("known_bug"):
            item.add_marker(pytest.mark.xfail(
                reason="Known store defect: the scenario describes the correct behaviour that the store violates",
                strict=True,
                raises=AssertionError,
            ))
