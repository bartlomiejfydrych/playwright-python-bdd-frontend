from src.pages.base_page import BasePage


class HomePage(BasePage):
    def open(self):
        self.goto("/")
