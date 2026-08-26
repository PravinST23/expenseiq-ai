# ExpenseIQ Database Design

## Version

2.0.0

---

# Overview

ExpenseIQ is an AI-powered Expense Management Platform. The database
is a normalized relational model on PostgreSQL, managed via
SQLAlchemy models + Alembic migrations (`backend/alembic/versions/`).

Supports:

- Expense Management
- Receipt Upload + OCR + Multimodal AI Extraction
- Hybrid Routing (Gemini cloud / Ollama offline)
- Duplicate Fraud Detection
- AI Risk Scoring & Compliance Validation
- Smart Auto-Approval Recommendations
- 3-Level Approval Workflow (L1 Manager / L2 Finance / L3 CFO)
- Reimbursement State Tracking (PENDING / APPROVED / PAID)
- Analytics / Power BI reporting feeds

---

# Database Entities

1. Employee
2. Project
3. Expense
4. Receipt
5. ExpenseApproval
6. AIAnalysis (`expense_ai_analysis`)
7. ComplianceCheck
8. DuplicateCheck

---

# Entity Relationship

```
Employee ──< Expense >── Project
              │
              ├──< Receipt
              │       │
              │       └──< AIAnalysis (per receipt)
              │
              ├──< ExpenseApproval (audit trail, 1 row per action)
              │
              ├── ComplianceCheck (1:1)
              │
              └── DuplicateCheck (1:1, optionally -> matched Expense)
```

---

# Employee

Columns: `id`, `employee_code`, `full_name`, `email`, `phone_number`,
`department`, `designation`, `manager_name`, `employee_status`,
`is_active`, `policy_tier`, `role`, `hashed_password`, `created_at`,
`updated_at`

`role` is one of `EMPLOYEE` / `L1_MANAGER` / `L2_FINANCE` / `L3_CFO` -
the approval routing role, and the RBAC role checked by
`app.api.deps.require_roles` on protected endpoints. `hashed_password`
(bcrypt, nullable) is only set for employees created with a password
and never leaves the server - `EmployeeResponse` exposes a
`has_password` boolean instead. See the Authentication & RBAC section
of the root README.

`policy_tier` feeds future spend-limit differentiation (STANDARD by
default); currently used as a reserved extension point.

---

# Project

Columns: `id`, `project_code`, `project_name`, `client_name`,
`project_description`, `start_date`, `end_date`, `project_manager`,
`project_budget`, `project_status`, `is_active`, `created_at`,
`updated_at`

---

# Expense

The master claim record - also the **denormalized read model** for
the AI pipeline's output and the approval/reimbursement state
machine, so the manager dashboard and Power BI feeds never need to
join across 4 tables for the common case.

Columns:

- `id`, `expense_number`, `employee_id` (FK), `project_id` (FK)
- `expense_category`, `merchant_name`, `amount`, `currency`,
  `expense_date`, `payment_method`, `description`
- `status` - workflow status string (`Pending L1 Manager Approval`,
  `Approved`, `Rejected`, ...)
- `is_sensitive` - drives the Hybrid Router (Ollama-only when true)
- `processing_engine` - `gemini` or `ollama`, whichever actually
  processed the latest receipt
- `fraud_risk_score`, `compliance_risk_score`, `ai_confidence_score` -
  latest Groq risk scores (0-100)
- `is_duplicate` - latest Duplicate Fraud Detector result
- `ai_recommendation` - `AUTO_APPROVE_RECOMMENDED` /
  `ESCALATE_FOR_REVIEW` / `REJECT_RECOMMENDED`
- `current_approval_level`, `required_approval_level` - 1/2/3,
  computed by the Smart Auto-Approval Engine, consumed by the
  approval workflow to route/gate actions
- `reimbursement_state` - `PENDING` / `APPROVED` / `PAID`
- `reimbursement_updated_at`, `reimbursement_processed_by`

---

# Receipt

Columns: `id`, `receipt_number`, `expense_id` (FK), `original_filename`,
`stored_filename`, `file_path`, `file_type`, `file_size`,
`upload_status`, `ocr_text`, `ocr_status`, `ocr_processed_at`,
`ai_status`, `extracted_json`

---

# ExpenseApproval

Immutable audit trail - one row per approval **action** taken (not
per routing stage).

Columns: `id`, `expense_id` (FK), `approver_role`
(`L1_MANAGER` / `L2_FINANCE` / `L3_CFO`), `approval_level` (1/2/3,
derived from role), `approver_name`, `action` (`Approved` /
`Rejected`), `comments`, `approved_at`

A system auto-approval (Smart Auto-Approval Engine, low risk +
`required_approval_level == 1`) is recorded here too, with
`approver_role = 'SYSTEM'`.

---

# AIAnalysis (`expense_ai_analysis`)

One row per receipt processed - the full AI pipeline output,
including OCR ground-truth text for QA comparison.

Columns: `id`, `expense_id` (FK), `receipt_id` (FK), extracted
receipt fields (`merchant_name`, `expense_date`, `expense_category`,
`total_amount`, `currency`, `payment_method`), `ocr_text`,
`extracted_json`, `policy_status`, `policy_reason`,
`requires_manager_approval`, `approval_recommendation`, `ai_provider`,
`ocr_provider`, `policy_provider`, `pipeline_version`,
`confidence_score`, `fraud_score`, `duplicate_score`, `quality_score`,
`compliance_risk_score`, `risk_reason`, `required_approval_level`,
`processed_at`

---

# ComplianceCheck

1:1 with Expense - latest Groq policy decision (kept separate from
`AIAnalysis` since it's queried standalone by finance/compliance
views).

Columns: `id`, `expense_id` (FK, unique), `policy_status`,
`policy_reason`, `ai_model`

---

# DuplicateCheck

1:1 with Expense - latest Duplicate Fraud Detector result.

Columns: `id`, `expense_id` (FK, unique), `duplicate_found`,
`confidence_score`, `matched_expense_id` (FK -> Expense, nullable),
`match_fields` (comma-separated: `merchant_name,amount,expense_date,
invoice_number`)

---

# Database Standards

- Primary Keys: UUID (`uuid4`)
- Foreign Keys: UUID
- Naming Convention: `snake_case`, plural table names
- Audit Columns: `created_at`, `updated_at` on every table
  (`BaseModel`)
- Migrations: Alembic, one revision per schema change -
  `backend/alembic/versions/`
