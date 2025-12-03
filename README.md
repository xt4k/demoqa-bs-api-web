# Py-ecosystem UI & API testing for DemoQA Book Store

##### Demo project for Python UI/API/E2E automation around `https://demoqa.com/`

![DemoQA logo](https://demoqa.com/favicon.ico)

---

## TABLE OF CONTENT

- [Technology stack](#technology-stack)
- [Project overview](#project-overview)
- [Project structure](#project-structure)
- [How to run tests locally](#how-to-run-tests-locally)
  - [Prerequisites](#prerequisites)
  - [Run API tests](#run-api-tests)
  - [Same layout as CI (parallel, Allure + HTML)](#same-layout-as-ci-parallel-allure--html)
  - [Run UI tests](#run-ui-tests)
  - [Local Allure report](#local-allure-report)
- [GitHub Actions pipeline](#github-actions-pipeline)
- [Published reports on GitHub Pages](#published-reports-on-github-pages)
- [Implemented test coverage](#implemented-test-coverage)
  - [API](#api)
  - [UI](#ui)
- [Future improvements](#future-improvements)

---

## Technology stack

| GitHub | GitHub Actions | PyCharm | Python | pytest / xdist | requests | Selenium | Allure | pytest-html | GitHub Pages |
|:------:|:--------------:|:-------:|:------:|:--------------:|:--------:|:--------:|:------:|:-----------:|:------------:|
| <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="40" height="40"> | <img src="https://avatars.githubusercontent.com/u/44036562?s=200&v=4" width="40" height="40"> | <img src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.png" width="40" height="40"> | <img src="https://www.python.org/static/opengraph-icon-200x200.png" width="40" height="40"> | <img src="https://docs.pytest.org/en/stable/_static/pytest1.png" width="40" height="40"> | <img src="https://avatars.githubusercontent.com/u/21003710?s=200&v=4" width="40" height="40"> | <img src="https://selenium.dev/images/selenium_logo_square_green.png" width="40" height="40"> | <img src="https://github.com/allure-framework/allure2/raw/master/.github/allure-logo.png" width="40" height="40"> | <img src="https://raw.githubusercontent.com/pytest-dev/pytest-html/master/doc/_static/logo.png" width="40" height="40"> | <img src="https://avatars.githubusercontent.com/u/9919?s=200&v=4" width="40" height="40"> |

**Key points:**

- **Language & test framework:** Python 3.13+/3.14, `pytest` with `pytest-xdist` for parallel execution.
- **API layer:** custom `HttpClient` built on top of `requests` with logging, Allure hooks, and auth helpers.
- **UI layer:** Selenium WebDriver, Page Object pattern, demo scenarios against `demoqa.com`.
- **Reporting:** Allure (`allure-pytest`) + `pytest-html` self-contained report.
- **CI/CD:** GitHub Actions pipeline which:
  - runs type checking (mypy),
  - executes API & UI tests in separate jobs,
  - archives raw test artifacts,
  - generates Allure + HTML reports on CI,
  - publishes reports to GitHub Pages.

---

## Project overview

This project demonstrates a **Python-ecosystem style** test automation framework for a public sandbox:

- **System under test:** DemoQA Book Store (`https://demoqa.com/BookStore/v1` API and related UI).
- **Levels of testing:**
  - API tests for **Account** and **BookStore** services.
  - UI tests for the DemoQA Book Store pages (navigation, login, profile).
- **Design goals:**
  - clear separation of concerns (clients → services → tests),
  - centralized configuration through `.properties` files,
  - shared `HttpClient` for all API calls,
  - reproducible CI pipeline with **publicly available** reports.

---

## Project structure

High-level layout (simplified, synced with the current repository):

```text
demoqa-bs-api-web/
├─ .github/
│  └─ workflows/
│     └─ tests.yml              # GitHub Actions pipeline
├─ config/
│  ├─ env/                      # Environment configs (qa.properties, dev.properties, ...)
│  ├─ user/                     # User configs (api_usr1.properties, ui_usr2.properties, ...)
│  └─ common.properties         # Shared settings
├─ core/
│  ├─ api/
│  │  ├─ clients/               # HTTP clients (AccountClient, BookStoreClient, base HttpClient)
│  │  ├─ models/                # Dataclasses for request/response payloads
│  │  └─ services/              # Service layer wrapping clients for tests
│  ├─ config/                   # Internal config helpers (env/user resolution)
│  ├─ http/                     # Shared HttpClient with logging, auth, hooks
│  ├─ providers/                # Data / request providers
│  ├─ ui/
│  │  └─ page_objects/
│  │     ├─ locators/           # Page locators (Books, Login, Profile, Sidebar)
│  │     ├─ base_page.py        # Common Selenium helpers
│  │     ├─ books_page.py
│  │     ├─ login_page.py
│  │     ├─ profile_page.py
│  │     └─ sidebar.py
│  └─ util/
│     ├─ allure_hooks/          # Allure integration hooks and pytest plugins
│     ├─ html_report/           # Custom html-report decorators & helpers
│     ├─ support/               # Extra utilities
│     ├─ logging.py             # Central logging setup
│     └─ run_log.log            # Example run log (local)
├─ tests/
│  ├─ api/
│  │  ├─ account/
│  │  │  ├─ test_account.py
│  │  │  └─ test_account_negative.py
│  │  ├─ bookstore/
│  │  │  ├─ test_bookstore.py
│  │  │  ├─ test_bookstore_negative.py
│  │  │  └─ conftest.py         # API fixtures for BookStore suite
│  │  └─ conftest.py            # Shared API fixtures (services, auth, etc.)
│  └─ ui/
│     ├─ base_test.py           # Base class for UI tests
│     ├─ conftest.py            # UI fixtures (driver, env)
│     ├─ test_books_menu_item.py
│     ├─ test_login.py
│     └─ test_profile.py
├─ .gitignore
├─ allure-pytest.txt            # Allure config for pytest (if used)
├─ bs_taf.zip                   # Archived reference of Java TAF (optional artifact)
├─ conftest.py                  # Root-level shared fixtures (logging, hooks)
├─ mypy.ini                     # mypy configuration
├─ pyrightconfig.json           # pyright configuration
├─ pytest.ini                   # pytest configuration
├─ pyvenv.cfg
├─ README.md
├─ report.html                  # Sample local pytest-html report
├─ requirements.txt
└─ run_log.log                  # Root log from last local run
```

### How to run tests locally
#### Prerequisites

To run the tests locally you need:
- **Python 3.13+ (CI uses 3.14).**
- **pip and a virtual environment (recommended).**

- **For UI tests:**
  - Google Chrome (or Chromium),
  - compatible ChromeDriver (or rely on webdriver-manager if configured).

#### Clone the repository and install dependencies:
```text
git clone https://github.com/xt4k/demoqa-bs-api-web.git
cd demoqa-bs-api-web
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

After this you can run API/UI tests the same way as on CI.

## Run API tests
The simplest way to run all API tests with verbose output:
```text
pytest tests/api -v
```

This run:
- **uses the default environment from config/env/*.properties (e.g. qa),**
- **uses default API user from config/user/*.properties,**
- **prints HTTP logs to console and to run_log.log via custom logger,**
- **does not generate Allure or HTML reports yet.**

### Same layout as CI (parallel, Allure + HTML)
#### To reproduce the CI layout locally, including:
- **xdist parallel execution,**
- **Allure results directory,**
- **self-contained HTML report,**

use:
```text
pytest tests/api \
  -n auto \
  --dist=loadscope \
  --alluredir=allure-results \
  --html=reports/report-api.html \
  --self-contained-html
```

#### Here:

- **`-n auto` — chooses the number of workers automatically.**

- **`--dist=loadscope` — keeps tests from one module / class on the same worker (better for fixtures).**

- **`--alluredir=allure-results` — stores raw Allure data under ./allure-results.**

- **`--html=reports/report-api.html` — generates pytest-html report under ./reports.**

- **`--self-contained-html` — embeds all CSS/JS into a single HTML file (easy to archive/publish).**

You can open `reports/report-api.html` directly in a browser after the run.

### Run UI tests

UI tests also can be run locally. Minimal example:
```text
export DEMOQA_BASE_URL="https://demoqa.com"
export DEMOQA_API_BASE="https://demoqa.com"

pytest tests/ui -v
```

To mirror the CI setup (parallel execution, Allure + HTML):
```text
export DEMOQA_BASE_URL="https://demoqa.com"
export DEMOQA_API_BASE="https://demoqa.com"

pytest tests/ui \
  -n 4 \
  --dist=loadgroup \
  --alluredir=allure-results \
  --html=reports/report-ui.html \
  --self-contained-html
```

- `--dist=loadgroup` is used so that tests with the same group marker can share the same browser/fixtures.

- Screenshots on failures are captured by custom hooks and attached to Allure / HTML reports 
(if configured in `core/util/allure_hooks` and `core/util/html_report`).

On Windows, use:
```text
set DEMOQA_BASE_URL=https://demoqa.com
set DEMOQA_API_BASE=https://demoqa.com
pytest tests\ui ...
```
#### Local Allure report
Any time you have allure-results generated (API or UI tests), you can launch local Allure UI:
```text
allure serve allure-results
```

This command:
- starts a temporary HTTP server,
- opens the report in your default browser,
- auto-regenerates data on rerun.

To just generate static HTML into a folder:
```text
allure generate allure-results --clean -o allure-report
```

and then open `allure-report/index.html` in a browser.

## GitHub Actions pipeline

CI/CD is configured in `.github/workflows/tests.yml`.

It contains several jobs:

1. `typecheck`:
- Checks out the repository.
- Sets up Python (3.14).
- Installs dependencies from `requirements.txt`.

Runs:
```text
mypy . | tee mypy-report.txt
```
- Uploads `mypy-report.txt` as `mypy-report` artifact.

2. `api`
- Checks out the code and installs dependencies.
- Runs API tests in parallel:
```text
pytest tests/api \
  -n auto \
  --maxfail=1 \
  --dist=loadscope \
  --html=reports/report-api.html \
  --self-contained-html \
  --alluredir=allure-results
```
- Archives:

  - `allure-results/`
  - `reports/report-api.html`
as the `api-reports` artifact.

Uses `continue-on-error: true` so that report generation and publishing still happen even if tests fail.

3. `ui`
- Checks out code.
- Sets up Python & Chrome (via `browser-actions/setup-chrome@v1`).
- Sets env vars (`DEMOQA_BASE_URL`, `DEMOQA_API_BASE`, `CHROME_PATH`).
- Runs Selenium UI tests with xdist:
```text
pytest tests/ui \
  -n 4 \
  --dist=loadgroup \
  --alluredir=allure-results \
  --html=reports/report-ui.html \
  --self-contained-html
```

- Uploads:
  - allure-results/
  - reports/report-ui.html

as the `ui-reports` artifact.

- Also marked with `continue-on-error: true` so flaky UI tests don’t break publishing.

4. `Publish Allure & HTML reports to GitHub Pages`
- Runs after api and ui.
- Downloads `api-reports` (required) and `ui-reports` (optional — failure to download does not fail the job).
- Installs **Allure CLI**.
- Generates Allure reports:
  - `site/api/allure/` from API results.
  - `site/ui/allure/` from UI results (if present).
- Copies pytest HTML reports as:
  - `site/api/report-api.html`
  - `site/ui/report-ui.html`
- Creates a simple `site/index.html` page with links to all available reports.
- Publishes `site/` to the `gh-pages` branch using `peaceiris/actions-gh-pages@v3`.

GitHub Pages is configured to serve the site from this `gh-pages` branch.

## Published reports on GitHub Pages

Latest public reports are available here:
- Landing page:
`https://xt4k.github.io/demoqa-bs-api-web/`

From the landing page you can navigate to:
- API – Allure report
`https://xt4k.github.io/demoqa-bs-api-web/api/allure/index.html`
- API – pytest HTML report
`https://xt4k.github.io/demoqa-bs-api-web/api/report-api.html`
- UI – Allure report
`https://xt4k.github.io/demoqa-bs-api-web/ui/allure/index.html`
- UI – pytest HTML report
`https://xt4k.github.io/demoqa-bs-api-web/ui/report-ui.html`

### Screenshots
1. **API pytest HTML report**
<p align="center"> <img src="https://github.com/xt4k/demoqa-bs-api-web/assets/XXXX/api-html-report.png" width="600"> </p>

2. **Landing page with report links (GitHub Pages)**

<p align="center"> <img src="https://github.com/xt4k/demoqa-bs-api-web/assets/XXXX/index-page.png" width="400"> </p>

3. **Allure overview (API tests)**

<p align="center"> <img src="https://github.com/xt4k/demoqa-bs-api-web/assets/XXXX/allure-overview.png" width="700"> </p>

4. **Allure suites view**

<p align="center"> <img src="https://github.com/xt4k/demoqa-bs-api-web/assets/XXXX/allure-suites.png" width="700"> </p>

5. **Allure detailed test execution (example)**
<p align="center"> <img src="https://github.com/xt4k/demoqa-bs-api-web/assets/XXXX/allure-test-details.png" width="700"> </p>

### Implemented test coverage
#### API
**Account service (`/Account/v1`)**

-`POST /User` – **create user**: happy path / negative checks

-`POST /GenerateToken` – **generate token**: happy path / negative tests

- All token handling is encapsulated in `HttpClient.authenticate_default()`:

    - uses user from `config/user/*.properties`,
    - generates `UserRequest` dataclass from config,
    - calls `GenerateToken` and stores token in session headers.

**BookStore service** (`/BookStore/v1`)

- `GET /Books` – list catalog
- `GET /Book/{isbn}` – get book by ISBN
- `POST /Books` – add books to user’s collection;
- `DELETE /Book` – delete a single book from user
- `DELETE /Books` – delete all books for user
- Negative flows (in `test_bookstore_negative.py`):
    - adding already existing book again;
    - invalid/malformed ISBN for CRUD operations;
    - unauthorized access where applicable.

All API tests share fixtures for:
- environment and base URLs (`config/env/qa.properties`),
- API users (`config/user/api_usrX.properties`),
- service objects (`BookStoreService`, `AccountService`),
- authenticated HTTP client instances.

**UI**

UI tests cover basic flows for the Book Store part of `demoqa.com`:

- Navigation:
     - open Book Store page from main menu / side bar,
     - verify menu items and links.

- Books grid/list:
  - check that the list of books is loaded,
  - basic assertions on table columns (title, author, publisher, etc.).

- Book details:
  - open a book from the list,
  - verify details (title, ISBN, description) on details page.

- Login / profile:
  - navigate to login page;
  - login with test user (if configured);
  - verify profile page structure/navigation.

Technical aspects:

- Page Object pattern:
 - `base_page.py` – common Selenium utilities (waits, click, text, etc.).
 - `books_page.py`, `login_page.py`, `profile_page.py` – page-specific actions.
- Locators are grouped in `core/ui/page_objects/locators/`.
- UI fixtures manage:
  - WebDriver lifecycle,
  - browser window sizing,
  - base URL.

- Screenshots on failure are attached via custom hooks in `core/util/allure_hooks` and `core/util/html_report`.
