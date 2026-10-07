from playwright.sync_api import Locator, Page, expect

from base_page import BasePage


class OrderDetailsPage(BasePage):
    """
    "Order Details" page (Account > Check Your Order, rt=account/invoice):
    a form where a guest checks an order by order ID and e-mail.
    Handles both states: the clean form and the form after submitting empty fields (validation errors).
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    PATH = "/index.php?rt=account/invoice"
    TITLE = "Order Details"

    ORDER_ID_REQUIRED_ERROR = "Order ID is required field!"
    EMAIL_INVALID_ERROR = "E-Mail Address does not appear to be valid!"

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

        # Heading and breadcrumbs
        self.heading = page.locator("h1.heading1 .maintext")
        self.breadcrumbs = page.locator("ul.breadcrumb li")
        self.breadcrumb_home_link = page.locator("ul.breadcrumb a[href$='/']")
        self.breadcrumb_account_link = page.locator("ul.breadcrumb a[href*='rt=account/account']")

        # Form
        self.form = page.locator("#CheckOrderFrm")
        self.order_id_input = page.locator("#CheckOrderFrm_order_id")
        self.email_input = page.locator("#CheckOrderFrm_email")
        self.required_marks = page.locator("#CheckOrderFrm .input-group-addon .required")
        self.continue_button = page.locator("#CheckOrderFrm button[type='submit']")
        self.back_button = page.locator("#CheckOrderFrm a[title='Back']")

        # Validation (visible only after submitting; the group gets .has-error and a .help-block appears)
        self.order_id_group = page.locator("#CheckOrderFrm .form-group", has=self.order_id_input)
        self.email_group = page.locator("#CheckOrderFrm .form-group", has=self.email_input)
        self.order_id_error = self.order_id_group.locator(".help-block")
        self.email_error = self.email_group.locator(".help-block")
        self.error_groups = page.locator("#CheckOrderFrm .form-group.has-error")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------
    # Navigation
    # ----------

    def open(self) -> None:
        self.goto(self.PATH)

    # -------------
    # Actions: Form
    # -------------

    def fill_order_id(self, order_id: str) -> None:
        self.order_id_input.fill(order_id)

    def fill_email(self, email: str) -> None:
        self.email_input.fill(email)

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_back(self) -> None:
        self.back_button.click()

    def submit_empty_form(self) -> None:
        self.order_id_input.clear()
        self.email_input.clear()
        self.click_continue()

    def check_order(self, order_id: str, email: str) -> None:
        self.fill_order_id(order_id)
        self.fill_email(email)
        self.click_continue()

    # --------------------
    # Actions: Breadcrumbs
    # --------------------

    def click_breadcrumb_home(self) -> None:
        self.breadcrumb_home_link.click()

    def click_breadcrumb_account(self) -> None:
        self.breadcrumb_account_link.click()

    # --------
    # Readings
    # --------

    def heading_text(self) -> str:
        return self.heading.inner_text().strip()

    def breadcrumb_names(self) -> list[str]:
        return [t.strip() for t in self.breadcrumbs.all_inner_texts()]

    def order_id_value(self) -> str:
        return self.order_id_input.input_value()

    def email_value(self) -> str:
        return self.email_input.input_value()

    def order_id_error_text(self) -> str:
        return self.order_id_error.inner_text().strip()

    def email_error_text(self) -> str:
        return self.email_error.inner_text().strip()

    def validation_errors_count(self) -> int:
        return self.error_groups.count()

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self) -> None:
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.TITLE)
        expect(self.form).to_be_visible()

    def expect_empty_form(self) -> None:
        expect(self.order_id_input).to_have_value("")
        expect(self.email_input).to_have_value("")
        expect(self.required_marks).to_have_count(2)

    def expect_no_validation_errors(self) -> None:
        expect(self.error_groups).to_have_count(0)

    def expect_order_id_required_error(self) -> None:
        expect(self.order_id_group).to_have_class(r".*has-error.*")
        expect(self.order_id_error).to_have_text(self.ORDER_ID_REQUIRED_ERROR)

    def expect_email_invalid_error(self) -> None:
        expect(self.email_group).to_have_class(r".*has-error.*")
        expect(self.email_error).to_have_text(self.EMAIL_INVALID_ERROR)

    def expect_empty_form_errors(self) -> None:
        """State after submitting empty fields: both fields flagged."""
        expect(self.error_groups).to_have_count(2)
        self.expect_order_id_required_error()
        self.expect_email_invalid_error()

    # endregion
    # ==========================================================================================================
