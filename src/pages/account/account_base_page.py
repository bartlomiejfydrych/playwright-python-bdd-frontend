from playwright.sync_api import Locator, Page, expect

from src.pages.base_page import BasePage


class AccountBasePage(BasePage):
    """
    Common elements across account pages (success, dashboard, edit, wishlist, history...):
    breadcrumbs and the "My Account" side menu.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    # Side menu "My Account": name ➤ href fragment
    SIDE_MENU_ITEMS = {
        "Account Dashboard": "account/account",
        "My wish list": "account/wishlist",
        "Edit account details": "account/edit",
        "Change password": "account/password",
        "Manage Address Book": "account/address",
        "Order history": "account/history",
        "Transaction history": "account/transactions",
        "Downloads": "account/download",
        "Notifications": "account/notification",
        "Logoff": "account/logout",
    }

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

        # Heading (h1; its subtext differs per page)
        self.heading = page.locator("h1.heading1 .maintext")

        # Breadcrumbs (e.g. Home > Account > Success)
        self.breadcrumbs = page.locator("section.breadcrumbs ul.breadcrumb")
        self.breadcrumb_items = page.locator("section.breadcrumbs ul.breadcrumb li a")
        self.breadcrumb_home_link = page.locator("section.breadcrumbs ul.breadcrumb a:has(i.fa-home)")
        self.breadcrumb_account_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='account/account']")

        # Side menu "My Account"
        self.side_menu = page.locator(".myaccountbox ul.side_account_list")
        self.side_menu_title = page.locator(".sidewidt h2.heading2 span", has_text="My Account")
        self.side_menu_links = page.locator(".myaccountbox ul.side_account_list a")
        self.side_menu_selected_link = page.locator(".myaccountbox ul.side_account_list li.selected a")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def side_menu_link(self, name: str) -> Locator:
        fragment = self.SIDE_MENU_ITEMS[name]
        return self.page.locator(f".myaccountbox ul.side_account_list a[href*='{fragment}']")

    # ------------------
    # Actions: main part
    # ------------------

    def click_breadcrumb_home(self) -> None:
        self.breadcrumb_home_link.click()

    def click_breadcrumb_account(self) -> None:
        self.breadcrumb_account_link.click()

    # ------------------
    # Actions: side menu
    # ------------------

    def open_side_menu_item(self, name: str) -> None:
        self.side_menu_link(name).click()

    def click_logoff(self) -> None:
        self.side_menu_link("Logoff").click()

    # --------
    # Readings
    # --------

    def heading_text(self) -> str:
        return self.heading.inner_text().strip()

    def breadcrumb_names(self) -> list[str]:
        return [t.strip() for t in self.breadcrumb_items.all_inner_texts()]

    def side_menu_names(self) -> list[str]:
        # &nbsp; before the name -> strip() also removes the non-breaking space
        return [t.strip() for t in self.side_menu_links.all_inner_texts()]

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_breadcrumbs(self, *names: str) -> None:
        expect(self.breadcrumb_items).to_have_text(list(names))

    def expect_side_menu_selected(self, name: str) -> None:
        expect(self.side_menu_selected_link).to_have_text(name)

    def expect_side_menu_items(self) -> None:
        expect(self.side_menu_links).to_have_text(list(self.SIDE_MENU_ITEMS), use_inner_text=True)

    # endregion
    # ==========================================================================================================
