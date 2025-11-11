from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple

class BasePage:
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip('/')

    def open(self, path: str) -> None:
        self.driver.get(f"{self.base_url}/{path.lstrip('/')}")

    def find(self, locator: Tuple[str, str]):
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))

    def click(self, locator: Tuple[str, str]):
        self.find(locator).click()

    def type(self, locator: Tuple[str, str], text: str, clear: bool = True):
        el = self.find(locator)
        if clear:
            el.clear()
        el.send_keys(text)

    def wait_url_contains(self, fragment: str, timeout: int = 10):
        WebDriverWait(self.driver, timeout).until(EC.url_contains(fragment))
