import re

from playwright.sync_api import Locator, Page, expect

from src.pages.account.account_base_page import AccountBasePage


class AccountNotificationsPage(AccountBasePage):
    """
    Notification settings "Notifications and Newsletter" (rt=account/notification): table with e-mail checkboxes
    (Newsletters is editable, Order Update and Account Update are always on and locked).
    Breadcrumbs, heading and the "My Account" side menu come from AccountBasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/notification")

    HEADING_TEXT = "Notifications and Newsletter"

    COLUMNS = ("Notifications", "E-mail")

    # Notifications: name ➤ setting key (input name = settings[<key>][email])
    NOTIFICATIONS = {
        "Newsletters": "newsletter",
        "Order Update": "order_update",
        "Account Update": "customer_account_update",
    }
    # Always on, the checkbox is disabled
    LOCKED_NOTIFICATIONS = ("Order Update", "Account Update")

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

        # Breadcrumbs: Home > Account > Notifications (the last item is specific to this page)
        self.breadcrumb_notifications_link = page.locator(
            "section.breadcrumbs ul.breadcrumb a[href*='account/notification']")

        # Form (note: the form wraps .contentpanel, so locators start from #imFrm)
        self.form = page.locator("#imFrm")
        self.column_headers = page.locator("#imFrm table.notification-table th")
        self.rows = page.locator("#imFrm table.notification-table tbody tr")
        self.notification_names_cells = page.locator("#imFrm table.notification-table tbody tr td:first-child")

        # Checkboxes
        self.newsletter_checkbox = page.locator("input[name='settings[newsletter][email]']")
        self.order_update_checkbox = page.locator("input[name='settings[order_update][email]']")
        self.account_update_checkbox = page.locator("input[name='settings[customer_account_update][email]']")

        # Buttons
        self.continue_button = page.locator("#imFrm button[type='submit']")
        self.back_button = page.locator("#imFrm a[title='Back']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def row(self, name: str) -> Locator:
        return self.rows.filter(has=self.page.locator("td:first-child", has_text=name))

    def notification_checkbox(self, name: str) -> Locator:
        key = self.NOTIFICATIONS[name]
        return self.page.locator(f"input[name='settings[{key}][email]']")

    def notification_description(self, name: str) -> Locator:
        return self.row(name).locator("small")

    # ------------------
    # Actions: main part
    # ------------------

    def set_newsletter(self, subscribed: bool) -> None:
        self.newsletter_checkbox.set_checked(subscribed)

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_back(self) -> None:
        self.back_button.click()

    def save_newsletter_subscription(self, subscribed: bool) -> None:
        self.set_newsletter(subscribed)
        self.click_continue()

    # --------
    # Readings
    # --------

    def notification_names(self) -> list[str]:
        # In the cell there is a name + description in <small>, we take only the first line (name)
        return [
            t.strip().splitlines()[0].strip()
            for t in self.notification_names_cells.all_inner_texts()
        ]

    def description_text(self, name: str) -> str:
        return self.notification_description(name).inner_text().strip()

    def is_checked(self, name: str) -> bool:
        return self.notification_checkbox(name).is_checked()

    def is_enabled(self, name: str) -> bool:
        return self.notification_checkbox(name).is_enabled()

    def is_newsletter_subscribed(self) -> bool:
        return self.newsletter_checkbox.is_checked()

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
        self.expect_side_menu_selected("Notifications")

    def expect_columns(self) -> None:
        expect(self.column_headers).to_have_text(list(self.COLUMNS))

    def expect_notifications_listed(self) -> None:
        expect(self.rows).to_have_count(len(self.NOTIFICATIONS))
        for name in self.NOTIFICATIONS:
            expect(self.row(name)).to_be_visible()

    def expect_newsletter_subscribed(self, subscribed: bool) -> None:
        if subscribed:
            expect(self.newsletter_checkbox).to_be_checked()
        else:
            expect(self.newsletter_checkbox).not_to_be_checked()

    def expect_locked_notifications(self) -> None:
        # Order Update and Account Update: checked and not editable
        for name in self.LOCKED_NOTIFICATIONS:
            expect(self.notification_checkbox(name)).to_be_checked()
            expect(self.notification_checkbox(name)).to_be_disabled()

    # endregion
    # ==========================================================================================================
