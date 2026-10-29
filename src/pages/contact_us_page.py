import re

from playwright.sync_api import Locator, Page, expect

from src.pages.base_page import BasePage


class ContactUsPage(BasePage):
    """
    Contact form "Contact Us" (rt=content/contact) and the confirmation page after sending
    it (rt=content/contact/success). Both pages share the same h1 and breadcrumbs, only the
    content of .contentpanel differs, so one page object covers both states.
    Everything else (header, footer, search box...) lives in BasePage.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    PATH = "/index.php?rt=content/contact"
    # Form: .../contact (a failed submit lands on .../contact&form_id=2), the success page is excluded
    URL_PATTERN = re.compile(r"rt=content/contact(?!/success)")
    SUCCESS_URL_PATTERN = re.compile(r"rt=content/contact/success")

    TITLE = "Contact Us"
    HEADING_TEXT = "Contact Us"
    FORM_TITLE = "Contact Us Form"
    SUCCESS_MESSAGE = "Your enquiry has been successfully sent to the store owner!"

    # Contact details displayed on the page (from the supplied page snapshot).
    STORE_ADDRESS_LINES = ("123 Main Street", "Kensington", "London", "SW7 1AA")
    STORE_TELEPHONE = "012345 6781199"

    # Form fields: input name (id = ContactUsFrm_<name>); all of them are required
    FIELDS = ("first_name", "email", "enquiry")

    # Label used in the feature files ➤ input name
    FIELD_BY_LABEL = {
        "First name": "first_name",
        "Email": "email",
        "Enquiry": "enquiry",
    }

    # Errors shown under the fields after submitting an empty form
    EMPTY_FORM_ERRORS = {
        "first_name": "First name: is required field! Name must be between 3 and 32 characters!",
        "email": "Email: is required field! E-Mail Address does not appear to be valid!",
        "enquiry": "Enquiry: is required field! Enquiry must be between 10 and 3000 characters!",
    }

    # Errors for a NON-empty value that breaks the rule (the "is required field!" prefix appears only for empty values)
    INVALID_VALUE_ERRORS = {
        "first_name": "Name must be between 3 and 32 characters!",
        "email": "E-Mail Address does not appear to be valid!",
        "enquiry": "Enquiry must be between 10 and 3000 characters!",
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

        # Heading (on the success page only the icon differs: envelope ➤ thumbs-up)
        self.heading = page.locator("h1.heading1 .maintext")

        # Breadcrumbs: Home > Contact Us
        # UWAGA: po nieudanym wysłaniu formularza ostatni element miał tekst "Shopping Cart" zamiast "Contact Us"
        # (href jest ten sam: content/contact), dlatego nie asertuj tekstu ostatniego elementu, tylko href.
        self.breadcrumbs = page.locator("section.breadcrumbs ul.breadcrumb")
        self.breadcrumb_links = page.locator("section.breadcrumbs ul.breadcrumb a")
        self.breadcrumb_home_link = page.locator("section.breadcrumbs ul.breadcrumb a:has(i.fa-home)")
        self.breadcrumb_contact_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='content/contact']")

        # Store data (no ids in the HTML, so the position in the row is the only handle)
        self.address_block = page.locator(".contentpanel .row > .col-md-6.pull-left")
        self.address = page.locator(".contentpanel address")
        self.telephone_block = page.locator(".contentpanel .row > .col-md-6.pull-right")

        # Form
        self.form = page.locator("#ContactUsFrm")
        self.form_title = page.locator("#ContactUsFrm h3.form_description")

        self.first_name_input = page.locator("#ContactUsFrm_first_name")
        self.email_input = page.locator("#ContactUsFrm_email")
        self.enquiry_input = page.locator("#ContactUsFrm_enquiry")

        # Buttons
        self.reset_button = page.locator("#ContactUsFrm button[type='reset']")
        self.submit_button = page.locator("#ContactUsFrm button[type='submit']")

        # Field errors (there is no .alert box at the top of the page, only messages under the fields)
        self.field_errors = page.locator("#ContactUsFrm .element_error")

        # Success page (rt=content/contact/success)
        self.success_section = page.locator(".contentpanel section.mb40")
        self.success_message = page.locator(".contentpanel section.mb40 p:not(:empty)")  # są też puste <p></p>
        self.continue_button = page.locator(".contentpanel section.mb40 a[title='Continue']")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def open(self) -> None:
        self.goto(self.PATH)

    def field_input(self, field: str) -> Locator:
        return self.page.locator(f"#ContactUsFrm_{field}")

    def field_group(self, field: str) -> Locator:
        return self.page.locator("#ContactUsFrm .form-group.form_field", has=self.field_input(field))

    def field_label(self, field: str) -> Locator:
        return self.field_group(field).locator("label.control-label")

    def field_error(self, field: str) -> Locator:
        return self.field_group(field).locator(".element_error")

    def field_required_marker(self, field: str) -> Locator:
        return self.field_group(field).locator(".input-group-addon .required")

    # ------------------
    # Actions: main part
    # ------------------

    def fill_form(
            self,
            first_name: str | None = None,
            email: str | None = None,
            enquiry: str | None = None,
    ) -> None:
        # None = do not touch the field, "" = clear the field
        values = {
            "first_name": first_name,
            "email": email,
            "enquiry": enquiry,
        }
        for field, value in values.items():
            if value is not None:
                self.field_input(field).fill(value)

    def fill_field(self, field: str, value: str) -> None:
        self.field_input(field).fill(value)

    def click_submit(self) -> None:
        self.submit_button.click()

    def click_reset(self) -> None:
        self.reset_button.click()

    def send_enquiry(self, first_name: str, email: str, enquiry: str) -> None:
        self.fill_form(first_name, email, enquiry)
        self.click_submit()

    def click_continue(self) -> None:
        self.continue_button.click()

    # ---------------------
    # Actions: breadcrumbs
    # ---------------------

    def click_breadcrumb_home(self) -> None:
        self.breadcrumb_home_link.click()

    # --------
    # Readings
    # --------

    def field_value(self, field: str) -> str:
        return self.field_input(field).input_value()

    def field_error_text(self, field: str) -> str:
        return self.field_error(field).inner_text().strip()

    def success_message_text(self) -> str:
        return self.success_message.inner_text().strip()

    def store_address_lines(self) -> list[str]:
        return [line.strip() for line in self.address.inner_text().splitlines() if line.strip()]

    def store_telephone_text(self) -> str:
        return self.telephone_block.inner_text().replace("Telephone:", "").strip()

    def breadcrumb_texts(self) -> list[str]:
        return [t.strip() for t in self.breadcrumb_links.all_inner_texts()]

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
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.HEADING_TEXT)
        expect(self.form).to_be_visible()
        expect(self.form_title).to_have_text(self.FORM_TITLE)

    def expect_fields_empty(self) -> None:
        for field in self.FIELDS:
            expect(self.field_input(field)).to_have_value("")

    def expect_field_value(self, field: str, value: str) -> None:
        expect(self.field_input(field)).to_have_value(value)

    def expect_field_values(self, first_name: str, email: str, enquiry: str) -> None:
        self.expect_field_value("first_name", first_name)
        self.expect_field_value("email", email)
        self.expect_field_value("enquiry", enquiry)

    def expect_required_fields(self) -> None:
        for field in self.FIELDS:
            expect(self.field_required_marker(field)).to_be_visible()

    def expect_store_contact_details(self) -> None:
        expect(self.address).to_be_visible()
        # NOTE FOR ME: expect(...) ponawia sprawdzenie, zwykły assert na odczytanym tekście nie
        for line in self.STORE_ADDRESS_LINES:
            expect(self.address).to_contain_text(line)
        expect(self.telephone_block).to_contain_text("Telephone:")
        expect(self.telephone_block).to_contain_text(self.STORE_TELEPHONE)

    def expect_field_error_visible(self, field: str) -> None:
        expect(self.field_error(field)).to_be_visible()
        expect(self.field_error(field)).not_to_be_empty()

    def expect_form_page_still_open(self) -> None:
        expect(self.page).to_have_url(self.URL_PATTERN)
        expect(self.form).to_be_visible()

    def expect_field_error(self, field: str, message: str) -> None:
        expect(self.field_error(field)).to_have_text(message)

    def expect_only_field_error(self, field: str, message: str) -> None:
        # The error of the tested field has the exact text and no other field shows an error
        self.expect_field_error(field, message)
        for other in self.FIELDS:
            if other != field:
                expect(self.field_error(other)).to_be_hidden()

    def expect_empty_form_errors(self) -> None:
        for field, message in self.EMPTY_FORM_ERRORS.items():
            self.expect_field_error(field, message)

    def expect_no_field_errors(self) -> None:
        # to_be_hidden passes both for an empty and for a missing element
        for field in self.FIELDS:
            expect(self.field_error(field)).to_be_hidden()

    def expect_success_loaded(self) -> None:
        expect(self.page).to_have_url(self.SUCCESS_URL_PATTERN)
        expect(self.page).to_have_title(self.TITLE)
        expect(self.heading).to_have_text(self.HEADING_TEXT)
        expect(self.success_message).to_have_text(self.SUCCESS_MESSAGE)
        expect(self.continue_button).to_be_visible()
        expect(self.form).to_have_count(0)

    # endregion
    # ==========================================================================================================
