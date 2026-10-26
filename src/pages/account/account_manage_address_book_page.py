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

    PATH = "/index.php?rt=account/address"
    URL_PATTERN = re.compile(r"rt=account/address")

    HEADING_TEXT = "Address Book"
    ENTRIES_HEADING_TEXT = "Address Book Entries"

    # Success alerts after address operations (rt=account/address/insert|update|delete -> redirect here)
    ADDRESS_INSERTED_TEXT = "Your address has been successfully inserted"
    ADDRESS_UPDATED_TEXT = "Your address has been successfully updated"
    ADDRESS_DELETED_TEXT = "Your address has been successfully deleted"

    # The default address has no Delete button, so this selector doubles as a "not default" indicator
    DELETE_BUTTON_SELECTOR = "a[title='Delete'], button[title='Delete']"

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
        self.delete_buttons = page.locator(f".contentpanel .genericbox :is({self.DELETE_BUTTON_SELECTOR})")
        self.success_alert = page.locator(".alert.alert-success")
        self.error_alert = page.locator(".alert.alert-error, .alert.alert-danger")

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

    def entry_delete_button(self, index: int = 0) -> Locator:
        return self.entry(index).locator(self.DELETE_BUTTON_SELECTOR)

    def entry_delete_button_containing(self, text: str) -> Locator:
        return self.entry_containing(text).locator(self.DELETE_BUTTON_SELECTOR)

    # ------------------
    # Actions: main part
    # ------------------

    def open(self) -> None:
        self.goto(self.PATH)

    def click_edit_address(self, index: int = 0) -> None:
        self.entry_edit_button(index).click()

    def click_edit_address_containing(self, text: str) -> None:
        self.entry_containing(text).locator("button[title='Edit']").click()

    def click_delete_address_containing(self, text: str) -> None:
        # Without a listener Playwright auto-dismisses dialogs, which would cancel a confirm() and the deletion.
        # The handler is removed afterwards so it can't accept a dialog that belongs to a later action.
        def accept_dialog(dialog) -> None:
            dialog.accept()

        # Fail fast with a readable message instead of a 30 s click timeout (e.g. when the address is the default one)
        expect(self.entry_delete_button_containing(text)).to_be_visible()
        self.page.on("dialog", accept_dialog)
        try:
            self.entry_delete_button_containing(text).click()
        finally:
            self.page.remove_listener("dialog", accept_dialog)

    def click_new_address(self) -> None:
        self.new_address_button.click()

    def click_back(self) -> None:
        self.back_button.click()

    # --------
    # Readings
    # --------

    def addresses_count(self) -> int:
        return self.entries.count()

    def has_delete_button_containing(self, text: str) -> bool:
        # Instant check (no auto-wait): call it only after the list has been asserted as loaded
        return self.entry_delete_button_containing(text).count() > 0

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

    def expect_success_alert(self, text: str) -> None:
        expect(self.success_alert).to_be_visible()
        expect(self.success_alert).to_contain_text(text)

    def expect_address_inserted_alert(self) -> None:
        self.expect_success_alert(self.ADDRESS_INSERTED_TEXT)

    def expect_address_updated_alert(self) -> None:
        self.expect_success_alert(self.ADDRESS_UPDATED_TEXT)

    def expect_address_deleted_alert(self) -> None:
        self.expect_success_alert(self.ADDRESS_DELETED_TEXT)

    def expect_delete_button_visible(self, text: str) -> None:
        expect(self.entry_delete_button_containing(text)).to_be_visible()

    def expect_no_delete_button(self, text: str) -> None:
        expect(self.entry_delete_button_containing(text)).to_have_count(0)

    def expect_addresses_count(self, count: int) -> None:
        expect(self.entries).to_have_count(count)

    def expect_address_listed(self, text: str) -> None:
        expect(self.entry_containing(text)).to_be_visible()

    def expect_address_not_listed(self, text: str) -> None:
        expect(self.entry_containing(text)).to_have_count(0)

    def expect_address_lines(self, lines: list[str], index: int = 0) -> None:
        # use_inner_text: z <br> robi się spacja (textContent skleiłby linie bez separatora)
        expect(self.entry_address(index)).to_have_text(" ".join(lines), use_inner_text=True)

    def expect_address_lines_containing(self, marker: str, lines: list[str]) -> None:
        expect(self.entry_containing(marker).locator("address")).to_have_text(" ".join(lines), use_inner_text=True)

    def expect_address_contains(self, marker: str, values: list[str]) -> None:
        # Order-agnostic: the store decides how it formats the address (e.g. "city postcode" in one line)
        address = self.entry_containing(marker).locator("address")
        for value in values:
            expect(address).to_contain_text(value)

    # endregion
    # ==========================================================================================================
