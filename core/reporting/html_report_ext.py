import os
import time
from datetime import datetime
from pytest_html import extras
from core.logging import Logger

SCREENSHOT_DIR = "screenshots"
log = Logger.get_logger()

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def _screenshot_from_item(item):
    driver = None
    for key in ("driver", "driver_mod", "driver_session"):
        driver = item.funcargs.get(key) if hasattr(item, "funcargs") else None
        if driver:
            break
    if not driver:
        return None
    fname = "screenshot_%s.png" % datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(SCREENSHOT_DIR, fname)
    try:
        driver.save_screenshot(path)
        return os.path.normpath(path)
    except Exception as e:
        Logger.warn(log, "Failed to capture screenshot: %s" % e)
        return None

def process_report(report, item, call):
    cls = item.cls
    if cls and hasattr(cls, "_html_sub_suite"):
        report._html_sub_suite = getattr(cls, "_html_sub_suite")
    if cls and hasattr(cls, "_feature"):
        report._feature = getattr(cls, "_feature")

    if hasattr(item.function, "_html_title_template"):
        template = getattr(item.function, "_html_title_template")
        try:
            param_map = item.callspec.params if hasattr(item, "callspec") else {}
            report._html_title = template.format(**param_map)
        except Exception:
            report._html_title = template
    elif hasattr(item.function, "_html_title"):
        report._html_title = getattr(item.function, "_html_title")

    if call.when == "call" and hasattr(item, "html_steps"):
        report.html_steps = getattr(item, "html_steps", [])

    if call.when == "call":
        report.duration = getattr(report, "duration", 0)
        start_time = time.time() - report.duration
        report.formatted_start_time = datetime.fromtimestamp(start_time).strftime("%H:%M:%S")

    if call.when == "call" and report.failed:
        shot = _screenshot_from_item(item)
        if shot:
            extra = getattr(report, "extra", [])
            rel = os.path.relpath(shot, os.getcwd())
            extra.append(extras.image(rel, name="Failure Screenshot"))
            report.extra = extra

def customize_header(cells):
    cells[:] = [
        '<th class="sortable" data-column-type="feature">Feature</th>',
        '<th class="sortable" data-column-type="sub_suite">Test set</th>',
        '<th class="sortable" data-column-type="testId">Test</th>',
        '<th class="sortable" data-column-type="start_time">Start Time</th>',
        '<th class="sortable" data-column-type="steps">Steps</th>',
        cells[2],
        cells[0],
        '<th>Screenshot</th>',
        cells[3],
    ]

def customize_row(report, cells):
    feature = getattr(report, "_feature", "")
    sub_suite = getattr(report, "_html_sub_suite", "")
    test_name = getattr(report, "_html_title", report.nodeid.split(":")[-1])
    start_time = getattr(report, "formatted_start_time", "N/A")
    steps = getattr(report, "html_steps", [])
    steps_html = "" if steps else '<span style="color: gray;"></span>'
    for idx, s in enumerate(steps, 1):
        steps_html += '<span>%d. %s</span><br>' % (idx, s)

    screenshot_html = ""
    if hasattr(report, "extra") and report.extra:
        for extra in report.extra:
            if extra.get("format_type") == "image":
                screenshot_html = (
                    '<a href="%s" target="_blank">'
                    '<img src="%s" alt="screenshot" style="max-height: 100px; max-width: 100px;" />'
                    "</a>"
                ) % (extra["content"], extra["content"])
                break

    cells[:] = [
        '<td data-column-type="feature">%s</td>' % feature,
        '<td data-column-type="sub_suite">%s</td>' % sub_suite,
        '<td data-column-type="testId">%s</td>' % test_name,
        '<td data-column-type="start_time" data-value="%s">%s</td>' % (start_time, start_time),
        '<td data-column-type="steps">%s</td>' % steps_html,
        cells[2],
        cells[0],
        "<td>%s</td>" % screenshot_html,
        cells[3],
    ]
