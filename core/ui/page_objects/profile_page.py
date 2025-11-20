import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from .locators.profile_page_locators import ProfilePageLocators as Loc

class ProfilePage(BasePage):


    def is_isbn_visible(self, isbn: str) -> bool:
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{isbn}')]"))
            )
            return True
        except Exception:
            return False

    @allure.step("Get text label for not logged user")
    def not_logged_label_text(self)->str:
        return self.get_text(Loc.NOT_LOGIN_LABEL)
