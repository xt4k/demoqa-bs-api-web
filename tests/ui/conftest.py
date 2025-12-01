# All code/comments in English
import contextlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from core.config.config import ConfigLoader, RunCfg


# =============================== CLI options =================================
def pytest_addoption(parser):
    # browsers / display
    parser.addoption("--browser", action="store", default="chrome", help="chrome|firefox|edge")
    parser.addoption("--headless", action="store_true", default=False, help="Run headless")
    parser.addoption("--window-size", action="store", default="1920,1080", help="WxH window size (default 1920,1080)")
    parser.addoption("--lang", action="store", default="en-US", help="Accept-Language/locale")
    parser.addoption("--incognito", action="store_true", default=False, help="Incognito/Private mode")
    # grid / base url / waits
    parser.addoption("--base-url", action="store", default="https://demoqa.com", help="Base URL")
    parser.addoption("--iwait", action="store", type=int, default=2, help="Implicit wait seconds")
    # HAR / cleanup
    parser.addoption("--har", action="store_true", default=False, help="Record HAR via CDP (Chrome/Edge)")
    parser.addoption("--cleanup-user", action="store_true", default=False, help="Delete temp user after session")


# =============================== Logging =====================================
def _make_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger("TEST")


LOGGER = _make_logger()


@pytest.fixture(scope="function", autouse=True)
def _test_log():
    LOGGER.info("=== test start ===")
    yield
    LOGGER.info("=== test end ===")


# ============================== Driver builders ==============================
def _chrome(cfg):
    opts = ChromeOptions()
    # console + performance logs (for HAR)
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})
    opts.add_argument(f"--lang={cfg['lang']}")
    if cfg["incognito"]:
        opts.add_argument("--incognito")
    if cfg["headless"]:
        opts.add_argument("--headless=new")
    w, h = cfg["window_size"].split(",")
    opts.add_argument(f"--window-size={int(w)},{int(h)}")
    if os.getenv("CI"):
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)

    # Enable CDP network for HAR
    with contextlib.suppress(Exception):
        drv.execute_cdp_cmd("Network.enable", {"maxTotalBufferSize": 100_000_000, "maxResourceBufferSize": 50_000_000})
    return drv


def _firefox(cfg):
    opts = FirefoxOptions()
    if cfg["headless"]:
        opts.add_argument("-headless")
    opts.set_preference("intl.accept_languages", cfg["lang"])
    service = FirefoxService(GeckoDriverManager().install())
    drv = webdriver.Firefox(service=service, options=opts)

    # set window size explicitly for FF
    w, h = map(int, cfg["window_size"].split(","))
    with contextlib.suppress(Exception):
        drv.set_window_size(w, h)
    return drv


def _edge(cfg):
    opts = EdgeOptions()
    opts.use_chromium = True
    if cfg["headless"]:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--lang={cfg['lang']}")
    if cfg["incognito"]:
        opts.add_argument("-inprivate")
    w, h = cfg["window_size"].split(",")
    opts.add_argument(f"--window-size={int(w)},{int(h)}")

    service = EdgeService(EdgeChromiumDriverManager().install())
    drv = webdriver.Edge(service=service, options=opts)

    # Enable CDP network for HAR (Edge)
    with contextlib.suppress(Exception):
        drv.execute_cdp_cmd("Network.enable", {})
    return drv


def _build_driver(py_cfg) -> WebDriver:
    cfg = {
        "browser": py_cfg.getoption("--browser").lower(),
        "headless": py_cfg.getoption("--headless"),
        "base_url": py_cfg.getoption("--base-url"),
        "window_size": py_cfg.getoption("--window-size"),
        "lang": py_cfg.getoption("--lang"),
        "incognito": py_cfg.getoption("--incognito"),
        "iwait": int(py_cfg.getoption("--iwait")),
        "har": bool(py_cfg.getoption("--har")),
    }

    if cfg["browser"] == "chrome":
        drv = _chrome(cfg)
    elif cfg["browser"] == "firefox":
        drv = _firefox(cfg)
    elif cfg["browser"] == "edge":
        drv = _edge(cfg)
    else:
        raise pytest.UsageError(f"Unsupported --browser={cfg['browser']}")

    drv.implicitly_wait(cfg["iwait"])
    with contextlib.suppress(Exception):
        drv.set_page_load_timeout(60)
        drv.set_script_timeout(30)

    # expose config
    drv.test_cfg = cfg
    drv.base_url = cfg["base_url"].rstrip("/")
    return drv


# ================================ WebDriver ==================================
@pytest.fixture(scope="function")
def driver(request):
    drv = _build_driver(request.config)
    yield drv
    with contextlib.suppress(Exception):
        drv.quit()


@pytest.fixture(scope="class")
def setup(request, driver):
    """Compatibility for class-based tests: request.cls.driver = driver."""
    request.cls.driver = driver
    yield


@pytest.fixture(scope="session")
def base_url(request) -> str:
    return request.config.getoption("--base-url")


@pytest.fixture(scope="session")
def ui_creds() -> tuple[str, str, str]:
    ui_cfg: RunCfg = ConfigLoader().load()
    """
    Provide (username, password) pair for UI login tests.

    Username and password are taken from:
      - config/common.properties -> test_user
      - config/user/<test_user>.properties
    """
    return ui_cfg.api_user_name, ui_cfg.api_user_password, ui_cfg.ui_user_id


# ================================ HAR recorder ===============================
def _is_chromium(drv) -> bool:
    name = (drv.capabilities or {}).get("browserName", "").lower()
    return name in ("chrome", "msedge", "edge", "chromium")


