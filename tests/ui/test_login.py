import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api_client import settings

pytestmark = [pytest.mark.ui, pytest.mark.xdist_group("group1")]

def test_login_success(on_fail, driver, test_user, cfg):
    driver.get(f"{settings.BASE_URL}/login")
    username = (cfg.login or settings.STATIC_LOGIN) or test_user["user_name"]
    password = (cfg.password or settings.STATIC_PASSWORD) or test_user["password"]
    driver.find_element(By.ID, "userName").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/profile"))
