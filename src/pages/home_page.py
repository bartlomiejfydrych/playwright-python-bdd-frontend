from playwright.sync_api import Locator, Page, expect

from src.pages.base_page import BasePage


class HomePage(BasePage):
    """Strona główna https://automationteststore.com/ (AbanteCart).

    Zawiera tylko to, co specyficzne dla strony głównej. Nagłówek,
    wyszukiwarka, waluta, mini-koszyk, menu kategorii i stopka są w BasePage.
    """

    PATH = "/"
    TITLE = "A place to practice your automation skills!"

    # klucz -> selektor sekcji produktowej na stronie głównej
    SECTIONS = {
        "featured": "#featured",
        "latest": "#latest",
        "bestsellers": "#bestseller",
        "specials": "#special",
    }
    BRANDS = {
        "Benefit": 12, "Pantene": 17, "M·A·C": 11, "Lancôme": 15,
        "Gucci": 20, "Giorgio Armani": 19, "Dove": 18,
        "Calvin Klein": 13, "Bvlgari": 14, "Sephora": 16,
    }

    def __init__(self, page: Page):
        super().__init__(page)

        # --- Baner i sekcje informacyjne ---
        self.banner = page.locator("#banner_slides")
        self.promo_blocks = page.locator("section.promo_section .promo_block")
        self.welcome_message = page.locator("section.contentpanel .welcome_msg")

        # --- Produkty (wszystkie sekcje) ---
        self.product_tiles = page.locator(".thumbnails > div")
        self.product_names = page.locator("a.prdocutname")

        # --- Marki ---
        self.brands_section = page.locator("#popularbrands")
        self.brand_links = page.locator("#brandcarousal a[href*='manufacturer_id=']")
        self.brands_prev = page.locator("#prev")
        self.brands_next = page.locator("#next")

    # ------------------------------------------------------------------ #
    # Lokatory dynamiczne
    # ------------------------------------------------------------------ #
    def section(self, key: str) -> Locator:
        return self.page.locator(self.SECTIONS[key])

    def section_heading(self, key: str) -> Locator:
        return self.section(key).locator("h1.heading1 .maintext")

    def section_tiles(self, key: str) -> Locator:
        return self.section(key).locator(".thumbnails > div")

    def product_tile(self, key: str, product_name: str) -> Locator:
        # nazwa produktu jest POZA .thumbnail, ale wewnątrz kolumny kafelka
        return self.section_tiles(key).filter(
            has=self.page.locator("a.prdocutname", has_text=product_name)
        ).first

    def product_name_link(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator("a.prdocutname")

    def product_image_link(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator(".thumbnail > a").first

    def product_view_link(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator("a.details")

    def product_review_link(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator("a.compare")

    def product_add_to_cart_button(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator("a.productcart")

    def product_price(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator(".oneprice, .pricenew")

    def product_old_price(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator(".priceold")

    def product_sale_badge(self, key: str, product_name: str) -> Locator:
        return self.product_tile(key, product_name).locator("span.sale")

    def brand_link(self, brand_name: str) -> Locator:
        return self.page.locator(f"#brandcarousal a:has(img[alt='{brand_name}'])").first

    # ------------------------------------------------------------------ #
    # Akcje
    # ------------------------------------------------------------------ #
    def open(self) -> "HomePage":
        self.goto(self.PATH)
        return self

    def open_product(self, key: str, product_name: str) -> None:
        self.product_name_link(key, product_name).click()

    def open_product_via_image(self, key: str, product_name: str) -> None:
        self.product_image_link(key, product_name).click()

    def open_product_view(self, key: str, product_name: str) -> None:
        self.product_tile(key, product_name).hover()  # linki pojawiają się na hover
        self.product_view_link(key, product_name).click()

    def open_product_review(self, key: str, product_name: str) -> None:
        self.product_tile(key, product_name).hover()
        self.product_review_link(key, product_name).click()

    def add_product_to_cart(self, key: str, product_name: str) -> None:
        """Dodaje produkt z listy.

        Produkty bez opcji dodają się AJAX-em (href='#'). Produkty z opcjami
        (np. Tropiques Minerale Loose Bronzer, sandały) mają w przycisku link
        do karty produktu, więc ta metoda przeniesie na stronę produktu.
        """
        self.product_tile(key, product_name).hover()
        self.product_add_to_cart_button(key, product_name).click()

    def product_adds_via_ajax(self, key: str, product_name: str) -> bool:
        href = self.product_add_to_cart_button(key, product_name).get_attribute("href")
        return href is not None and href.rstrip("/").endswith("#")

    def open_brand(self, brand_name: str) -> None:
        self.brand_link(brand_name).click()

    # ------------------------------------------------------------------ #
    # Odczyty
    # ------------------------------------------------------------------ #
    def product_names_in(self, key: str) -> list[str]:
        return [
            t.strip()
            for t in self.section(key).locator("a.prdocutname").all_inner_texts()
        ]

    def promo_titles(self) -> list[str]:
        return [t.strip() for t in self.promo_blocks.locator("h2").all_inner_texts()]

    def brand_names(self) -> list[str]:
        return [
            self.brand_links.nth(i).locator("img").get_attribute("alt") or ""
            for i in range(self.brand_links.count())
        ]

    # ------------------------------------------------------------------ #
    # Asercje pomocnicze
    # ------------------------------------------------------------------ #
    def expect_loaded(self) -> None:
        expect(self.page).to_have_title(self.TITLE)
        expect(self.logo).to_be_visible()

    def expect_sections_visible(self) -> None:
        for key in self.SECTIONS:
            expect(self.section_heading(key)).to_be_visible()
            expect(self.section_tiles(key)).to_have_count(4)
