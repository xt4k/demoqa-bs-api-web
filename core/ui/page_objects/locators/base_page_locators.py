from selenium.webdriver.common.by import By


class BasePageLocators:
    """Common base page with shared Selenium actions and waits."""
    LOGGED_USER_NAME = (By.ID, "userName-value")
    LOG_OUT_BTN = (By.ID, "submit")
