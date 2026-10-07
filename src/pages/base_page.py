from playwright.sync_api import Locator, Page, expect


class BasePage:
    """
    Common elements across store pages (verified on the home page and login page):
    header, search box, currency, mini-basket, category menu, and newsletter footer.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    CURRENCIES = ("USD", "EUR", "GBP")

    # Main categories: name ➤ path
    CATEGORIES = {
        "Apparel & accessories": "68",
        "Makeup": "36",
        "Skincare": "43",
        "Fragrance": "49",
        "Men": "58",
        "Hair Care": "52",
        "Books": "65",
    }
    # Subcategories: names are repeated, so the key is path
    SUBCATEGORIES = {
        "Shoes": "68_69", "T-shirts": "68_70",
        "Makeup > Cheeks": "36_40", "Makeup > Eyes": "36_39",
        "Makeup > Face": "36_38", "Makeup > Lips": "36_41",
        "Makeup > Nails": "36_42", "Makeup > Value Sets": "36_37",
        "Skincare > Eyes": "43_47", "Skincare > Face": "43_46",
        "Skincare > Gift Ideas & Sets": "43_45",
        "Skincare > Hands & Nails": "43_48", "Skincare > Sun": "43_44",
        "Fragrance > Men": "49_51", "Fragrance > Women": "49_50",
        "Men > Body & Shower": "58_63", "Men > Fragrance Sets": "58_59",
        "Men > Pre-Shave & Shaving": "58_61", "Men > Skincare": "58_60",
        "Hair Care > Conditioner": "52_54", "Hair Care > Shampoo": "52_53",
        "Books > Audio CD": "65_66", "Books > Paperback": "65_67",
    }

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region LOCATORS
    # ==========================================================================================================

    def __init__(self, page: Page):
        self.page = page

        # ---
        # TOP
        # ---

        # Header
        self.logo = page.locator("a.logo")
        self.login_or_register_link = page.locator("#customer_menu_top a")

        # Top menu (#main_menu_top appears once; the second menu is in #categorymenu)
        self.specials_link = page.locator("#main_menu_top a.menu_specials")
        self.account_link = page.locator("#main_menu_top a.menu_account")
        self.login_link = page.locator("#main_menu_top a.menu_login")
        self.check_order_link = page.locator("#main_menu_top a.menu_order")
        self.cart_link = page.locator("#main_menu_top li[data-id='menu_cart'] a")
        self.checkout_link = page.locator("#main_menu_top a.menu_checkout")

        # Search engine
        self.search_input = page.locator("#filter_keyword")
        self.search_button = page.locator(".button-in-search")
        self.search_category_selected = page.locator("#category_selected")
        self.search_category_options = page.locator(
            "#search-category a[id^='category_']:not(#category_selected)"
        )

        # Currency
        self.currency_toggle = page.locator("ul.language a.dropdown-toggle")
        self.currency_options = page.locator("ul.currency a")

        # Mini-basket
        self.cart_toggle = page.locator("ul.topcart a.dropdown-toggle")
        self.cart_count = page.locator("ul.topcart span.label-orange")
        self.cart_total = page.locator("ul.topcart span.cart_total")
        self.mini_cart_view_cart_button = page.locator("ul.topcart a[title='View Cart']")
        self.mini_cart_checkout_button = page.locator("ul.topcart a[title='Checkout']")
        self.mini_cart_empty_info = page.locator("#top_cart_product_list .empty_cart")

        # ---
        # MID
        # ---

        # Category menu
        self.category_menu = page.locator("#categorymenu")
        self.home_link = page.locator("#categorymenu a.menu_home")
        self.top_categories = page.locator(
            "#categorymenu ul.categorymenu > li > a:not(.menu_home)"
        )

        # ------
        # BOTTOM
        # ------

        # Footer
        self.footer = page.locator("footer")
        self.about_us_block = page.locator("footer .footersocial h2", has_text="About Us")
        self.contact_us_block = page.locator("footer .footersocial h2", has_text="Contact Us")
        self.testimonials_block = page.locator("footer .footersocial h2", has_text="Testimonials")
        self.testimonials = page.locator("#testimonialsidebar li:not(.clone)")
        self.newsletter_section = page.locator("#newslettersignup")
        self.newsletter_email_input = page.locator("#subscribeFrm input[name='email']")
        self.newsletter_submit_button = page.locator("#subscribeFrm button[type='submit']")
        self.footer_about_us_link = page.locator(".footerlinks a[href*='content_id=1']")
        self.footer_privacy_policy_link = page.locator(".footerlinks a[href*='content_id=2']")
        self.footer_return_policy_link = page.locator(".footerlinks a[href*='content_id=3']")
        self.footer_shipping_link = page.locator(".footerlinks a[href*='content_id=4']")
        self.footer_contact_us_link = page.locator(".footerlinks a[href*='content/contact']")
        self.footer_site_map_link = page.locator(".footerlinks a[href*='content/sitemap']")
        self.footer_login_link = page.locator(".footerlinks a[href*='account/login']")
        self.facebook_link = page.locator("footer a.facebook")
        self.twitter_link = page.locator("footer a.twitter")
        self.linkedin_link = page.locator("footer a.linkedin")
        self.back_to_top_link = page.locator("#gotop")

        # Message modal
        self.message_modal = page.locator("#msgModal")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------
    # Navigation
    # ----------

    def goto(self, path: str = "/"):
        self.page.goto(path)

    def title(self) -> str:
        return self.page.title()

    # ----------------
    # Dynamic locators
    # ----------------

    def currency_option(self, code: str) -> Locator:
        return self.page.locator(f"ul.currency a[href*='currency={code}']")

    def category_link(self, name: str) -> Locator:
        path = self.CATEGORIES[name]
        return self.page.locator(f"#categorymenu a[href$='path={path}']")

    def subcategory_link(self, name: str) -> Locator:
        path = self.SUBCATEGORIES[name]
        return self.page.locator(f"#categorymenu .subcategories a[href$='path={path}']")

    def search_category_option(self, name: str) -> Locator:
        return self.page.locator(
            "#search-category a[id^='category_']:not(#category_selected)",
            has_text=name,
        )

    # ---------------
    # Actions: Header
    # ---------------

    def click_logo(self) -> None:
        self.logo.click()

    def click_login_or_register(self) -> None:
        self.login_or_register_link.click()

    def click_specials(self) -> None:
        self.specials_link.click()

    def click_account(self) -> None:
        self.account_link.click()

    def click_login_from_account_menu(self) -> None:
        self.account_link.hover()
        self.login_link.click()

    def click_check_your_order(self) -> None:
        self.account_link.hover()
        self.check_order_link.click()

    def click_cart(self) -> None:
        self.cart_link.click()

    def click_checkout(self) -> None:
        self.checkout_link.click()

    # ---------------------------------------------
    # Actions: search engine, currency, mini-basket
    # ---------------------------------------------

    def search(self, phrase: str, category: str | None = None) -> None:
        self.search_input.click()  # focus otwiera listę kategorii
        if category:
            self.search_category_option(category).click()
        self.search_input.fill(phrase)
        self.search_button.click()

    def search_with_enter(self, phrase: str) -> None:
        self.search_input.fill(phrase)
        self.search_input.press("Enter")

    def change_currency(self, code: str) -> None:
        self.currency_toggle.hover()
        self.currency_option(code).click()

    def open_mini_cart(self) -> None:
        self.cart_toggle.hover()

    def open_cart_from_mini_cart(self) -> None:
        self.open_mini_cart()
        self.mini_cart_view_cart_button.click()

    def open_checkout_from_mini_cart(self) -> None:
        self.open_mini_cart()
        self.mini_cart_checkout_button.click()

    # -------------------
    # Actions: Categories
    # -------------------

    def click_home(self) -> None:
        self.home_link.click()

    def open_category(self, name: str) -> None:
        self.category_link(name).click()

    def open_subcategory(self, name: str) -> None:
        parent = next(
            cat for cat, pid in self.CATEGORIES.items()
            if self.SUBCATEGORIES[name].startswith(pid + "_")
        )
        self.category_link(parent).hover()  # podkategorie rozwijają się na hover
        self.subcategory_link(name).click()

    # ---------------
    # Actions: footer
    # ---------------

    def scroll_to_footer(self) -> None:
        self.footer.scroll_into_view_if_needed()

    def click_back_to_top(self) -> None:
        self.back_to_top_link.click()

    def subscribe_to_newsletter(self, email: str) -> None:
        self.newsletter_email_input.fill(email)
        self.newsletter_submit_button.click()

    # --------
    # Readings
    # --------

    def cart_items_count(self) -> int:
        return int(self.cart_count.inner_text().strip())

    def cart_total_text(self) -> str:
        return self.cart_total.inner_text().strip()

    def selected_currency_text(self) -> str:
        return self.currency_toggle.inner_text().strip()

    def top_category_names(self) -> list[str]:
        return [t.strip() for t in self.top_categories.all_inner_texts()]

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_cart_count(self, count: int) -> None:
        expect(self.cart_count).to_have_text(str(count))

    def expect_currency(self, symbol: str) -> None:
        expect(self.currency_toggle).to_contain_text(symbol)

    # endregion
    # ==========================================================================================================
