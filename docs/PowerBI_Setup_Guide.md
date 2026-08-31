# ExpenseIQ - Power BI Dashboard Setup Guide

The backend exposes ready-made JSON analytics feeds under
`/api/v1/analytics/*` (see `backend/app/api/v1/analytics.py`). Power BI
Desktop connects to these directly with the built-in Web connector - no
extra ETL needed. This covers the RFP's 4 required views plus two bonus
feeds (reimbursement liability, AI accuracy) for QA evidence.

## Prerequisites

1. Backend running locally: `uvicorn app.main:app --reload` (from
   `backend/`), reachable at `http://127.0.0.1:8000`.
2. At least a few expenses processed through the pipeline - run
   `python scripts/bootstrap_org.py` first (one-time, creates the MAC
   teams/projects + the first HR_HEAD), then sign up a few real
   employees and submit/process some receipts so the dashboards
   aren't empty.
3. Power BI Desktop installed (Windows).

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
