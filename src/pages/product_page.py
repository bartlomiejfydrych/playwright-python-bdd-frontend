import re

from playwright.sync_api import Locator, Page, expect

from base_page import BasePage


class ProductPage(BasePage):
    """
    Single product page (verified on: Skinsheen Bronzer Stick, product_id=50, and
    Absolue Eye Precious Cells, product_id=65, which is on sale):
    breadcrumbs, product details (name, price, quantity, add to cart),
    tabs (description, reviews, tags) and the "Latest Products" side list.
    """

    # ==========================================================================================================
    # region VARIABLES
    # ==========================================================================================================

    PATH = "/index.php?rt=product/product&product_id={product_id}"

    # Tabs: name ➤ fragment in href
    TABS = {
        "Description": "#description",
        "Reviews": "#review",
        "Tags": "#producttag",
    }

    RATINGS = (1, 2, 3, 4, 5)

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region LOCATORS
    # ==========================================================================================================

    def __init__(self, page: Page):
        super().__init__(page)

        # -----------
        # BREADCRUMBS
        # -----------

        self.breadcrumbs = page.locator("section.breadcrumbs ul.breadcrumb li a")

        # ---------------
        # LEFT: side list
        # ---------------

        # "Latest Products" (the same <a.productname> class is used in the main product name, so scope it)
        self.latest_products = page.locator(".sidewidt ul.side_prd_list li")
        self.latest_product_links = page.locator(".sidewidt ul.side_prd_list a.productname")

        # ---------------
        # DETAILS: images
        # ---------------

        # Desktop image (the mobile one is duplicated in a second .bigimage block)
        self.main_image = page.locator("#product_details .bigimage.easyzoom img")
        self.main_image_link = page.locator("#product_details .bigimage.easyzoom a.local_image")
        # Thumbnails appear only for products with more than one image (e.g. product_id=65)
        self.thumbnails = page.locator("#product_details ul.smallimage .producthtumb a")

        # ---------------
        # DETAILS: buying
        # ---------------

        self.product_name = page.locator("#product_details h1.productname")
        # Current price; for products on sale the old (crossed-out) price is shown next to it
        self.price = page.locator("#product_details .productfilneprice")
        self.old_price = page.locator("#product_details .productpageoldprice")
        self.quantity_input = page.locator("#product_quantity")
        self.total_price = page.locator("#product .total-price")
        self.product_id_input = page.locator("#product_product_id")
        self.add_to_cart_button = page.locator("#product ul.productpagecart a.cart")
        self.print_button = page.locator("#product a.productprint")
        # Product options (selects/radios/checkboxes) - not present on this product, selector taken from the page's JS
        self.option_fields = page.locator("#product select[name^='option'], #product input[name^='option']")

        # ----
        # TABS
        # ----

        self.tab_description = page.locator("#myTab a[href$='#description']")
        self.tab_reviews = page.locator("#myTab a[href$='#review']")
        self.tab_tags = page.locator("#myTab a[href$='#producttag']")

        # Tab: Description
        self.description_pane = page.locator("#description")
        self.description_text = page.locator("#description > p")
        self.model_info = page.locator("#description ul.productinfo li", has_text="Model:")
        self.manufacturer_link = page.locator("#description ul.productinfo a[href*='manufacturer_id']")
        self.manufacturer_logo = page.locator("#description ul.productinfo a[href*='manufacturer_id'] img")

        # Tab: Reviews
        self.review_pane = page.locator("#review")
        self.current_reviews = page.locator("#current_reviews")
        self.no_reviews_info = page.locator("#current_reviews .content")
        self.review_name_input = page.locator("#review input#name")
        self.review_text_input = page.locator("#review textarea#text")
        self.review_captcha_image = page.locator("#captcha_img")
        self.review_captcha_input = page.locator("#captcha")
        self.review_submit_button = page.locator("#review_submit")
        self.review_alert_success = page.locator("#review .alert-success")
        self.review_alert_error = page.locator("#review .alert-danger")

        # Tab: Tags
        self.tags_pane = page.locator("#producttag")
        self.tags = page.locator("#producttag ul.tags a")

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region METHODS
    # ==========================================================================================================

    # ----------
    # Navigation
    # ----------

    def goto_product(self, product_id: int | str) -> None:
        self.goto(self.PATH.format(product_id=product_id))

    # ----------------
    # Dynamic locators
    # ----------------

    def tab_link(self, name: str) -> Locator:
        fragment = self.TABS[name]
        return self.page.locator(f"#myTab a[href$='{fragment}']")

    def breadcrumb(self, name: str) -> Locator:
        return self.breadcrumbs.filter(has_text=name)

    def tag_link(self, name: str) -> Locator:
        return self.tags.filter(has_text=name)

    def latest_product_link(self, name: str) -> Locator:
        return self.latest_product_links.filter(has_text=name)

    def rating_star(self, rating: int) -> Locator:
        # Note: id="ratingN" is duplicated (div + input), so we target the title
        return self.page.locator(f"#review .star-rating a[title='{rating}']")

    # ---------------------
    # Actions: product form
    # ---------------------

    def set_quantity(self, quantity: int) -> None:
        # Total Price is recalculated on the keyup event, and fill() does not call it - hence press_sequentially
        self.quantity_input.clear()
        self.quantity_input.press_sequentially(str(quantity))

    def add_to_cart(self, quantity: int | None = None) -> None:
        if quantity is not None:
            self.set_quantity(quantity)
        self.add_to_cart_button.click()

    def click_print(self) -> None:
        self.print_button.click()

    # ---------------
    # Actions: header
    # ---------------

    def click_breadcrumb(self, name: str) -> None:
        self.breadcrumb(name).click()

    def click_manufacturer(self) -> None:
        self.manufacturer_link.click()

    def click_latest_product(self, name: str) -> None:
        self.latest_product_link(name).click()

    # -------------
    # Actions: tabs
    # -------------

    def open_tab(self, name: str) -> None:
        self.tab_link(name).click()

    def open_description_tab(self) -> None:
        self.tab_description.click()

    def open_reviews_tab(self) -> None:
        self.tab_reviews.click()

    def open_tags_tab(self) -> None:
        self.tab_tags.click()

    def click_tag(self, name: str) -> None:
        self.open_tags_tab()
        self.tag_link(name).click()

    # ----------------
    # Actions: reviews
    # ----------------

    def select_rating(self, rating: int) -> None:
        self.rating_star(rating).click()

    def write_review(self, name: str, text: str, rating: int | None = None, captcha: str = "") -> None:
        self.open_reviews_tab()
        if rating is not None:
            self.select_rating(rating)
        self.review_name_input.fill(name)
        self.review_text_input.fill(text)
        self.review_captcha_input.fill(captcha)

    def submit_review(self) -> None:
        self.review_submit_button.click()

    # --------
    # Readings
    # --------

    def product_name_text(self) -> str:
        return self.product_name.inner_text().strip()

    def price_text(self) -> str:
        return self.price.inner_text().strip()

    def old_price_text(self) -> str:
        return self.old_price.inner_text().strip()

    def is_on_sale(self) -> bool:
        return self.old_price.count() > 0

    def total_price_text(self) -> str:
        return self.total_price.inner_text().strip()

    def quantity_value(self) -> int:
        return int(self.quantity_input.input_value())

    def product_id(self) -> str:
        return self.product_id_input.input_value()

    def description(self) -> str:
        return self.description_text.inner_text().strip()

    def model_text(self) -> str:
        # Tekst li to "Model: 558003" - odcinamy etykietę
        return self.model_info.inner_text().replace("Model:", "").strip()

    def manufacturer_name(self) -> str:
        return self.manufacturer_logo.get_attribute("title") or ""

    def breadcrumb_names(self) -> list[str]:
        return [t.strip() for t in self.breadcrumbs.all_inner_texts()]

    def tag_names(self) -> list[str]:
        return [t.strip() for t in self.tags.all_inner_texts()]

    def latest_product_names(self) -> list[str]:
        return [t.strip() for t in self.latest_product_links.all_inner_texts()]

    def reviews_count(self) -> int:
        # Etykieta zakładki: "Reviews (0)"
        return int(re.search(r"\((\d+)\)", self.tab_reviews.inner_text()).group(1))

    # endregion
    # ==========================================================================================================

    # ==========================================================================================================
    # region ASSERTIONS
    # ==========================================================================================================

    # -----------------
    # Helper assertions
    # -----------------

    def expect_product_name(self, name: str) -> None:
        expect(self.product_name).to_have_text(name)

    def expect_price(self, price: str) -> None:
        expect(self.price).to_have_text(price)

    def expect_old_price(self, price: str) -> None:
        expect(self.old_price).to_have_text(price)

    def expect_on_sale(self) -> None:
        expect(self.old_price).to_be_visible()

    def expect_not_on_sale(self) -> None:
        expect(self.old_price).to_have_count(0)

    def expect_total_price(self, price: str) -> None:
        expect(self.total_price).to_have_text(price)

    def expect_quantity(self, quantity: int) -> None:
        expect(self.quantity_input).to_have_value(str(quantity))

    def expect_model(self, model: str) -> None:
        expect(self.model_info).to_contain_text(model)

    def expect_tabs_visible(self) -> None:
        for name in self.TABS:
            expect(self.tab_link(name)).to_be_visible()

    def expect_no_reviews(self) -> None:
        expect(self.no_reviews_info).to_have_text("There are no reviews for this product.")

    def expect_review_error(self, message: str | None = None) -> None:
        expect(self.review_alert_error).to_be_visible()
        if message:
            expect(self.review_alert_error).to_contain_text(message)

    def expect_review_success(self, message: str | None = None) -> None:
        expect(self.review_alert_success).to_be_visible()
        if message:
            expect(self.review_alert_success).to_contain_text(message)

    # endregion
    # ==========================================================================================================
