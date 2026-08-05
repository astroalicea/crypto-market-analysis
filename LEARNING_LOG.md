# Learning Log — Crypto Market Analysis Project

> Fill this out at the end of every Claude Code session. Takes 5–10 minutes.
> This is your proof of growth. Future you will thank present you.

---

## How to Use This

At the end of each session, Claude Code will ask you the five reflection questions. Answer them here in a new entry. Be honest — especially on question 5. If you can't answer it, that's the most important thing to write down.

Don't write perfect answers. Write real ones.

---

## Entry Template

Copy this block for each new session:

```
---

### Session [NUMBER] — [DATE]
**Phase:** [e.g. Phase 2 — API Layer]
**Duration:** [e.g. 1.5 hours]
**What we built:**


**Why it was structured this way:**


**What problem it solves:**


**Alternatives that existed:**


**Could I rebuild this tomorrow without AI?** (Yes / Mostly / No — be honest)


**Concepts I need to review before next session:**


**Wins (even small ones):**


**Where I got stuck or confused:**


---
```

---

## Entries

<!-- Your entries go below this line. Newest at the top. -->

---

### Session 2 — 2026-08-04
**Phase:** Phase 3 (finish) → Phase 4 → Phase 5 — Market Cap Tiering, Matplotlib Dashboard, Django Backend
**Duration:**
**What we built:**
- `assign_market_cap_tiers()` in `analysis.py` — classifies coins into small/mid/large cap using fixed dollar thresholds (`pd.cut`), finishing Phase 3.
- `charts.py` — a horizontal bar chart (top 10 by market cap), a scatter plot (volume vs. 24h price change, colored by tier), and `build_dashboard()` combining both into one exported PNG. Closed Phase 4.
- Full Django backend for Phase 5: project scaffold (`crypto_dashboard`), a `dashboard` app, the `CoinSnapshot` model + migration, a `fetch_coins` management command that pulls the existing pipeline into the ORM, and a dashboard view + template with a live `chart.png` endpoint.
- Fixed a stale `requirements.txt` (pandas/numpy/matplotlib were installed but unpinned), untracked `__pycache__` files that predated `.gitignore`, moved Django's `SECRET_KEY` out of source into `.env` via `python-decouple`, and found/fixed a `.gitignore` bug where every line except the first had a leading space and silently never matched anything — which meant `.env` had been tracked in git the whole time (only ever committed empty, so no real key leaked).
- Caught a real bug by actually running the dev server instead of trusting green tests: matplotlib defaulted to an interactive GUI backend, which crashed off Django's main request thread. Fixed by forcing the `Agg` backend inside `charts.py` itself.
- All 40 tests passing; pushed to `origin/main`.

**Why it was structured this way:**
- Market cap tiers use fixed thresholds (large/mid/small by real dollar cutoffs), not quantiles, because quantile tiers are relative to whatever slice of the market got fetched (`per_page`) — a top-10 fetch would mislabel a $20B coin as "small cap." Fixed thresholds mean the label carries the same real-world meaning regardless of fetch size.
- Chart functions return `(fig, ax)` instead of calling `plt.show()`, following the "return, not print" rule extended to plotting — a function that returns objects is testable and reusable; one that does I/O internally isn't.
- The dashboard chart is generated in-memory (`BytesIO`) and streamed as an HTTP response rather than written to disk, avoiding a `MEDIA_ROOT`/static-files setup that isn't needed yet.
- `CoinSnapshot` uses `DecimalField` for money fields instead of `FloatField`, because floats have binary rounding error and Decimal is the standard choice for anything money-shaped.

**What problem it solves:**
Closes the gap between "I have a data pipeline that prints numbers" and "I have a web app with a database, a way to refresh its data, and a page that displays it" — the actual shape of the portfolio project's end goal.

**Alternatives that existed:**
- Quantile-based tiering (`pd.qcut`) instead of fixed thresholds.
- Writing the dashboard chart to disk (`MEDIA_ROOT`) instead of streaming it from memory.
- Plotly instead of Matplotlib — ruled out for now since the checklist wanted a static PNG, not an interactive chart; noted as a real option for Phase 5 later if the dashboard wants interactivity.

**Could I rebuild this tomorrow without AI?** (Yes / Mostly / No — be honest)
No

**Concepts I need to review before next session:**


**Wins (even small ones):**


**Where I got stuck or confused:**


---

### Session 1 — [DATE]
**Phase:** Phase 1 — Setup & First Run
**Duration:**
**What we built:**


**Why it was structured this way:**


**What problem it solves:**


**Alternatives that existed:**


**Could I rebuild this tomorrow without AI?** (Yes / Mostly / No)


**Concepts I need to review before next session:**


**Wins:**


**Where I got stuck or confused:**


---

## Concepts Reference — Build This As You Go

> Add terms here as you learn them. Your own definitions stick better than Google's.

| Term | What It Means (in my own words) | Where I first used it |
|------|---------------------------------|----------------------|
| return vs print | | Session 1 |
| DataFrame | | |
| ORM | | |
| migration | | |
| API endpoint | | |
| HTTP status code | | |
| try/except | | |
| environment variable | | |
| gunicorn | | |
| reverse proxy | | |
| pytest / mocking | | |
| NumPy array | | |
| normalization | | |
| standard deviation | | |

Add rows as you encounter new terms.

---

## Phase Completion Milestones

Mark these when you genuinely feel you understand the phase — not just when the code works.

- [ ] **Phase 2 complete** — I can explain HTTP requests, JSON, API error handling, and why `return` matters without looking anything up
- [ ] **Phase 3 complete** — I can explain what a DataFrame is, what NumPy adds, and walk through my analysis code from memory
- [ ] **Phase 4 complete** — I can explain Matplotlib's figure/axes model and when I'd choose it over Plotly
- [ ] **Phase 5 complete** — I can draw the Django request lifecycle on a whiteboard and explain the ORM
- [ ] **Phase 6 complete** — I can explain what gunicorn and nginx do and why both are needed, and I have a live URL

---

## Interview Prep — Update After Each Phase

> These are answers to real interview questions based on what you built.

**"Tell me about a project you built."**
*(Update as you go)*


**"Walk me through your data pipeline."**
*(Update as you go)*


**"What would you do differently if you built this again?"**
*(Update as you go)*


**"How does this project relate to data engineering?"**
*(Update as you go)*
