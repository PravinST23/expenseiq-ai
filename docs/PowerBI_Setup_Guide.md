# ExpenseIQ - Power BI Dashboard Setup Guide

The backend exposes ready-made JSON analytics feeds under
`/api/v1/analytics/*` (see `backend/app/api/v1/analytics.py`). Power BI
Desktop connects to these directly with the built-in Web connector - no
extra ETL needed. This covers the RFP's 4 required views plus two bonus
feeds (reimbursement liability, AI accuracy) for QA evidence.

## Fastest path: open the pre-built project

`powerbi/ExpenseIQ.pbip` at the repo root is a complete, ready-to-open
Power BI Project (the modern text-based PBIP/TMDL format, not a binary
`.pbix`) with all 5 required pages, both semantic model tables and
report visuals already authored, pointed at the local analytics API.

1. Start the backend (`uvicorn app.main:app --reload` from `backend/`,
   reachable at `http://127.0.0.1:8000`) with at least some expenses
   processed so the dashboards aren't empty.
2. In Power BI Desktop, enable the two preview features this project
   uses (one-time, per machine): **File -> Options and settings ->
   Options -> Preview features** -> check **Power BI Project (.pbip)
   save option**, **Store reports using enhanced metadata format
   (PBIR)**, and **Store semantic model using TMDL format** -> restart
   Desktop.
3. **File -> Open -> Browse** to `powerbi/ExpenseIQ.pbip` and open it.
   Power BI Desktop loads the semantic model, calls the 5 analytics
   endpoints listed below, and the 5 report pages (Overview, Spend by
   Category, Spend by Employee, Approval Status Summary, Reimbursement
   Liability Tracker) render with live data.
4. If a page renders blank on first open, hit **Home -> Refresh** once
   - Power BI Desktop sometimes needs an explicit refresh the very
   first time a project-format model loads.
5. Apply the color theme: **View -> Themes -> Browse for themes** ->
   select `powerbi/ExpenseIQTheme.json` (repo root, alongside the
   `.pbip` file). This is Power BI Desktop's own standard theme-import
   feature - more reliable than hand-authoring the theme reference
   into the PBIP file, which is what caused it not to apply earlier.

This was hand-authored (not exported from a live Desktop session), so
if it doesn't open cleanly, whatever error dialog Power BI Desktop
shows names the exact file - share that message and it can be fixed
directly, since PBIR/TMDL are both publicly documented JSON/text
formats.

Two feeds aren't in the pre-built project (spend by project, and the
AI-accuracy/QA-evidence feed) - add them as extra pages using the
manual steps below if you want them too.

## Manual path / adding more pages

## Step 1 - Connect each feed

Repeat for each URL below: **Home -> Get Data -> Web** -> paste the URL
-> **OK** -> in the preview window, Power BI auto-detects the JSON as a
table -> **Transform Data** (opens Power Query) -> confirm the columns
look right -> **Close & Apply**.

| Dashboard View (RFP requirement) | URL | Suggested visual |
|---|---|---|
| Spend by category | `http://127.0.0.1:8000/api/v1/analytics/spend-by-category` | Clustered bar chart (category vs total_amount) |
| Spend by employee | `http://127.0.0.1:8000/api/v1/analytics/spend-by-employee` | Clustered bar chart (employee_name vs total_amount), sorted descending |
| Approval status summary | `http://127.0.0.1:8000/api/v1/analytics/approval-status-summary` | Donut chart (status vs count) |
| Reimbursement liability tracker | `http://127.0.0.1:8000/api/v1/analytics/reimbursement-liability` -> expand the `by_state` list | Stacked bar (state vs total_amount) + a card visual for `outstanding_liability` |
| Spend by project (bonus) | `http://127.0.0.1:8000/api/v1/analytics/spend-by-project` | Treemap |
| AI accuracy / QA evidence (bonus) | `http://127.0.0.1:8000/api/v1/analytics/ai-accuracy` | Card visuals: duplicate_rate, average_fraud_risk, average_compliance_risk, average_confidence |
| Executive overview KPIs | `http://127.0.0.1:8000/api/v1/analytics/overview` | Card visuals for the header row |

For endpoints that return a nested list (`reimbursement-liability`'s
`by_state`, `ai-accuracy`'s `recommendation_mix` /
`processing_engine_mix`), use Power Query's **List Tools -> To Table**,
then **Expand** the resulting record column to get flat rows.

## Step 2 - Build the 4 required pages

1. **Executive Dashboard** - KPI cards from `/overview` (total
   employees, total expenses, total spend, approved amount) + the
   approval status donut.
2. **Spend Analytics** - category bar chart + employee bar chart +
   project treemap, with slicers for department / project / date range
   (add a `Date` table via **Modeling -> New Table** if you want a
   proper date slicer; `expense_date` isn't in these aggregate feeds by
   design - point a slicer at the `spend-by-employee` department field
   instead, or extend the backend endpoint with a date filter query
   param if a real date slicer is required).
3. **Approval & Reimbursement** - approval status donut + reimbursement
   liability stacked bar + the `outstanding_liability` card.
4. **AI Insights (QA evidence)** - duplicate rate, average risk scores,
   recommendation mix (from `ai-accuracy`) - this page doubles as the
   AI-structured-data-correctness evidence required by the QA strategy.

## Step 3 - Refresh

**Home -> Refresh** re-pulls every feed live from the running backend.
For the Week 17 demo, refresh once right before presenting so the
numbers match whatever was just processed live.

## Publishing (optional)

If you have a Power BI Pro/free account, **Home -> Publish** pushes the
report to the Power BI Service so it's shareable via a link instead of
only the local `.pbix` file - useful for the Moodle evidence package
(screenshot both the desktop file and, if published, the shared link).

## Reconciliation check (QA requirement)

The proposal's QA strategy requires a Power BI vs. PostgreSQL data-drift
check. Run this to compare a dashboard number against the source of
truth directly:

```sql
-- Should match the "Total Spend" card / spend-by-category sum
SELECT SUM(amount) FROM expenses;

-- Should match the reimbursement-liability outstanding_liability figure
SELECT SUM(amount) FROM expenses WHERE reimbursement_state IN ('PENDING', 'APPROVED');
```
