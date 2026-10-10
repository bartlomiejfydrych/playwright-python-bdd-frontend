import re

from playwright.sync_api import Locator, Page, expect

from src.pages.account.account_base_page import AccountBasePage


class AccountEditAccountDetailsPage(AccountBasePage):
    """
    Account details form "My Account Information" (rt=account/edit): read-only login name
    and editable first name, last name, e-mail, telephone and fax.
    Breadcrumbs, heading and the "My Account" side menu come from AccountBasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/edit")

    HEADING_TEXT = "My Account Information"
    PERSONAL_DETAILS_TEXT = "Your Personal Details"

    # Form fields: name ➤ input name (id = AccountFrm_<name>)
    FIELDS = ("firstname", "lastname", "email", "telephone", "fax")
    REQUIRED_FIELDS = ("firstname", "lastname", "email")

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

        # Breadcrumbs: Home > Account > Edit Information (the last item is specific to this page)
        self.breadcrumb_edit_information_link = page.locator(
            "section.breadcrumbs ul.breadcrumb a[href*='account/edit']")

        # Form
        self.form = page.locator("#AccountFrm")
        self.personal_details_heading = page.locator("#AccountFrm h4.heading4")

        # Login name is plain text (not an input), the text node sits directly in .input-group
        self.login_name = page.locator("#AccountFrm .form-group", has_text="Login Name:").locator(".input-group")

        self.first_name_input = page.locator("#AccountFrm_firstname")
        self.last_name_input = page.locator("#AccountFrm_lastname")
        self.email_input = page.locator("#AccountFrm_email")
        self.telephone_input = page.locator("#AccountFrm_telephone")
        self.fax_input = page.locator("#AccountFrm_fax")

        # Buttons
        self.continue_button = page.locator("#AccountFrm button[type='submit']")
        self.back_button = page.locator("#AccountFrm a[title='Back']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def field_input(self, field: str) -> Locator:
        return self.page.locator(f"#AccountFrm_{field}")

    def field_group(self, field: str) -> Locator:
        return self.page.locator("#AccountFrm .form-group", has=self.field_input(field))

    def field_error(self, field: str) -> Locator:
        return self.field_group(field).locator(".help-block")

    def field_required_marker(self, field: str) -> Locator:
        return self.field_group(field).locator(".input-group-addon .required")

    # ------------------
    # Actions: main part
    # ------------------

    def fill_form(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            email: str | None = None,
            telephone: str | None = None,
            fax: str | None = None,
    ) -> None:
        # None = do not touch the field, "" = clear the field
        values = {
            "firstname": first_name,
            "lastname": last_name,
            "email": email,
            "telephone": telephone,
            "fax": fax,
        }
        for field, value in values.items():
            if value is not None:
                self.field_input(field).fill(value)

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_back(self) -> None:
        self.back_button.click()

    def edit_account(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            email: str | None = None,
            telephone: str | None = None,
            fax: str | None = None,
    ) -> None:
        self.fill_form(first_name, last_name, email, telephone, fax)
        self.click_continue()

    # --------
    # Readings
    # --------

    def login_name_text(self) -> str:
        return self.login_name.inner_text().strip()

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
        self.expect_side_menu_selected("Edit account details")

    def expect_login_name(self, login_name: str) -> None:
        expect(self.login_name).to_have_text(login_name)

    def expect_field_value(self, field: str, value: str) -> None:
        expect(self.field_input(field)).to_have_value(value)

    def expect_required_fields(self) -> None:
        for field in self.REQUIRED_FIELDS:
            expect(self.field_required_marker(field)).to_be_visible()
        for field in set(self.FIELDS) - set(self.REQUIRED_FIELDS):
            expect(self.field_required_marker(field)).to_have_count(0)

    def expect_field_error(self, field: str, message: str) -> None:
        expect(self.field_error(field)).to_have_text(message)

    def expect_no_field_errors(self) -> None:
        for field in self.FIELDS:
            expect(self.field_error(field)).to_have_text("")

    # endregion
    # ==========================================================================================================
