from selenium.webdriver.common.by import By


class BooksPageLocators:
    TITLES_SELECTOR = (By.CSS_SELECTOR, "#app .rt-tbody .action-buttons a")
    SEARCH = (By.ID, "searchBox")
    ROWS_SELECT = (By.CSS_SELECTOR, "#app select")
    NEXT_PAGE_BTN = (By.CSS_SELECTOR, "div.-next button")
    PREV_PAGE_BTN = (By.CSS_SELECTOR, "div.-previous button")
    THIS_PAGE_NUM = (By.CSS_SELECTOR, "div.-pageJump input")
    TOTAL_PAGE_NUM = (By.CSS_SELECTOR, ".-totalPages")
    PAGE_LABEL = (By.XPATH, "//span[contains(., 'Page') and contains(., 'of')]")
    ROWS = (By.CSS_SELECTOR, "div.rt-tr-group")
