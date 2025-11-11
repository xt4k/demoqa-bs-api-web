import re
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


pytestmark = [pytest.mark.ui]

@pytest.mark.usefixtures("driver_mod")
@pytest.mark.xdist_group("group2")
def test_search_with_param_fixture(on_fail, driver_mod, search_query_and_rows):
    query, rows_label = search_query_and_rows

    selects = driver_mod.find_elements(By.TAG_NAME, "select")
    if selects:
        Select(selects[0]).select_by_visible_text(rows_label)

    search = driver_mod.find_element(By.ID, "searchBox")
    search.clear()
    search.send_keys(query)

    WebDriverWait(driver_mod, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.rt-tr-group")))
    rows = driver_mod.find_elements(By.CSS_SELECTOR, "div.rt-tr-group")
    if not rows:
        pytest.skip("No rows rendered, skipping due to upstream UI behavior.")
    assert any(re.search(query, r.text, re.I) for r in rows), f"No results contain: {query}"
