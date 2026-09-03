# ExpenseIQ

AI-first, end-to-end Expense Management Application built for Impact
pSiddhi 3.0 (S2-C-08). Replaces manual receipt capture, policy
checking, and approval routing with an auditable AI pipeline:

```
Receipt Upload
   -> Tesseract OCR (raw text)
   -> Hybrid Router: Gemini 2.5-class vision (cloud) OR Ollama/LLaVA
      (on-device, forced for is_sensitive receipts; automatic
      fallback if the cloud call fails/times out)
   -> LangChain-style structured parsing (Pydantic-validated JSON)
   -> Duplicate Fraud Detector (fuzzy match vs. every other expense)
   -> Groq Cloud risk scoring (fraud_risk / compliance_risk /
      confidence + PASS/FAIL policy decision)
   -> Smart Auto-Approval Engine (AUTO_APPROVE / ESCALATE / REJECT
      + required approval level)
   -> 3-level manager-chain Approval Workflow (Reporting Manager ->
      Skip-Level Manager -> CFO, resolved from each requester's real
      org-chart position - see app.workflow.manager_chain)
   -> Reimbursement state machine (PENDING -> APPROVED -> PAID)
   -> Power BI / React analytics feeds
```

Org structure mirrors Psiog's actual MAC teams (Arcturus, Hercules,
Polaris, ...) with client projects nested under each one - see
`backend/scripts/bootstrap_org.py`.

## Repository layout

```
backend/    FastAPI + PostgreSQL + AI pipeline (see backend/README below)
frontend/   React + Tailwind + Recharts (employee portal + manager dashboard)
docs/       Deviation log, Power BI setup guide
docker-compose.yml   Local Postgres + backend + frontend stack
render.yaml           Render.com Blueprint for cloud deployment
.github/workflows/ci.yml   GitHub Actions - backend tests+coverage, frontend lint+build
```

## Quick start (local, no Docker)

```bash
# 1. Backend
cd backend
python -m venv .venv && .venv\Scripts\activate      # Windows
cp .env.example .env                                 # fill in Postgres creds + GEMINI_API_KEY + GROQ_API_KEY
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload                         # http://127.0.0.1:8000/docs

# 2. Frontend (new terminal)
cd frontend
npm install
npm run dev                                            # http://127.0.0.1:5173

# 3. One-time org setup (fresh database only)
cd backend
python scripts/wipe_data.py --yes      # only if re-running against old data
python scripts/bootstrap_org.py        # creates the 8 MAC teams + known
                                        # projects + one bootstrap HR_HEAD
                                        # (edit the HR_HEAD section at the
                                        # top of the script with real
                                        # details first)
```

From there, every other employee registers via `POST /auth/signup`
(or the frontend Sign Up page) and every other CFO/HR_HEAD account is
created by an existing HR_HEAD via `POST /employees/` - exactly as a
live deployment would, never by editing the database directly.

Ollama must be running locally (`ollama serve`, with the model in
`OLLAMA_MODEL` pulled, e.g. `ollama pull llava`) for the offline /
sensitive-receipt path and for the Gemini-failure fallback to work.

## Authentication & RBAC

JWT-based auth (`app/core/security.py`, bcrypt password hashing +
`python-jose`), with approval routing driven by each employee's real
org-chart position rather than a fixed role:

- `POST /api/v1/auth/signup` - public self-service registration.
  Always creates an `EMPLOYEE`-role account (there is no way to
  request a privileged role here); pick your MAC team and your
  Reporting Manager, and you're logged in immediately.
- `POST /api/v1/auth/login` - email + password -> bearer access
  token (default 60 min expiry, `JWT_EXPIRE_MINUTES`).
- `GET /api/v1/auth/me` - protected; resolves the token back to the
  authenticated employee (validates the token is live).
- Every `Employee` has a `role` (`EMPLOYEE` / `HR_HEAD` / `CFO`), an
  optional `manager_id` (their Reporting Manager - a real
  self-referential FK, not free text), a `team_id` (their MAC), and
  an optional `password` at creation - only employees created with a
  password can log in.
- **Approval routing** (`app.workflow.manager_chain`): every expense
  is approved by the requester's actual **Reporting Manager** (level
  1) -> their **Skip-Level Manager** (level 2) -> the **CFO** (level
  3, fixed). Any `EMPLOYEE` can be someone's approver just by being
  referenced as their `manager_id` - there's no "manager" role. If a
  requester (or their manager) has no manager on file, that level
  escalates straight to the CFO instead of erroring.
- **Protected routes**: `POST/PUT/DELETE /approvals/*` (any
  authenticated employee may call it, but `ApprovalService` checks
  the caller is the *exact* employee the chain resolves to for that
  specific expense - not just anyone with a broad role),
  `PATCH /expenses/{id}/reimbursement` (CFO only), and
  `POST/PUT/DELETE /employees/`, `/projects/`, `/teams/` (HR_HEAD
  only). The authenticated identity always overrides whatever
  approver_role/approver_name/processed_by/employee_id the request
  body contains, so a caller cannot forge an action as a role/person
  they aren't.
- Everything else (read endpoints, receipt upload, analytics,
  AI-analysis, compliance/duplicate checks) is intentionally left
  open in this pass.
- `scripts/bootstrap_org.py` provisions the one unavoidable
  chicken-and-egg account (the first HR_HEAD, since nothing else can
  create it) plus the real MAC teams/projects; every other account
  goes through `POST /auth/signup` or an HR_HEAD-authenticated
  `POST /employees/` from there on.

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env    # fill in API keys
docker compose up --build
# backend:  http://localhost:8000/docs
# frontend: http://localhost:3000
```

Ollama is **not** containerized (see comment in `docker-compose.yml`)
- it runs on the host and the backend container reaches it via
`host.docker.internal`.

## Testing & coverage

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

No setup step needed - tests isolate themselves inside a dedicated
`pgtest` Postgres *schema* (not a separate database) within whatever
`POSTGRES_DATABASE` your `.env` already points at, so pytest can never
write into real/dev data regardless of what that database is, and
never needs `CREATEDB`/superuser rights, only the ordinary `CREATE
SCHEMA` privilege an app user already has on a database it owns. The
schema is dropped and recreated fresh at the start of every run - see
`tests/conftest.py`.

Tests that require live Gemini/Groq keys or a local Ollama runtime
are skipped automatically in CI (`CI=true`, set by GitHub Actions) -
see `tests/test_ai_pipeline.py` / `tests/test_receipt.py`. Everything
else (all CRUD, the 3-level approval workflow, the duplicate
detector, the auto-approval engine, reimbursement state machine, and
every analytics endpoint) runs fully mocked/DB-backed in CI.

## Key docs

- [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md) - every deviation from
  the approved proposal, disclosed with reasoning (two AI model
  swaps forced by upstream retirements).
- [`docs/PowerBI_Setup_Guide.md`](docs/PowerBI_Setup_Guide.md) - wiring
  Power BI Desktop to the `/api/v1/analytics/*` feeds for the 4
  required dashboard views.
- `backend/scripts/bootstrap_org.py` - one-time setup for a fresh
  database: creates the 8 real MAC teams, the known client projects,
  and the first HR_HEAD account (edit the placeholder details at the
  top of the script before running against real data).
- `backend/scripts/wipe_data.py` - `TRUNCATE`s every table (requires
  `--yes`); use before re-running `bootstrap_org.py` against a
  database that already has data in it.

## Author

Pravin Shanmugavel (P476) - Impact pSiddhi 3.0, Semester 2, Custom
Track (S2-C-08).
