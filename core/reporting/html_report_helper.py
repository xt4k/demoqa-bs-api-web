import os
import time
from datetime import datetime

from pytest_html import extras

from core.util.logging import Logger

SCREENSHOT_DIR = "screenshots"
logger = Logger.get_logger()

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)


def take_screenshot() -> str:
    """Capture a screenshot and return its file path."""
    screenshot_filename = f"screenshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
    return os.path.normpath(screenshot_path)


def process_report(report, item, call):
    """
    Process the test report to add additional data like screenshots, custom titles, and metadata.

    Args:
        report: The pytest report object.
        item: The pytest test item object.
        call: The pytest call object.
    """
    revision = getattr(item, "funcargs", {}).get("get_revision", None)

    # Extract metadata from test classes
    cls = item.cls
    if cls and hasattr(cls, "_html_sub_suite"):
        report._html_sub_suite = getattr(cls, "_html_sub_suite")
        if revision:
            report.html_revision = revision
            # Logger.log_info(logger, f"Test `{item.name}` has revision: {revision}")

    if cls and hasattr(cls, "_feature"):
        report._feature = getattr(cls, "_feature")

        # === HTML TITLE SUPPORT (STATIC AND DYNAMIC) ===
    if hasattr(item.function, "_html_title_template"):
        template = getattr(item.function, "_html_title_template")
        try:
            # Support dynamic values from @pytest.mark.parametrize
            param_map = item.callspec.params if hasattr(item, "callspec") else {}
            param_map["test_index"] = getattr(item.module, "test_index", "")
            report._html_title = template.format(**param_map)
        except Exception as e:
            logger.warning(f"[process_report] Failed to format html_title: {e}")
            report._html_title = template
    elif hasattr(item.function, "_html_title"):
        report._html_title = getattr(item.function, "_html_title")

    # === HTML STEPS SUPPORT ===
    if call.when == "call" and hasattr(item, "html_steps"):
        steps = getattr(item, "html_steps", [])
        report.html_steps = steps
        # Logger.log_info(logger, f"[p_r] html_steps {item.name}: {steps}")

    # === TIME METADATA ===
    if call.when == "call":
        report.duration = getattr(report, "duration", 0)  # Ensure duration exists
        report.start_time = time.time() - report.duration  # Calculate start time
        report.formatted_start_time = datetime.fromtimestamp(report.start_time).strftime(
            "%H:%M:%S")  # Convert timestamps to readable format
        # Logger.log_info(logger, f"Test `{item.name}` started at {report.formatted_start_time}, duration: {report.duration:.2f}s")

    # === SCREENSHOT ON FAILURE ===
    if call.when == "call" and report.failed:
        screenshot_path = take_screenshot()
        if screenshot_path:
            rel_screenshot_path = os.path.relpath(screenshot_path, os.getcwd())
            extra = getattr(report, "extra", [])
            extra.append(extras.image(rel_screenshot_path, name="Failure Screenshot"))
            report.extra = extra
            logger.info(f"[process_report] added screenshot: {report.extra}")


def customize_header(cells):
    """Reorder columns in the HTML report header."""
    cells[:] = [
        '<th class="sortable" data-column-type="feature">Feature</th>',
        '<th class="sortable" data-column-type="revision">Revision</th>',
        '<th class="sortable" data-column-type="sub_suite">Test set</th>',
        '<th class="sortable" data-column-type="testId">Test</th>',
        '<th class="sortable" data-column-type="start_time">Start Time</th>',
        '<th class="sortable" data-column-type="steps">Steps</th>',
        '<th class="sortable" data-column-type="duration">Duration</th>',
        '<th class="sortable" data-column-type="result">Result</th>',
        '<th>Screenshot</th>',
        '<th class="sortable" data-column-type="links">Links</th>',
    ]


def customize_row(report, cells):
    """Reorder and populate columns in the HTML report rows."""
    # logger.info(f"List of cells before processing: {cells}")
    # Get custom metadata
    feature_name = getattr(report, "_feature", "")
    revision = getattr(report, "html_revision", "N/A")

    sub_suite_name = getattr(report, "_html_sub_suite", "")
    screenshot_html = ""
    steps_html = ""
    start_time = getattr(report, "formatted_start_time", "N/A")
    # Get custom test name if available
    test_name = getattr(report, "_html_title", report.nodeid.split(":")[-1])
    steps = getattr(report, "html_steps", [])
    # Logger.log_info(logger, f"[c_r] html_steps: {steps}")
    if steps:
        steps_html = ""  # f"{len(steps)}:<br>"
        for idx, step in enumerate(steps, 1):
            steps_html += f'<span">{idx}. {step}</span><br>'
    else:
        steps_html = '<span style="color: gray;"></span>'
    # Logger.log_info(logger, f"Generated steps_html: {steps_html}")

    if hasattr(report, "extra") and report.extra:
        for extra in report.extra:
            if extra.get("format_type") == "image":
                # logger.info(f"[table_row] extra: {extra}")
                screenshot_html = (
                    f'<a href="{extra["content"]}" target="_blank">'
                    f'<img src="{extra["content"]}" alt="screenshot" style="max-height: 100px; max-width: 100px;" />'
                    f"</a>"
                )
                break
    # Reorganize cells based on the new order
    cells[:] = [
        f'<td data-column-type="feature">{feature_name}</td>',
        f'<td data-column-type="revision">{revision}</td>',
        f'<td data-column-type="sub_suite">{sub_suite_name}</td>',
        f'<td data-column-type="testId">{test_name}</td>',
        #  f"<td>{feature_name}</td>",  # Feature
        # f"<td>{sub_suite_name}</td>",  # Sub Suite
        # f"<td>{test_name}</td>",  # Test
        f'<td data-column-type="start_time" data-value="{start_time}">{start_time}</td>',
        f'<td data-column-type="steps">{steps_html}</td>',
        # f"<td>{steps_html}</td>",  # Steps
        cells[2],  # Duration
        cells[0],  # Result
        f"<td>{screenshot_html}</td>",  # Screenshot
        cells[3],  # Links
    ]
