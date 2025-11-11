# demoqa-bookstore-ui-api-e2e-selenium-py
A compact, production-style starter for **UI (Selenium)**, **API (requests)**, and **E2E** tests against the **DemoQA Book Store**.

## Configuration
Place your settings in `config/config.ini` or via env vars:
- INI keys (section `[demoqa]`): `base_url`, `api_base`, `login`, `password`
- Env overrides: `DEMOQA_BASE_URL`, `DEMOQA_API_BASE`, `DEMOQA_LOGIN`, `DEMOQA_PASSWORD`

If `login`/`password` are empty, tests auto-create a temporary user via API.
