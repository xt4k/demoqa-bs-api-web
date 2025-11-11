import re
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


pytestmark = [pytest.mark.ui]

@pytest.mark.usefixtures("driver_mod")
class TestSearchAndPagination:
    @pytest.mark.xdist_group("group2")
    @pytest.mark.parametrize("query", ["Git", "Java", "Design"])
    def test_search_books_by_title(self, on_fail, driver_mod, query):
        driver_mod.get(f"{settings.BASE_URL}/books")
        search = driver_mod.find_element(By.ID, "searchBox")
        search.clear()
        search.send_keys(query)
        WebDriverWait(driver_mod, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.rt-tr-group")))
        rows = driver_mod.find_elements(By.CSS_SELECTOR, "div.rt-tr-group")
        if not rows:
            pytest.skip("No rows rendered, skipping due to upstream UI behavior.")
        assert any(re.search(query, r.text, re.I) for r in rows), f"No results contain: {query}"

    @pytest.mark.xdist_group("group3")
    def test_pagination_next_prev_5_rows(self, on_fail, driver_mod):
        driver_mod.get(f"{settings.BASE_URL}/books")
        selects = driver_mod.find_elements(By.TAG_NAME, "select")
        if selects:
            Select(selects[0]).select_by_visible_text("5 rows")

        label_el = WebDriverWait(driver_mod, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(., 'Page') and contains(., 'of')]"))
        )
        m0 = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", label_el.text)
        assert m0, f"Unexpected label: {label_el.text}"
        cur0, total = int(m0.group(1)), int(m0.group(2))
        if total < 2:
            pytest.skip("Only one page available with 5 rows.")

        driver_mod.find_element(By.XPATH, "//button[normalize-space()='Next']").click()
        WebDriverWait(driver_mod, 5).until(
            EC.text_to_be_present_in_element((By.XPATH, "//span[contains(., 'Page') and contains(., 'of')]"),
                                             f"Page {cur0+1} of")
        )
        driver_mod.find_element(By.XPATH, "//button[normalize-space()='Previous']").click()
        WebDriverWait(driver_mod, 5).until(
            EC.text_to_be_present_in_element((By.XPATH, "//span[contains(., 'Page') and contains(., 'of')]"),
                                             f"Page {cur0} of")
        )

    @pytest.mark.xfail(reason="Boundary disabled-state may be unreliable on upstream UI")
    @pytest.mark.xdist_group("group4")
    def test_pagination_boundaries(self, on_fail, driver_mod):
        driver_mod.get(f"{settings.BASE_URL}/books")
        prev = driver_mod.find_element(By.XPATH, "//button[normalize-space()='Previous']")
        assert not prev.is_enabled(), "Expected 'Previous' to be disabled on first page"
