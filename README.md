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
   -> 3-level Approval Workflow (L1 Manager -> L2 Finance -> L3 CFO)
   -> Reimbursement state machine (PENDING -> APPROVED -> PAID)
   -> Power BI / React analytics feeds
```

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

# 3. (Optional) seed demo data - creates employees/projects and runs
#    every receipt already in backend/uploads/receipts/ through the
#    full AI pipeline
cd backend
python scripts/seed_demo_data.py
```

Ollama must be running locally (`ollama serve`, with the model in
`OLLAMA_MODEL` pulled, e.g. `ollama pull llava`) for the offline /
sensitive-receipt path and for the Gemini-failure fallback to work.

## Authentication & RBAC

JWT-based auth (`app/core/security.py`, bcrypt password hashing +
`python-jose`):

- `POST /api/v1/auth/login` - email + password -> bearer access
  token (default 60 min expiry, `JWT_EXPIRE_MINUTES`).
- `GET /api/v1/auth/me` - protected; resolves the token back to the
  authenticated employee (validates the token is live).
- Every `Employee` has a `role` (`EMPLOYEE` / `L1_MANAGER` /
  `L2_FINANCE` / `L3_CFO`) and an optional `password` at creation
  (`POST /api/v1/employees/`) - only employees created with a
  password can log in.
- **Protected routes**: `POST/PUT/DELETE /approvals/*` (any
  L1/L2/L3 role) and `PATCH /expenses/{id}/reimbursement`
  (L2_FINANCE/L3_CFO only) - see `app.api.deps.require_roles`. The
  authenticated identity always overrides whatever
  approver_role/approver_name/processed_by the request body
  contains, so a caller cannot forge an approval or reimbursement
  action as a role/person they aren't.
- Everything else (employee/project/expense/receipt CRUD, analytics,
  AI-analysis, compliance/duplicate checks) is intentionally left
  open in this pass - the approval and reimbursement workflows are
  where identity/role integrity actually matters for the audit
  trail; broader protection is a natural next step.
- `scripts/seed_demo_data.py` provisions one login-ready account per
  role - see the Login page's demo-accounts hint or the script's
  `EMPLOYEES` list (shared password `Demo@12345`).

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
- `backend/scripts/seed_demo_data.py` - generates the RFP's minimum
  coverage evidence set (20+ receipts across 5 categories, 5+ Ollama
  offline runs, 3-role approval routing, reimbursement states across
  PENDING/APPROVED/PAID) from the real receipt images already in
  `backend/uploads/receipts/`.

## Author

Pravin Shanmugavel (P476) - Impact pSiddhi 3.0, Semester 2, Custom
Track (S2-C-08).
