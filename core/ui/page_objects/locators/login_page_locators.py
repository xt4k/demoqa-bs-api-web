from selenium.webdriver.common.by import By

class LoginPageLocators:
    USERNAME = (By.ID, "userName")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login")
    ERROR_MSG = (By.ID, "name")
