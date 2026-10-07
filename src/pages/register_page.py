from playwright.sync_api import Locator, Page, expect

from base_page import BasePage


class RegisterPage(BasePage):
    """
    Create Account page (index.php?rt=account/create): registration form split into
    four sections (personal details, address, login details, newsletter) + privacy policy and submit.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    PATH = "/index.php?rt=account/create"

    # Form fields: name ➤ id suffix (the id is always AccountFrm_<name>)
    FIELDS = (
        "firstname", "lastname", "email", "telephone", "fax",
        "company", "address_1", "address_2", "city", "zone_id", "postcode", "country_id",
        "loginname", "password", "confirm",
    )

    # Required fields (marked with a red asterisk)
    REQUIRED_FIELDS = (
        "firstname", "lastname", "email",
        "address_1", "city", "zone_id", "postcode", "country_id",
        "loginname", "password", "confirm",
    )

    # Error messages (verified after submitting an empty form)
    ERRORS = {
        "firstname": "First Name must be between 1 and 32 characters!",
        "lastname": "Last Name must be between 1 and 32 characters!",
        "email": "Email Address does not appear to be valid!",
        "address_1": "Address 1 must be between 3 and 128 characters!",
        "city": "City must be between 3 and 128 characters!",
        "zone_id": "Please select a region / state!",
        "postcode": "Zip/postal code must be between 3 and 10 characters!",
        "loginname": "Login name must be alphanumeric only and between 5 and 64 characters!",
        "password": "Password must be between 4 and 20 characters!",
    }
    PRIVACY_POLICY_ERROR = "Error: You must agree to the Privacy Policy!"

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region LOCATORS
    # ==========================================================================================================

    def __init__(self, page: Page):
        super().__init__(page)

        # ------------
        # Page heading
        # ------------

        self.breadcrumb = page.locator("ul.breadcrumb")
        self.heading = page.locator("h1.heading1 .maintext")
        self.form = page.locator("#AccountFrm")
        self.login_page_link = page.locator("#AccountFrm > p a")
        self.section_headings = page.locator("#AccountFrm h4.heading4")

        # ---------------------
        # Your Personal Details
        # ---------------------

        self.first_name_input = page.locator("#AccountFrm_firstname")
        self.last_name_input = page.locator("#AccountFrm_lastname")
        self.email_input = page.locator("#AccountFrm_email")
        self.telephone_input = page.locator("#AccountFrm_telephone")
        self.fax_input = page.locator("#AccountFrm_fax")

        # ------------
        # Your Address
        # ------------

        self.company_input = page.locator("#AccountFrm_company")
        self.address_1_input = page.locator("#AccountFrm_address_1")
        self.address_2_input = page.locator("#AccountFrm_address_2")
        self.city_input = page.locator("#AccountFrm_city")
        self.region_select = page.locator("#AccountFrm_zone_id")  # options loaded by AJAX after country selection
        self.postcode_input = page.locator("#AccountFrm_postcode")
        self.country_select = page.locator("#AccountFrm_country_id")

        # -------------
        # Login Details
        # -------------

        self.login_name_input = page.locator("#AccountFrm_loginname")
        self.password_input = page.locator("#AccountFrm_password")
        self.password_confirm_input = page.locator("#AccountFrm_confirm")

        # ----------
        # Newsletter
        # ----------

        self.newsletter_yes_radio = page.locator("#AccountFrm_newsletter1")
        self.newsletter_no_radio = page.locator("#AccountFrm_newsletter0")

        # ----------------
        # Privacy + submit
        # ----------------

        self.privacy_policy_link = page.locator("#AccountFrm a[href*='content_id=2']")
        self.privacy_policy_modal = page.locator("#privacyPolicyModal")
        self.privacy_policy_modal_close_button = page.locator("#privacyPolicyModal .modal-footer button")
        self.agree_checkbox = page.locator("#AccountFrm_agree")
        self.continue_button = page.locator("#AccountFrm button[title='Continue']")

        # ----------
        # Validation
        # ----------

        # Errors under fields: group gets class has-error and text goes to .help-block
        self.invalid_form_groups = page.locator("#AccountFrm .form-group.has-error")
        self.field_errors = page.locator("#AccountFrm .form-group.has-error .help-block")

        # Alert above the form: no agreement to the privacy policy OR list of all field errors (<br> between entries)
        self.error_alert = page.locator(".alert.alert-error")
        self.error_alert_close_button = page.locator(".alert.alert-error button.close")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------
    # Navigation
    # ----------

    def goto(self, path: str = PATH):
        super().goto(path)

    # ----------------
    # Dynamic locators
    # ----------------

    def field(self, name: str) -> Locator:
        return self.page.locator(f"#AccountFrm_{name}")

    def field_error(self, name: str) -> Locator:
        return self.page.locator("#AccountFrm .form-group", has=self.field(name)).locator(".help-block")

    # ----------------------
    # Actions: Personal data
    # ----------------------

    def fill_personal_details(
            self, first_name: str, last_name: str, email: str, telephone: str = "", fax: str = ""
    ) -> None:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        if telephone:
            self.telephone_input.fill(telephone)
        if fax:
            self.fax_input.fill(fax)

    # ----------------
    # Actions: Address
    # ----------------

    def fill_address(
            self,
            address_1: str,
            city: str,
            postcode: str,
            country: str,
            region: str,
            company: str = "",
            address_2: str = "",
    ) -> None:
        if company:
            self.company_input.fill(company)
        self.address_1_input.fill(address_1)
        if address_2:
            self.address_2_input.fill(address_2)
        self.city_input.fill(city)
        self.postcode_input.fill(postcode)
        self.select_country(country)
        self.select_region(region)

    def select_country(self, country: str) -> None:
        self.country_select.select_option(label=country)

    def select_region(self, region: str) -> None:
        # Region list is reloaded after country change – select_option waits until option appears
        self.region_select.select_option(label=region)

    # ----------------------
    # Actions: Login details
    # ----------------------

    def fill_login_details(self, login_name: str, password: str, password_confirm: str | None = None) -> None:
        self.login_name_input.fill(login_name)
        self.password_input.fill(password)
        self.password_confirm_input.fill(password if password_confirm is None else password_confirm)

    # -------------------
    # Actions: Newsletter
    # -------------------

    def subscribe_newsletter(self, subscribe: bool = True) -> None:
        (self.newsletter_yes_radio if subscribe else self.newsletter_no_radio).check()

    # ---------------------------
    # Actions: Privacy and submit
    # ---------------------------

    def open_privacy_policy(self) -> None:
        self.privacy_policy_link.click()

    def close_privacy_policy(self) -> None:
        self.privacy_policy_modal_close_button.click()

    def accept_privacy_policy(self) -> None:
        self.agree_checkbox.check()

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_login_page_link(self) -> None:
        self.login_page_link.click()

    def register(
            self,
            first_name: str,
            last_name: str,
            email: str,
            address_1: str,
            city: str,
            postcode: str,
            country: str,
            region: str,
            login_name: str,
            password: str,
            newsletter: bool | None = None,
            agree: bool = True,
    ) -> None:
        """Fills out the required fields and submits the form (complete optional fields using separate methods)."""
        self.fill_personal_details(first_name, last_name, email)
        self.fill_address(address_1, city, postcode, country, region)
        self.fill_login_details(login_name, password)
        if newsletter is not None:
            self.subscribe_newsletter(newsletter)
        if agree:
            self.accept_privacy_policy()
        self.click_continue()

    # --------
    # Readings
    # --------

    def heading_text(self) -> str:
        return self.heading.inner_text().strip()

    def section_heading_names(self) -> list[str]:
        return [t.strip() for t in self.section_headings.all_inner_texts()]

    def field_error_text(self, name: str) -> str:
        return self.field_error(name).inner_text().strip()

    def error_alert_text(self) -> str:
        return self.error_alert.inner_text().replace("×", "").strip()

    def error_alert_messages(self) -> list[str]:
        lines = self.error_alert.inner_text().replace("×", "").splitlines()
        return [line.strip() for line in lines if line.strip()]

    def fields_with_errors(self) -> list[str]:
        return [
            g.locator("input, select").first.evaluate("el => el.name")
            for g in self.invalid_form_groups.all()
        ]

    def selected_country_text(self) -> str:
        return self.country_select.locator("option:checked").inner_text().strip()

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_loaded(self) -> None:
        expect(self.heading).to_contain_text("Create Account")
        expect(self.form).to_be_visible()

    def expect_field_error(self, name: str, text: str | None = None) -> None:
        if text is None:
            expect(self.field_error(name)).not_to_be_empty()
        else:
            expect(self.field_error(name)).to_contain_text(text)

    def expect_no_field_errors(self) -> None:
        expect(self.invalid_form_groups).to_have_count(0)

    def expect_error_alert(self, text: str) -> None:
        expect(self.error_alert).to_contain_text(text)

    def expect_required_field_errors(self) -> None:
        """Empty form with consent selected: errors under the fields + the same messages collected in the alert."""
        for name, message in self.ERRORS.items():
            self.expect_field_error(name, message)
            expect(self.error_alert).to_contain_text(message)
        expect(self.invalid_form_groups).to_have_count(len(self.ERRORS))

    def expect_privacy_policy_error(self) -> None:
        self.expect_error_alert(self.PRIVACY_POLICY_ERROR)

    def expect_privacy_policy_visible(self) -> None:
        expect(self.privacy_policy_modal).to_be_visible()

    # endregion
    # ==========================================================================================================
