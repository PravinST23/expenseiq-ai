# Deviations from the Approved Proposal

Documented as they happen, per the mid-term evaluator's feedback that
undisclosed deviations (not the deviations themselves) were the real
problem last time. Both changes below were forced by upstream vendor
model retirements discovered on 2026-08-26 while hardening the AI
pipeline for the final submission - not scope changes.

## 1. Gemini model: `gemini-2.5-flash` -> `gemini-3.5-flash`

**Approved:** Google AI Studio - Gemini 2.5 Flash, multimodal receipt
extraction.

**Actual:** `models/gemini-2.5-flash` now returns `404 NOT_FOUND -
"This model ... is no longer available to new users"` on this API
key. The `-latest` alias (`models/gemini-flash-latest`) is reachable
but consistently times out (30s+, `ReadTimeout`). `models/gemini-3.5-
flash` was verified working end-to-end (upload + multimodal
extraction, ~8s, correct structured JSON) and is used instead - same
tier (fast/cheap multimodal flash model), same free-tier pricing
model, same prompt contract. `app/ai/gemini_service.py` documents this
inline.

**Impact:** None on functionality or cost. `GEMINI_MODEL` is a single
constant in `gemini_service.py` - trivial to swap again if Google
retires this one too.

## 2. Groq model: `llama-3.3-70b-versatile` -> `openai/gpt-oss-120b`

**Approved:** Groq Cloud - Llama 3.3 70B, policy compliance + risk
scoring.

**Actual:** `llama-3.3-70b-versatile` was removed from Groq's model
catalog (`404 model_not_found` - confirmed via `client.models.list()`,
it's no longer listed at all). `openai/gpt-oss-120b` is the closest
current equivalent on Groq's free tier (large open-weights model,
sub-2s responses, reliable structured JSON) and is used instead.
`app/ai/groq_service.py` documents this inline.

**Impact:** None on functionality or cost (still Groq free tier).

## 3. Rebrand + real org structure + manager-chain approval routing (client-driven)

**Approved:** Generic 3-role fixed approval hierarchy
(`L1_MANAGER` -> `L2_FINANCE` -> `L3_CFO`), demo/seed data for
development and grading, generic light-themed UI, login only against
pre-seeded accounts.

**Actual, at the client's (Psiog's) explicit request:**

- **Rebrand** - the frontend went through several iterations at the
  client's request (first Psiog's own teal/lime brand, then a
  notebook/journal aesthetic) before settling on its current look: a
  professional slate/navy + blue palette modeled on how real
  AI-driven expense/finance SaaS products (Brex, Ramp, Mercury,
  Expensify) are actually designed - independent of any single
  company's branding, per the client's final instruction to design
  it that way rather than reuse their brand colors.
- **Real self-service auth** - added `POST /auth/signup`; anyone can
  register as an `EMPLOYEE` and pick their own team/manager. Sign In
  and Sign Up pages replace the old login-only screen with a
  demo-account hint.
- **Org structure matches the real company** - introduced a `Team`
  entity seeded once (`backend/scripts/bootstrap_org.py`) with
  Psiog's actual 8 MAC teams (Arcturus, Hercules, Polaris, Andromeda,
  Vega, Sirius, Draco, Scorpius) and known client projects nested
  under them (GTF/Revlon/Stallion -> MAC3-Polaris, Finvi ->
  MAC2-Hercules), matching the org chart the client provided.
