import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def build_chrome():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    chrome_path = os.getenv("CHROME_PATH")
    if chrome_path:
        options.binary_location = chrome_path
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1600, 1000)
    return driver

@pytest.fixture(scope="function")
def driver():
    d = build_chrome()
    yield d
    d.quit()

@pytest.fixture(scope="module")
def driver_mod():
    d = build_chrome()
    yield d
    d.quit()

@pytest.fixture(scope="session")
def driver_session():
    d = build_chrome()
    yield d
    d.quit()
