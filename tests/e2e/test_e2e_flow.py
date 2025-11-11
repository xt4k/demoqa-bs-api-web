import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api_service.book_store_service import BookStoreService as bss

pytestmark = pytest.mark.e2e

@pytest.mark.usefixtures("driver_session")
class TestE2EFlows:
    def test_api_to_ui_collection_visibility(self, on_fail, driver_session, test_user):
        books = bss.list_books().json()["books"]
        isbn = books[0]["isbn"]
        add = bss.add_books(test_user["user_id"], [isbn], test_user["token"])
        assert add.status_code in (200, 201)

        driver_session.get(f"{settings.BASE_URL}/login")
        driver_session.find_element(By.ID, "userName").send_keys(test_user["user_name"])
        driver_session.find_element(By.ID, "password").send_keys(test_user["password"])
        driver_session.find_element(By.ID, "login").click()
        WebDriverWait(driver_session, 10).until(EC.url_contains("/profile"))
        WebDriverWait(driver_session, 5).until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{isbn}')]")))
