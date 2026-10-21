import re

from playwright.sync_api import Playwright, StorageState

from src.configuration import config

LOGIN_PATH = "index.php?rt=account/login"
ACCOUNT_PATH_FRAGMENT = "rt=account/account"


def _extract_hidden_value(html: str, field_name: str) -> str:
    # we are looking for the entire <input ...> tag, because the order of attributes can be arbitrary
    tag = re.search(rf'<input[^>]*name="{field_name}"[^>]*>', html)
    if not tag:
        raise RuntimeError(f"Hidden field '{field_name}' not found on login page")
    value = re.search(r'value="([^"]*)"', tag.group(0))
    if not value:
        raise RuntimeError(f"Hidden field '{field_name}' has no value")
    return value.group(1)


def login_via_api(
        playwright: Playwright,
        base_url: str,
        login_name: str | None = None,
        password: str | None = None,
) -> StorageState:
    """
    Logs in with plain HTTP requests and returns Playwright storage state.
    Without arguments it uses the account from .env; custom credentials are needed e.g. to check
    which password is currently valid after a password change.
    """
    api = playwright.request.new_context(base_url=base_url)
    try:
        html = api.get(LOGIN_PATH).text()

        response = api.post(
            LOGIN_PATH,
            multipart={
                "csrftoken": _extract_hidden_value(html, "csrftoken"),
                "csrfinstance": _extract_hidden_value(html, "csrfinstance"),
                "loginname": login_name if login_name is not None else config.get_account_login_name(),
                "password": password if password is not None else config.get_account_password(),
            },
        )

        # If the data is invalid, the server returns a 200 and returns to the login page.
        # So the status alone isn't enough. Upon success, we're redirected to account/account.
        if ACCOUNT_PATH_FRAGMENT not in response.url:
            raise RuntimeError(f"API login failed, ended up on: {response.url}")

        return api.storage_state()
    finally:
        api.dispose()
