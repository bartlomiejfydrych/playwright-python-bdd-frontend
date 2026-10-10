import re

from playwright.sync_api import Locator, Page, expect

from src.pages.account.account_base_page import AccountBasePage


class AccountDashboardPage(AccountBasePage):
    """
    Account dashboard "My Account" (rt=account/account): heading with the customer's first name,
    icon bar with quick links (some with badges), and tiles with account summaries.
    Breadcrumbs and the "My Account" side menu come from AccountBasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/account")

    HEADING_TEXT = "My Account"

    # Icon bar: name ➤ href fragment (icons only, the name is in the tooltip)
    QUICK_LINKS = {
        "Edit account details": "account/edit",
        "Change password": "account/password",
        "Manage Address Book": "account/address",
        "My wish list": "account/wishlist",
        "Order history": "account/history",
        "Transaction history": "account/transactions",
        "Downloads": "account/download",
        "Notifications": "account/notification",
        "Logoff": "account/logout",
    }
    # Only some icons have a badge (counter or balance)
    QUICK_LINKS_WITH_BADGE = (
        "Manage Address Book", "My wish list", "Order history", "Transaction history", "Downloads",
    )

    # Tiles: header name (the tile value is a counter or balance)
    TILES = ("Manage Address Book", "Order history", "Downloads", "Transaction history")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region LOCATORS
    # ==========================================================================================================

    def __init__(self, page: Page):
        super().__init__(page)

        # ---
        # MID
        # ---

        # Content panel
        self.first_name = page.locator("h1.heading1 .subtext")

        # Icon bar with quick links
        self.quick_links_bar = page.locator("ul.nav-dash")
        self.quick_links = page.locator("ul.nav-dash li a")
        self.quick_link_badges = page.locator("ul.nav-dash li a .badge")

        # Tiles
        self.tiles_section = page.locator(".dash-tiles")
        self.tiles = page.locator(".dash-tiles .dash-tile")
        self.tile_headers = page.locator(".dash-tiles .dash-tile-header")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def quick_link(self, name: str) -> Locator:
        fragment = self.QUICK_LINKS[name]
        return self.page.locator(f"ul.nav-dash li a[href*='{fragment}']")

    def quick_link_badge(self, name: str) -> Locator:
        return self.quick_link(name).locator(".badge")

    def tile(self, name: str) -> Locator:
        return self.page.locator(
            ".dash-tiles .dash-tile",
            has=self.page.locator(".dash-tile-header", has_text=name),
        )

    def tile_value(self, name: str) -> Locator:
        return self.tile(name).locator(".dash-tile-text")

    def tile_settings_link(self, name: str) -> Locator:
        return self.tile(name).locator(".dash-tile-options a")

    # ------------------
    # Actions: main part
    # ------------------

    def click_quick_link(self, name: str) -> None:
        self.quick_link(name).click()

    def click_tile_settings(self, name: str) -> None:
        self.tile_settings_link(name).click()

    # --------
    # Readings
    # --------

    def first_name_text(self) -> str:
        return self.first_name.inner_text().strip()

    def quick_link_badge_text(self, name: str) -> str:
        return self.quick_link_badge(name).inner_text().strip()

    def tile_value_text(self, name: str) -> str:
        return self.tile_value(name).inner_text().strip()

    def tile_names(self) -> list[str]:
        return [t.strip() for t in self.tile_headers.all_inner_texts()]

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.URL_PATTERN)
        expect(self.heading).to_have_text(self.HEADING_TEXT)
        self.expect_side_menu_selected("Account Dashboard")

    def expect_first_name(self, first_name: str) -> None:
        expect(self.first_name).to_have_text(first_name)

    def expect_quick_links(self) -> None:
        expect(self.quick_links).to_have_count(len(self.QUICK_LINKS))

    def expect_quick_link_badge(self, name: str, value: str) -> None:
        expect(self.quick_link_badge(name)).to_have_text(value)

    def expect_tiles(self) -> None:
        expect(self.tile_headers).to_have_text(list(self.TILES))

    def expect_tile_value(self, name: str, value: str) -> None:
        expect(self.tile_value(name)).to_have_text(value)

    # endregion
    # ==========================================================================================================
