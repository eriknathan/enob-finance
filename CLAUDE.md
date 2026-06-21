# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**EnobFinance** — personal finance manager built with Python + Django full stack. Part of the Enob ecosystem.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Database
python manage.py migrate
python manage.py makemigrations <app_name>

# Run
python manage.py runserver

# Create superuser
python manage.py createsuperuser
```

## Architecture

Monolithic Django app — backend, business logic, and frontend all in Django. No JS framework. TailwindCSS via CDN. SQLite database.

### Apps (prefix `app_`)

| App | Responsibility |
|---|---|
| `app_core` | `TimestampedModel` base, `base.html`, shared mixins, home redirect |
| `app_accounts` | Custom User (email login), authentication |
| `app_months` | `FinancialMonth` and its entries: income, variable/fixed expenses, summary, balance |
| `app_cards` | Credit cards and monthly invoices |
| `app_investments` | Monthly investments and annual goal vs. actual view |
| `app_installments` | Installment plans (payments and sales) and their parcels |
| `app_dashboard` | Consolidated monthly and annual dashboard |
| `app_exports` | Excel export via openpyxl |

### Key design decisions

- `AUTH_USER_MODEL = 'app_accounts.User'` — must be set before the first migration.
- All models inherit `TimestampedModel` from `app_core` (`created_at`, `updated_at`).
- Calculated values (totals, balances) are **never stored** — always derived via model methods/properties.
- Every query must filter by the authenticated user (`request.user`).
- Balance carry-over: the final balance of month N becomes an "Entry" in month N+1, fetched by `(year, month)` lookup — treat missing previous month as zero.
- Installment `kind`: `'payment'` (expense) or `'sale'` (income).
- Receipt proofs are stored as URLs (e.g. Google Drive links), not file uploads.

### Templates

All templates live under `templates/` at the project root, organized by app:

```
templates/
  base.html
  components/
  app_accounts/
  app_months/
  ...
```

`settings.py` must have `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']`.

Signals go in `signals.py` inside each app.

## Code conventions

- **Language:** code and comments in English; UI text in Brazilian Portuguese.
- **Quotes:** single quotes throughout.
- **Views:** Class Based Views (`LoginRequiredMixin`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`). No function views unless strictly necessary.
- **Dependencies:** only `Django`, `openpyxl`, and (later) Google OAuth. No other external libs.
- No over-engineering — implement only what the PRD defines.

## Design system

Dark premium aesthetic with Tailwind utility classes. Key tokens:

- Primary gradient: `bg-gradient-to-r from-[#0066FF] to-[#00AAFF]`
- Dark background: `#000918` / surfaces: `#0A1428`
- Font: **Sora** (`font-['Sora']`)
- Status pills: `bg-green-50 text-green-600` (paid) / `bg-red-50 text-red-600` (unpaid)
- Card container: `rounded-2xl bg-white border border-gray-100 shadow-sm p-6`
- Balance card: `rounded-2xl bg-gradient-to-br from-[#0A1428] to-[#000918] text-white p-6`

Full component reference in [`docs/design-system.md`](docs/design-system.md).

## Documentation

See [`docs/`](docs/) for architecture, code standards, data models, and setup details.
