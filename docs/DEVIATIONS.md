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
