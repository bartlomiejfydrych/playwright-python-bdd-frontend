import re

from playwright.sync_api import Locator, Page, expect

from src.pages.account.account_base_page import AccountBasePage


class AccountManageAddressBookPage(AccountBasePage):
    """
    Address book "Address Book" (rt=account/address): list of saved addresses (each with an Edit button)
    and the Back / New Address buttons.
    Breadcrumbs, heading and the "My Account" side menu come from AccountBasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/address")

    HEADING_TEXT = "Address Book"
    ENTRIES_HEADING_TEXT = "Address Book Entries"

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

        # Breadcrumbs: Home > Account > Address Book (the last item is specific to this page)
        self.breadcrumb_address_book_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='account/address']")

        # Address entries (each in its own .genericbox: <address> with lines separated by <br> + Edit button)
        self.entries_heading = page.locator(".contentpanel h4.heading4")
        self.entries = page.locator(".contentpanel .genericbox")
        self.entry_addresses = page.locator(".contentpanel .genericbox address")
        self.edit_buttons = page.locator(".contentpanel .genericbox button[title='Edit']")

        # Buttons under the list
        self.back_button = page.locator(".contentpanel a.btn[title='Back']")
        self.new_address_button = page.locator(".contentpanel a.btn[title='New Address']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def entry(self, index: int = 0) -> Locator:
        return self.entries.nth(index)

    def entry_containing(self, text: str) -> Locator:
        return self.entries.filter(has_text=text)

    def entry_address(self, index: int = 0) -> Locator:
        return self.entry(index).locator("address")

    def entry_edit_button(self, index: int = 0) -> Locator:
        return self.entry(index).locator("button[title='Edit']")

    # ------------------
    # Actions: main part
    # ------------------

    def click_edit_address(self, index: int = 0) -> None:
        self.entry_edit_button(index).click()

    def click_edit_address_containing(self, text: str) -> None:
        self.entry_containing(text).locator("button[title='Edit']").click()

    def click_new_address(self) -> None:
        self.new_address_button.click()

    def click_back(self) -> None:
        self.back_button.click()

    # --------
    # Readings
    # --------

    def addresses_count(self) -> int:
        return self.entries.count()

    def address_lines(self, index: int = 0) -> list[str]:
        # Address lines are separated by <br>, inner_text replaces them with newlines
        text = self.entry_address(index).inner_text()
        return [line.strip() for line in text.splitlines() if line.strip()]

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
        self.expect_side_menu_selected("Manage Address Book")

    def expect_addresses_count(self, count: int) -> None:
        expect(self.entries).to_have_count(count)

    def expect_address_listed(self, text: str) -> None:
        expect(self.entry_containing(text)).to_be_visible()

    def expect_address_not_listed(self, text: str) -> None:
        expect(self.entry_containing(text)).to_have_count(0)

    def expect_address_lines(self, lines: list[str], index: int = 0) -> None:
        # use_inner_text: z <br> robi się spacja (textContent skleiłby linie bez separatora)
        expect(self.entry_address(index)).to_have_text(" ".join(lines), use_inner_text=True)

    # endregion
    # ==========================================================================================================
