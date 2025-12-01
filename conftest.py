# conftest.py
from __future__ import annotations

import contextlib
from typing import Generator, Any, Dict

import allure
import pytest

from core.api.services.account_service import AccountService
from core.api.services.book_store_service import BookStoreService
from core.config.config import RunCfg
from core.util.allure_hooks.allure import AllureApiLogger
from core.http.http_client import HttpClient
from core.providers.data_generator import generate_user_request_dict
from core.util.html_report.html_report_decorator import html_step

from core.util.html_report.html_report_helper import process_report, customize_header, customize_row
from core.util.logging import Logger
from core.util.support.demoqa_flows import ensure_test_user, cleanup_demo_user

log = Logger.get_logger("conftest", prefix="project_root")


@pytest.fixture(scope="session")
def env_info(http_root: HttpClient) -> RunCfg:
    """Environment info string, reusable in tests."""
    return http_root.cfg


@pytest.fixture(scope="session")
def http_root() -> Generator[HttpClient, None, None]:
    """Single shared HttpClient + install Allure response-hook."""
    http = HttpClient(is_auth=False)
    AllureApiLogger().install(http.s)

    cfg = http.cfg
    env_info = (
        f"ENV={cfg.env_name}\n"
        f"API_BASE={cfg.api_uri}\n"
        f"WEB_BASE={cfg.web_url}\n"
        f"TEST_USER={cfg.api_user_name}\n"
        f"USER_ID={cfg.api_user_id or ''}\n"
    )
    allure.attach(env_info, name="Environment", attachment_type=allure.attachment_type.TEXT)
    log.info(f"ENV loaded: env={cfg.env_name} api={cfg.api_uri} user={cfg.api_user_name}")
    try:
        yield http
    finally:
        http.close()
        log.info("HttpClient session closed")


@pytest.fixture(scope="session")
@html_step("Provide AccountService client")
@allure.step("Provide AccountService client")
def account_service(http_root: HttpClient) -> AccountService:
    """Thin wrapper over HttpClient, uses shared Session."""
    log.info("AccountService uses shared HttpClient session")
    return AccountService(is_auth=False, session=http_root.s)


@pytest.fixture(scope="session")
@html_step("Provide BookStoreService client")
@allure.step("Provide BookStoreService client")
def book_store_service(http_root: HttpClient) -> BookStoreService:
    """Thin wrapper over HttpClient, uses shared Session."""
    log.info("BookStoreService uses shared HttpClient session")
    return BookStoreService(is_auth=False, session=http_root.s)


@pytest.fixture(scope="session")
def api_auth_user(
        request: pytest.FixtureRequest,
        account_service: AccountService,
        book_store_service: BookStoreService,
) -> Generator[dict[str, Any], Any, None]:
    """
    Provide authenticated DemoQA user for all tests:

    - if DEMOQA_USER/DEMOQA_PASS are set -> reuse them, no cleanup
    - otherwise create temporary user and optionally clean it up
      at the end of the session (if --cleanup-user is passed)
    """
    user, needs_cleanup = ensure_test_user(account_service)
    yield user

    if needs_cleanup and request.config.getoption("--cleanup-user", default=False):
        cleanup_demo_user(account_service, book_store_service, user)


@pytest.fixture()
def user_id(account_service: AccountService) -> Generator[Any, Any, None]:
    """
    Create a fresh DemoQA user for BookStore tests and clean it up afterwards.
    """
    # Arrange: create user with random valid credentials
    create_user_dict = generate_user_request_dict()
    response = account_service.create_user_request(create_user_dict)
    body = response.json()

    uid = body["userID"]

    yield uid

    # Teardown: best-effort delete user, ignore errors if already removed
    with contextlib.suppress(Exception):
        account_service.delete_user(uid)


@pytest.fixture(scope="function")
def ui_login_via_api(
        driver,
        env_info: RunCfg,
        api_auth_user: Dict[str, Any],
):
    """
    Log in UI by injecting localStorage from API login.
    """
    driver.get(env_info.web_url)

    script = """
        window.localStorage.setItem('userID', arguments[0]);
        window.localStorage.setItem('userName', arguments[1]);
        window.localStorage.setItem('token', arguments[2]);
        window.localStorage.setItem('expires', arguments[3]);
    """
    driver.execute_script(
        script,
        api_auth_user["userId"],
        api_auth_user["username"],
        api_auth_user["token"],
        api_auth_user["expires"],
    )

    yield api_auth_user

    with contextlib.suppress(Exception):
        driver.execute_script("window.localStorage.clear();")


def pytest_html_report_title(report):
    report.title = "DemoQA Book Store — UI/API/E2E Tests"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to customize test reports to include additional details like screenshots and custom titles.
    Delegates the processing to the utility module.
    """
    outcome = yield
    report = outcome.get_result()
    process_report(report, item, call)


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells):
    """Customize the HTML report header."""
    customize_header(cells)


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report, cells):
    """Customize the HTML report rows."""
    customize_row(report, cells)

@pytest.fixture(autouse=True)
def _html_steps_request_context(request: pytest.FixtureRequest):
    """
    Make current pytest request available for html_step decorator.
    """
    pytest.current_request = request
    try:
        yield
    finally:
        pytest.current_request = None