- **Approval routing rebuilt around the real manager chain** - the
  client described their actual Comp-Off approval process (Reporting
  Manager -> that manager's manager -> HR Department Head) as the
  model to follow; per their explicit clarification, this is **not**
  a separate Comp-Off feature but the same 3-level pattern applied to
  the existing Expense approval workflow. The old fixed
  `L1_MANAGER`/`L2_FINANCE`/`L3_CFO` roles are gone; `role` is now
  just `EMPLOYEE`/`HR_HEAD`/`CFO` (an RBAC role for admin actions
  only), and every expense routes through the requester's real
  `manager_id` chain (Reporting Manager -> Skip-Level Manager -> CFO,
  the fixed head of the chain) - see `app.workflow.manager_chain` and
  the Authentication & RBAC section of the root README.
- **Demo data removed** - `scripts/seed_demo_data.py` deleted;
  `scripts/wipe_data.py` (new) truncates every table; going forward
  all data enters the system the way it would in production - signup
  for employees, HR_HEAD-authenticated APIs for team/project/employee
  management - except the one unavoidable bootstrap step
  (`scripts/bootstrap_org.py`) that creates the first HR_HEAD account
  and the reference MAC/project data, since nothing else can create
  the very first privileged account.

**Impact:** This is a scope change, not a bug fix - flagged here per
the mid-term evaluator's feedback that undisclosed deviations are the
real problem, not deviations themselves. All 3 client screenshots
(company site, Comp-Off approval notification, org chart) that
motivated this are on file. Full backend test suite (104 tests) and
frontend lint/build were re-verified green after the change; see
`backend/tests/test_manager_chain.py` and the rewritten
`backend/tests/test_approval.py` for the new routing's coverage
(wrong-approver rejection, escalation-when-chain-incomplete, and
approver-identity server-resolution tests).

## 4. Database schema names differ from the approved proposal's Section 5.4

**Approved:** A schema with separate, single-purpose tables per the
proposal's exact naming: `expense_claims`, `ocr_extractions`,
`policy_violations`, `ai_risk_scores`, `workflow_audit_trails`,
`reimbursement_status`.

**Actual:** The implemented schema consolidates several of these into
denormalized tables with different names: `expenses` (not
`expense_claims`, and reimbursement state/history live as columns on
this table rather than a separate `reimbursement_status` table),
`expense_ai_analysis` (one row per receipt covering what the proposal
split across `ocr_extractions` + `ai_risk_scores`), `compliance_checks`
(not `policy_violations`), `expense_approvals` (not
`workflow_audit_trails`). `duplicate_checks` and `employees` match the
proposal's naming as-is.

**Why:** This was an engineering judgment call made while building the
AI pipeline, not a scope decision - `expenses` is deliberately the
denormalized read model the manager dashboard and Power BI feeds query
directly (see `database/DatabaseDesign.md`), so the pipeline's
per-receipt output, risk score, and reimbursement state are columns on
one row instead of joins across four tables for the common case. It
was not flagged as a deviation when it was built, and is being
disclosed now on discovering the mismatch against the approved
proposal's Section 5.4 during a full reconciliation pass.

**Impact:** None on functionality - the actual schema fully covers
every field the proposal's version would have (audit trail, risk
scores, policy reasons, reimbursement state), just organized
differently. `database/DatabaseDesign.md` is the source of truth for
the schema as actually built.

## 5. Robustness hardening added during this pass (not a deviation, a fix)

Neither the Gemini nor Ollama client had an explicit request timeout,
so a stalled network path could hang the entire pipeline indefinitely
- and because a hang never raises an exception, it silently defeated
the Hybrid Router's fallback-to-Ollama logic (which only triggers on
an exception). Added explicit timeouts to all three AI clients
(Gemini 30s, Groq 20s, Ollama 120s) so a stuck call fails fast and the
Hybrid Router's fallback actually engages the way the proposal
describes ("Hybrid Router auto-switches to Ollama - zero downtime").

## 6. Expense delete cascade bug (not a deviation, a fix)

`DELETE /expenses/{id}` failed with a 500 (`IntegrityError: null value
in column "expense_id" of relation "duplicate_checks" violates
not-null constraint`) for any expense that had gone through the full
AI pipeline. Root cause: on the `Expense` model, the `receipts` and
`approvals` relationships had `cascade="all, delete-orphan"`, but
`ai_reviews`, `duplicate_check`, and `compliance_check` did not - so
SQLAlchemy tried to disassociate those children by nulling out their
(NOT NULL) `expense_id` FK instead of deleting them. Fixed by adding
the same cascade to all three relationships in
`app/models/expense.py`, plus a migration
(`9853d1a62365_fix_expense_delete_cascade_and_.py`) adding
`ON DELETE SET NULL` to `duplicate_checks.matched_expense_id` (a
separate, nullable "matched a different expense" pointer that had no
DB-level ondelete behavior at all).