@pytest.fixture(scope="function", autouse=True)
def har_recorder(request, driver, base_url):
    """
    Record HAR via Chrome DevTools 'performance' logs.
    Enabled only when --har and Chromium-based browser.
    """
    if not driver.test_cfg.get("har") or not _is_chromium(driver):
        yield None
        return

    # flush previous logs
    with contextlib.suppress(Exception):
        driver.get_log("performance")

    yield {}

    try:
        raw = driver.get_log("performance")
    except Exception:
        raw = []

    events = []
    for e in raw:
        try:
            evt = json.loads(e["message"])["message"]
            events.append(evt)
        except Exception:
            continue

    target_host = urlsplit(base_url).netloc or "demoqa.com"
    requests_map = {}  # requestId -> data

    # Collect requests/responses
    for ev in events:
        method = ev.get("method")
        params = ev.get("params", {})
        rid = params.get("requestId")
        if not rid:
            continue

        if method == "Network.requestWillBeSent":
            req = params.get("request", {})
            url = req.get("url", "")
            if target_host not in url:
                continue
            requests_map.setdefault(rid, {})
            requests_map[rid]["request"] = {
                "url": url,
                "method": req.get("method"),
                "headers": req.get("headers", {}),
                "postData": req.get("postData"),
                "timestamp": params.get("timestamp"),
            }

        elif method == "Network.responseReceived":
            resp = params.get("response", {})
            url = resp.get("url", "")
            if target_host not in url:
                continue
            requests_map.setdefault(rid, {})
            requests_map[rid]["response"] = {
                "url": url,
                "status": resp.get("status"),
                "statusText": resp.get("statusText"),
                "headers": resp.get("headers", {}),
                "mimeType": resp.get("mimeType"),
            }

        elif method == "Network.loadingFinished":
            requests_map.setdefault(rid, {})
            requests_map[rid]["loadingFinished"] = params

    # Fetch bodies via CDP (best-effort)
    for rid, entry in list(requests_map.items()):
        if "response" not in entry:
            continue
        with contextlib.suppress(Exception):
            body_res = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": rid})
            entry["response"]["body"] = body_res.get("body", "")
            entry["response"]["base64Encoded"] = body_res.get("base64Encoded", False)

    # Build minimal HAR 1.2
    har = {"log": {"version": "1.2", "creator": {"name": "pytest-har", "version": "1.0"}, "entries": []}}
    for rid, e in requests_map.items():
        req = e.get("request", {})
        resp = e.get("response", {})
        lf = e.get("loadingFinished", {})
        if not req or not resp:
            continue
        har["log"]["entries"].append({
            "startedDateTime": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "time": 0,
            "request": {
                "method": req.get("method"),
                "url": req.get("url"),
                "httpVersion": "HTTP/1.1",
                "headers": [{"name": k, "value": str(v)} for k, v in (req.get("headers") or {}).items()],
                "queryString": [],
                "postData": (
                    {"mimeType": (req.get("headers", {}) or {}).get("Content-Type", ""),
                     "text": req.get("postData", "")}
                    if req.get("postData") else None
                ),
                "headersSize": -1,
                "bodySize": -1,
            },
            "response": {
                "status": resp.get("status", 0),
                "statusText": resp.get("statusText", ""),
                "httpVersion": "HTTP/1.1",
                "headers": [{"name": k, "value": str(v)} for k, v in (resp.get("headers") or {}).items()],
                "content": {
                    "size": int(lf.get("encodedDataLength", -1)) if isinstance(lf.get("encodedDataLength"),
                                                                               (int, float)) else -1,
                    "mimeType": resp.get("mimeType", ""),
                    "text": resp.get("body", ""),
                },
                "redirectURL": (resp.get("headers") or {}).get("location", ""),
                "headersSize": -1,
                "bodySize": int(lf.get("encodedDataLength", -1)) if isinstance(lf.get("encodedDataLength"),
                                                                               (int, float)) else -1,
            },
            "cache": {},
            "timings": {"send": -1, "wait": -1, "receive": -1},
        })

    outdir = Path("target/har")
    outdir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{request.node.name}_{ts}.har"
    fpath = outdir / fname
    fpath.write_text(json.dumps(har, ensure_ascii=False, indent=2), encoding="utf-8")

    with contextlib.suppress(Exception):
        allure.attach.file(str(fpath), name=fname, attachment_type=allure.attachment_type.JSON)


# ============================== Failure attachments ==========================
def _attach_text(name: str, content: str):
    with contextlib.suppress(Exception):
        allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def _attach_json(name: str, obj):
    with contextlib.suppress(Exception):
        allure.attach(json.dumps(obj, indent=2, ensure_ascii=False),
                      name=name, attachment_type=allure.attachment_type.JSON)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # run all other allure_hooks to obtain report
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        drv = item.funcargs.get("driver")
        if not drv:
            return

        ts = time.strftime("%Y-%m-%d_%H-%M-%S")
        with contextlib.suppress(Exception):
            allure.attach(drv.get_screenshot_as_png(), name=f"{item.name}_{ts}.png",
                          attachment_type=allure.attachment_type.PNG)
        with contextlib.suppress(Exception):
            allure.attach(drv.page_source, name=f"{item.name}_{ts}.html",
                          attachment_type=allure.attachment_type.HTML)
        with contextlib.suppress(Exception):
            _attach_text("current_url.txt", drv.current_url)
        with contextlib.suppress(Exception):
            logs = drv.get_log("browser")
            if logs:
                _attach_json("console.json", logs)
