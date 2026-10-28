import re
import warnings

from playwright.sync_api import Locator, Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.pages.account.account_base_page import AccountBasePage


class AccountManageAddressBookEditAddressPage(AccountBasePage):
    """
    Address edit form "Edit Address" (rt=account/address/update&address_id=...): name, company, address lines,
    city, region, postcode, country and the default address option.
    Breadcrumbs, heading and the "My Account" side menu come from AccountBasePage
    (on this page no item of the side menu is marked as selected).
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    URL_PATTERN = re.compile(r"rt=account/address/(?:insert|update)")

    HEADING_TEXT = "Address Book"
    FORM_HEADING_TEXT = "Edit Address"

    ERROR_ALERT_TEXT = "Oops, there is an error with information provided!"

    # Texts verified against the running store (the store says "Address", not "Address 1", and the postcode minimum is 2)
    FIELD_ERROR_MESSAGES = {
        "firstname": "First Name must be between 1 and 32 characters!",
        "lastname": "Last Name must be between 1 and 32 characters!",
        "address_1": "Address must be between 3 and 128 characters!",
        "city": "City must be between 3 and 128 characters!",
        "postcode": "Zip/postal code must be between 2 and 10 characters!",
        "zone_id": "Please select a region / state!",
    }

    REGION_PLACEHOLDER = "--- Please Select ---"

    # Changing the country triggers an AJAX call: GET index.php?rt=common/zone&zone_id=FALSE&country_id=<id>
    # which replaces the options of the Region / State select
    ZONE_REQUEST_PATTERN = "rt=common/zone"

    # Form fields: input name (id = AddressFrm_<name>); zone_id and country_id are selects
    FIELDS = (
        "firstname", "lastname", "company", "address_1", "address_2",
        "city", "zone_id", "postcode", "country_id",
    )
    REQUIRED_FIELDS = ("firstname", "lastname", "address_1", "city", "zone_id", "postcode", "country_id")

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

        # Breadcrumbs: Home > Account > Address Book > Edit Address (the last two are specific to address pages)
        self.breadcrumb_address_book_link = page.locator(
            "section.breadcrumbs ul.breadcrumb a[href$='rt=account/address']")
        self.breadcrumb_edit_address_link = page.locator("section.breadcrumbs ul.breadcrumb a[href*='address/update']")

        # Form
        self.form = page.locator("#AddressFrm")
        self.form_heading = page.locator("#AddressFrm h4.heading4")

        self.first_name_input = page.locator("#AddressFrm_firstname")
        self.last_name_input = page.locator("#AddressFrm_lastname")
        self.company_input = page.locator("#AddressFrm_company")
        self.address_1_input = page.locator("#AddressFrm_address_1")
        self.address_2_input = page.locator("#AddressFrm_address_2")
        self.city_input = page.locator("#AddressFrm_city")
        self.region_select = page.locator("#AddressFrm_zone_id")
        self.postcode_input = page.locator("#AddressFrm_postcode")
        self.country_select = page.locator("#AddressFrm_country_id")

        # Default address (radio buttons Yes / No)
        self.default_yes_radio = page.locator("#AddressFrm_default1")
        self.default_no_radio = page.locator("#AddressFrm_default0")

        # Buttons
        self.continue_button = page.locator("#AddressFrm button[type='submit']")
        self.back_button = page.locator("#AddressFrm a[title='Back']")
        self.error_alert = page.locator(".alert.alert-error, .alert.alert-danger")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------------
    # Dynamic locators
    # ----------------

    def field_input(self, field: str) -> Locator:
        return self.page.locator(f"#AddressFrm_{field}")

    def field_group(self, field: str) -> Locator:
        return self.page.locator("#AddressFrm .form-group", has=self.field_input(field))

    def field_error(self, field: str) -> Locator:
        return self.field_group(field).locator(".help-block")

    def field_required_marker(self, field: str) -> Locator:
        return self.field_group(field).locator(".input-group-addon .required")

    def selected_option(self, field: str) -> Locator:
        return self.field_input(field).locator("option:checked")

    # ------------------
    # Actions: main part
    # ------------------

    def fill_form(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            company: str | None = None,
            address_1: str | None = None,
            address_2: str | None = None,
            city: str | None = None,
            postcode: str | None = None,
            country: str | None = None,
            region: str | None = None,
            default: bool | None = None,
    ) -> None:
        # None = leave the field untouched, "" = clear the text field
        text_values = {
            "firstname": first_name,
            "lastname": last_name,
            "company": company,
            "address_1": address_1,
            "address_2": address_2,
            "city": city,
            "postcode": postcode,
        }
        for field, value in text_values.items():
            if value is not None:
                self.field_input(field).fill(value)

        # Country first, then region: changing the country reloads the region list
        if country is not None:
            self.select_country(country)
        if region is not None:
            self.select_region(region)

        if default is not None:
            (self.default_yes_radio if default else self.default_no_radio).check()

    def select_country(self, country: str) -> None:
        # Selecting the already selected country fires no change event, so there is no request to wait for
        if self.country_select.locator("option:checked").inner_text().strip() == country:
            return
        country_id = self.country_option(country).get_attribute("value")

        # Wait for the response that carries the new region list (matched by country_id, so a request still
        # in flight for the previously selected country can't satisfy the wait)
        with self.page.expect_response(
                lambda response: self.ZONE_REQUEST_PATTERN in response.url and f"country_id={country_id}" in response.url
        ):
            self.country_select.select_option(label=country)

    def country_option(self, country: str) -> Locator:
        return self.country_select.locator("option").filter(has_text=re.compile(rf"^\s*{re.escape(country)}\s*$"))

    def select_region(self, region: str) -> None:
        # Exact-text regex: has_text alone is a substring match ("Virginia" would also match "West Virginia")
        # and wait_for() fails on several matches. Waiting for the option also covers the case where the
        # country was not changed and the list is still being loaded after the page opened.
        option = self.region_select.locator("option").filter(has_text=re.compile(rf"^\s*{re.escape(region)}\s*$"))
        try:
            option.wait_for(state="attached", timeout=10_000)
        except PlaywrightTimeoutError:
            # Seen in ~1 of 35 runs: the region list for the already selected country never showed up.
            # Ask the store for it again once and leave a trace in the test report.
            warnings.warn(f"Region list did not contain '{region}' after 10 s - reloading it once", stacklevel=2)
            self.reload_regions()
            option.wait_for(state="attached")
        self.region_select.select_option(label=region)

    def reload_regions(self) -> None:
        country_id = self.country_select.input_value()
        with self.page.expect_response(
                lambda response: self.ZONE_REQUEST_PATTERN in response.url and f"country_id={country_id}" in response.url
        ):
            self.country_select.dispatch_event("change")

    def fill_field(self, field: str, value: str) -> None:
        self.field_input(field).fill(value)

    def clear_region(self) -> None:
        self.region_select.select_option(label=self.REGION_PLACEHOLDER)

    def click_continue(self) -> None:
        self.continue_button.click()

    def click_back(self) -> None:
        self.back_button.click()

    def edit_address(
            self,
            first_name: str | None = None,
            last_name: str | None = None,
            company: str | None = None,
            address_1: str | None = None,
            address_2: str | None = None,
            city: str | None = None,
            postcode: str | None = None,
            country: str | None = None,
            region: str | None = None,
            default: bool | None = None,
    ) -> None:
        self.fill_form(
            first_name, last_name, company, address_1, address_2,
            city, postcode, country, region, default,
        )
        self.click_continue()

    # --------
    # Readings
    # --------

    def field_value(self, field: str) -> str:
        return self.field_input(field).input_value()

    def field_error_text(self, field: str) -> str:
        return self.field_error(field).inner_text().strip()

    def selected_country_text(self) -> str:
        return self.selected_option("country_id").inner_text().strip()

    def selected_region_text(self) -> str:
        return self.selected_option("zone_id").inner_text().strip()

    def is_default_address(self) -> bool:
        return self.default_yes_radio.is_checked()

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
        expect(self.form_heading).to_have_text(self.FORM_HEADING_TEXT)

    def expect_loaded_for_edit(self) -> None:
        # The region list is (re)loaded asynchronously after the page opens. Submitting before that finishes
        # sends "--- Please Select ---" and the store rejects an address that was valid a moment ago.
        self.expect_loaded()
        expect(self.selected_option("zone_id")).not_to_have_text(self.REGION_PLACEHOLDER)

    def expect_field_value(self, field: str, value: str) -> None:
        expect(self.field_input(field)).to_have_value(value)

    def expect_selected_country(self, country: str) -> None:
        expect(self.selected_option("country_id")).to_have_text(country)

    def expect_selected_region(self, region: str) -> None:
        expect(self.selected_option("zone_id")).to_have_text(region)

    def expect_default_address(self, is_default: bool) -> None:
        if is_default:
            expect(self.default_yes_radio).to_be_checked()
        else:
            expect(self.default_no_radio).to_be_checked()

    def expect_required_fields(self) -> None:
        for field in self.REQUIRED_FIELDS:
            expect(self.field_required_marker(field)).to_be_visible()
        for field in set(self.FIELDS) - set(self.REQUIRED_FIELDS):
            expect(self.field_required_marker(field)).to_have_count(0)

    def expect_field_error(self, field: str, message: str) -> None:
        expect(self.field_error(field)).to_have_text(message)

    def expect_field_validation_error(self, field: str) -> None:
        self.expect_field_error(field, self.FIELD_ERROR_MESSAGES[field])

    def expect_error_alert(self) -> None:
        expect(self.error_alert).to_be_visible()
        expect(self.error_alert).to_contain_text(self.ERROR_ALERT_TEXT)

    def expect_no_field_errors(self) -> None:
        for field in self.FIELDS:
            expect(self.field_error(field)).to_have_text("")

    # endregion
    # ==========================================================================================================
