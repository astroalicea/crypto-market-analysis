# Crypto Market Analysis

An end-to-end data pipeline that pulls live cryptocurrency market data from the CoinGecko API, cleans and enriches it with pandas and NumPy, stores each run in a database, and serves it through a Django dashboard with Matplotlib charts.

Built as a portfolio project to practice the core data engineering loop: **extract → transform → load → serve**.

## How it works

```
CoinGecko API ──► fetcher.py ──► analysis.py ──► Database ──► Django views ──► Browser
   (source)        (extract)      (transform)      (load)        (serve)
                       └──────── fetch_coins command ────────┘
```

| Stage | File | What it does |
|---|---|---|
| Extract | `fetcher.py` | Calls `/coins/markets`. Handles timeouts, HTTP errors (including 429 rate limits), and malformed JSON. Returns `None` on failure instead of crashing. |
| Transform | `analysis.py` | Loads results into a DataFrame, drops records with missing fields, and assigns market cap tiers (small < $1B ≤ mid < $10B ≤ large). |
| Load | `dashboard/management/commands/fetch_coins.py` | Records each run as a `FetchRun` and writes the coins as `CoinSnapshot` rows in a single transaction. |
| Serve | `dashboard/views.py`, `charts.py` | Renders a table from the latest **successful** run, plus a PNG chart (top 10 by market cap; volume vs. 24h price change). |

The dashboard never calls CoinGecko directly. It only reads from the database, so page loads stay fast and an API outage can't take the site down. The page simply keeps showing the last good data.

## Tech stack

- **Python 3.12+**: requests, pandas, NumPy, Matplotlib
- **Django 6**: ORM, management commands, views and templates
- **SQLite** locally (PostgreSQL planned for production)
- **pytest** + pytest-django for testing
- **python-decouple** for environment-based configuration

## Getting started

```bash
git clone git@github.com:astroalicea/crypto-market-analysis.git
cd crypto-market-analysis

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env              # then set DJANGO_SECRET_KEY (instructions inside)
python manage.py migrate          # create the database tables
```

## Usage

**1. Run the pipeline.** This fetches the top 20 coins by market cap and stores them:

```bash
python manage.py fetch_coins
python manage.py fetch_coins --per-page 50   # fetch more coins
```

**2. Start the dashboard:**

```bash
python manage.py runserver
```

Then open:

- http://127.0.0.1:8000/ shows the coin table
- http://127.0.0.1:8000/chart.png shows the chart image on its own
- http://127.0.0.1:8000/admin/ lets you browse runs and snapshots (run `python manage.py createsuperuser` first)

The data is only as fresh as your last `fetch_coins` run. Run it again to update the dashboard.

## Running tests

```bash
pytest
```

The tests cover the API client (mocked responses for timeouts, HTTP errors, network failures, and bad JSON), the analysis functions, chart generation, the `fetch_coins` command, the models, and the views.

## Design decisions

- **Run tracking with `FetchRun`.** Every pipeline execution is recorded, including failed ones, with a status and an error message. The dashboard reads only from the latest successful run, so a failed fetch never shows a partial or empty page.
- **Atomic writes.** Snapshots and the run's success status are committed together in one transaction. Either the whole run lands or none of it does.
- **Fixed market cap thresholds instead of quantiles.** Tiers use industry-standard cutoffs ($1B, $10B), so a coin's tier means the same thing no matter which other coins were fetched alongside it.
- **`Decimal` for money, `float` for percentages.** Prices and market caps are stored as `DecimalField` to avoid floating-point rounding. They are converted to floats only at the charting step, where exact precision doesn't matter.
- **Explicit failure handling.** Functions return `None` and log the reason rather than raising into the caller or failing silently.

## Roadmap

- [x] API layer with error handling
- [x] pandas/NumPy analysis and tiering
- [x] Matplotlib dashboard
- [x] Django app with run tracking
- [x] Production-safe settings (env vars, `DEBUG=False`, `ALLOWED_HOSTS`)
- [ ] Deploy to AWS EC2 with gunicorn + nginx
- [ ] Scheduled fetches (cron, later Airflow) so the dashboard updates itself
- [ ] PostgreSQL in production
