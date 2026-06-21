# EnobFinance

Personal finance manager built with Python and Django. Part of the Enob ecosystem.

## Features

- **Monthly budgeting** — each month is a standalone page with income, variable expenses, and fixed expenses
- **Carry-over balance** — the closing balance of month N automatically becomes the opening balance of month N+1
- **Credit card invoices** — track invoices per card per month
- **Investments with goal** — log investments and set a monthly target; annual view shows goal vs. actual
- **Installment plans** — manage multi-installment payments and sales, mark each installment paid, attach receipt URLs
- **Excel export** — download a full `.xlsx` workbook with an annual summary, per-month sheets, cards, and installment plans
- **Multi-user** — each user sees only their own data; email-based authentication

## Prerequisites

- Python 3.14+
- pip

## Local Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd enob-finance

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Create an admin user
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Open http://localhost:8000 in your browser.

## Docker

```bash
# Copy and fill in the required environment variable
echo "SECRET_KEY=your-secret-key-here" > .env

# Build and start
docker-compose up --build
```

The app will be available at http://localhost:8000. The SQLite database is persisted via a bind mount (`./db.sqlite3`).

## Production

Set the following environment variables and point Django at the production settings module:

```bash
export SECRET_KEY="<long-random-string>"
export ALLOWED_HOSTS="yourdomain.com"
export DJANGO_SETTINGS_MODULE="enobfinance.settings_prod"

python manage.py migrate
python manage.py collectstatic --no-input
gunicorn enobfinance.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

`settings_prod.py` enforces `DEBUG=False`, secure cookie flags, HTTPS redirect, and console logging.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14, Django 6 |
| Frontend | Django Template Language, TailwindCSS (CDN) |
| Database | SQLite |
| Excel export | openpyxl |
| Production server | Gunicorn |
| Container | Docker / docker-compose |
