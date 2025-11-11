from reporting.html_report_ext import process_report, customize_header, customize_row
import pytest

def pytest_html_report_title(report):
    report.title = "DemoQA Book Store — UI/API/E2E Tests"

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    process_report(rep, item, call)

def pytest_html_results_table_header(cells):
    customize_header(cells)

def pytest_html_results_table_row(report, cells):
    customize_row(report, cells)
