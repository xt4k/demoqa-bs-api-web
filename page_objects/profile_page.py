from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class ProfilePage(BasePage):
    LOGOUT_BTN = (By.ID, "submit")

    def is_isbn_visible(self, isbn: str) -> bool:
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{isbn}')]"))
            )
            return True
        except Exception:
            return False

    def logout(self):
        self.click(self.LOGOUT_BTN)
