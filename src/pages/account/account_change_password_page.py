import re

from playwright.sync_api import Locator, Page, expect

from src.pages.account.account_base_page import AccountBasePage


class AccountChangePasswordPage(AccountBasePage):
    """
    Password change form "Change Password" (rt=account/password): current password,
    new password and its confirmation (all required, masked).
    Breadcrumbs, heading and the "My Account" side menu come from AccountBasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/password")

    HEADING_TEXT = "Change Password"
    INSTRUCTION_TEXT = "To update your password, please provide current and new password details"

    # Form fields: input name (id = PasswordFrm_<name>); all of them are required
    FIELDS = ("current_password", "password", "confirm")

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

        # Breadcrumbs: Home > Account > Change Password (the last item is specific to this page)
        self.breadcrumb_change_password_link = page.locator(
            "section.breadcrumbs ul.breadcrumb a[href*='account/password']")

        # Form
        self.form = page.locator("#PasswordFrm")
        self.instruction = page.locator("#PasswordFrm h4.heading4")

        self.current_password_input = page.locator("#PasswordFrm_current_password")
        self.new_password_input = page.locator("#PasswordFrm_password")
        self.confirm_password_input = page.locator("#PasswordFrm_confirm")

        # Buttons
        self.continue_button = page.locator("#PasswordFrm button[type='submit']")
        self.back_button = page.locator("#PasswordFrm a[title='Back']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def field_input(self, field: str) -> Locator:
        return self.page.locator(f"#PasswordFrm_{field}")

    def field_group(self, field: str) -> Locator:
        return self.page.locator("#PasswordFrm .form-group", has=self.field_input(field))

    def field_error(self, field: str) -> Locator:
        return self.field_group(field).locator(".help-block")

    def field_required_marker(self, field: str) -> Locator:
        return self.field_group(field).locator(".input-group-addon .required")

    # ------------------
    # Actions: main part
    # ------------------

    def fill_form(
            self,
            current_password: str | None = None,
            new_password: str | None = None,
            confirm_password: str | None = None,
    ) -> None:
        # None = do not touch the field, "" = clear the field
        values = {
            "current_password": current_password,
            "password": new_password,
            "confirm": confirm_password,
        }
        for field, value in values.items():
            if value is not None:
                self.field_input(field).fill(value)

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_back(self) -> None:
        self.back_button.click()

    def change_password(
            self,
            current_password: str,
            new_password: str,
            confirm_password: str | None = None,
    ) -> None:
        # No confirm password = confirmation same as new password
        if confirm_password is None:
            confirm_password = new_password
        self.fill_form(current_password, new_password, confirm_password)
        self.click_continue()

    # --------
    # Readings
    # --------

    def field_value(self, field: str) -> str:
        return self.field_input(field).input_value()

    def field_error_text(self, field: str) -> str:
        return self.field_error(field).inner_text().strip()

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
        self.expect_side_menu_selected("Change password")

    def expect_instruction(self) -> None:
        expect(self.instruction).to_have_text(self.INSTRUCTION_TEXT)

    def expect_fields_empty(self) -> None:
        for field in self.FIELDS:
            expect(self.field_input(field)).to_have_value("")

    def expect_fields_masked(self) -> None:
        for field in self.FIELDS:
            expect(self.field_input(field)).to_have_attribute("type", "password")

    def expect_required_fields(self) -> None:
        for field in self.FIELDS:
            expect(self.field_required_marker(field)).to_be_visible()

    def expect_field_error(self, field: str, message: str) -> None:
        expect(self.field_error(field)).to_have_text(message)

    def expect_no_field_errors(self) -> None:
        for field in self.FIELDS:
            expect(self.field_error(field)).to_have_text("")

    # endregion
    # ==========================================================================================================
