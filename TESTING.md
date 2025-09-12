Testing Guide

Overview
- Uses Django’s built-in test runner with a temporary test database.
- Tests cover FBV flows for board and account apps, including comment AJAX endpoints.

Prerequisites
- Python 3.10+ recommended
- Virtual environment (venv)

Setup
1) Create and activate a virtual environment
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `python -m venv .venv; .venv\\Scripts\\Activate.ps1`

2) Install dependencies
   - `pip install -r requirements.txt`
   - Note: Pillow is required for ImageField; it is already listed in requirements.txt.

3) Configure environment (optional)
   - Copy `.env` (already present for local dev) or ensure defaults are fine.
   - By default, tests run against SQLite and do not need a running MySQL.

4) Run migrations for dev DB (optional but useful for quick manual checks)
   - `python manage.py migrate`

Running Tests
- Run all tests
  - `python manage.py test`

- Increase verbosity (more detail)
  - `python manage.py test -v 2`

- Run a specific app’s tests
  - `python manage.py test board`
  - `python manage.py test account`

- Run a specific test case or method
  - Case: `python manage.py test board.tests.BoardFBVTests`
  - Method: `python manage.py test board.tests.BoardFBVTests.test_create_update_delete_flow`

Notes
- The Django test client simulates HTTP requests without starting a server.
- Tests isolate state using a temporary database created and destroyed per test run.
- CSRF: The current test endpoints do not require CSRF tokens explicitly; views that require POST are tested with POST.

Troubleshooting
- Import errors: Ensure the virtual environment is active and dependencies are installed.
- ImageField error (Pillow): Reinstall Pillow: `pip install --force-reinstall pillow`.
- Database errors: Ensure `DB_ENGINE` is not set to `mysql` while testing unless a MySQL instance is configured; default is SQLite.