Verified live end-to-end, not just by reading the code: created a real
expense via the API, uploaded a real receipt through it (populating
all 4 previously-broken child tables via the actual pipeline, not
direct DB writes), confirmed all 4 rows existed, called
`DELETE /expenses/{id}`, got `204`, and confirmed all 4 child rows
plus the expense itself were gone with zero orphans left behind. Added
a permanent regression test
(`test_delete_expense_cascades_ai_pipeline_child_rows` in
`tests/test_expense.py`) that sets up the same 4 child rows and
asserts the cascade - the existing `test_delete_expense` never caught
this because it only ever deleted a bare expense with no children.

## 7. Local pytest was never actually able to run, this whole project (not a deviation, a fix)

The isolated-test-database design (`tests/conftest.py` redirecting to
a separate `expenseiq_test` database) assumed the app's Postgres user
had `CREATEDB`. It didn't, on this machine - `psycopg.OperationalError:
database "expenseiq_test" does not exist`, on every single local run,
for the entire project up to this point. CI was unaffected (its own
ephemeral Postgres container creates that database itself), so the
suite was genuinely green in the environment that actually gates
merges - but nobody could run it locally to develop against, and (see
below) it was masking two more real bugs.

**Fix:** isolation is now schema-based, not database-based.
`Settings.POSTGRES_SCHEMA` (new, optional, unset in every real
environment) pins a connection's `search_path` to a single schema via
a `-csearch_path=` libpq option on the connection string; conftest.py
sets it to a dedicated `pgtest` schema and drops/recreates that schema
fresh at the start of every session, inside whatever database
`POSTGRES_DATABASE` already points at. Creating a schema only needs
ordinary rights on a database the app user already owns - not the
CREATEDB/superuser-adjacent privilege a separate database needs - so
this works with zero admin access, locally or in CI.

Running the suite locally for the first time immediately surfaced two
real, previously-invisible problems it had been hiding:

- `tests/test_quality_validator.py` glob-scanned the app's real,
  gitignored `uploads/receipts/` upload directory for "known-good"
  sample images - fragile by construction, since that directory
  accumulates whatever anyone has actually uploaded through the
  running app, including a deliberately-poorly-cropped image from an
  earlier manual quality-validator demo. In CI that glob always
  matched zero files (a fresh checkout has no uploads directory at
  all), so `@pytest.mark.skipif` silently skipped all 6 of these
  tests there - meaning the Receipt Quality Validator had **never
  once actually run in CI**. Fixed by generating deterministic
  synthetic receipt images in a tmp dir instead of depending on
  ambient upload state - hermetic, and now genuinely exercised in CI
  for the first time. (Getting this synthetic image right also
  surfaced a real characteristic of the sharpness heuristic itself:
  Pillow's edge-detect filter leaves a thin unfiltered border around
  the whole image, and on a small canvas that border's contribution to
  the variance calculation is large enough to sit above the blur
  threshold regardless of actual blur - only at a realistic
  photo-sized resolution does the heuristic behave the way its own
  docstring describes. Documented inline in the test.)
- A schema that's only ever created-if-missing (rather than dropped
  and recreated) accumulates data across repeat local runs -
  `test_matching_merchant_amount_date_flags_duplicate` failed
  non-deterministically the first time this was tried, because the
  duplicate detector's fuzzy merchant-name matching (Python `difflib`,
  per the proposal's Novelty 2) matched an unrelated expense left over
  from an earlier run instead of the one the test had just created.
  Fixed by dropping the schema before recreating it every session.

Verified by running the full suite three consecutive times against a
freshly-dropped schema after the fix: **113/113 passing, deterministic
all three times**, plus a real, independently-measured coverage number
this project never had before - **91.7%** (`pytest --cov=app`),
against the proposal's own 85%+ target.
