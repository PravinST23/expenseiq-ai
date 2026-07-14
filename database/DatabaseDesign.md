# ExpenseIQ Database Design

## Version

1.0.0

---

# Overview

ExpenseIQ is an AI-powered Expense Management Platform.

The database is designed using a normalized relational model with PostgreSQL.

The design supports:

- Expense Management
- Receipt Upload
- OCR Processing
- AI Data Extraction
- Duplicate Detection
- Compliance Validation
- Approval Workflow
- Reporting

---

# Database Entities

1. Employee
2. Project
3. Expense
4. Receipt
5. DuplicateCheck
6. ComplianceCheck

---

# Entity Relationship

Employee
│
├──< Expense >── Project
│
│
├── Receipt
│
├── DuplicateCheck
│
└── ComplianceCheck

---

# Employee

Stores employee master information.

Columns

- id (UUID)
- employee_code
- full_name
- email
- department
- designation
- is_active
- created_at
- updated_at

Primary Key

id

---

# Project

Stores project information.

Columns

- id
- project_code
- project_name
- client_name
- is_active
- created_at
- updated_at

Primary Key

id

---

# Expense

Stores employee expense claims.

Columns

- id
- employee_id
- project_id
- category
- amount
- currency
- expense_date
- merchant_name
- description
- status
- created_at
- updated_at

Primary Key

id

Foreign Keys

employee_id → Employee.id

project_id → Project.id

---

# Receipt

Stores uploaded receipt information.

Columns

- id
- expense_id
- file_name
- file_path
- mime_type
- uploaded_at

Primary Key

id

Foreign Key

expense_id → Expense.id

---

# DuplicateCheck

Stores duplicate detection results.

Columns

- id
- expense_id
- duplicate_found
- matched_expense_id
- confidence_score
- created_at

Primary Key

id

Foreign Key

expense_id → Expense.id

---

# ComplianceCheck

Stores AI policy validation.

Columns

- id
- expense_id
- policy_status
- policy_reason
- ai_model
- checked_at

Primary Key

id

Foreign Key

expense_id → Expense.id

---

# Relationships

Employee

One Employee

↓

Many Expenses

Project

One Project

↓

Many Expenses

Expense

One Expense

↓

One Receipt

Expense

One Expense

↓

One DuplicateCheck

Expense

One Expense

↓

One ComplianceCheck

---

# Future Tables

The following tables will be introduced in later sprints.

Approval

ApprovalHistory

Roles

Users

Notifications

AuditLogs

OCRResults

AIExtraction

PolicyRules

---

# Database Standards

Primary Keys

UUID

Foreign Keys

UUID

Naming Convention

snake_case

Table Naming

Plural

Examples

employees

expenses

projects

receipts

Indexes

Primary Keys

Unique Constraints

Employee Code

Email

Project Code

Audit Columns

created_at

updated_at

Soft Delete

Will be implemented in a later sprint if required.