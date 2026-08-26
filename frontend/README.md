# ExpenseIQ Frontend

React 19 + Vite + Tailwind CSS v4 + Recharts + React Router.

## What's here

- **Employee portal** (`/submit`, `/my-expenses`, `/expenses/:id`) -
  submit a claim, upload the receipt, watch the AI pipeline result
  (risk badges, duplicate alert, auto-approval recommendation) land
  live, and review the full approval audit trail per expense.
- **Manager dashboard** (`/approvals`) - role-scoped approval queue
  (L1 Manager / L2 Finance / L3 CFO) with AI risk badges and
  approve/reject actions that call the backend's routing-enforced
  approval API.
- **Reimbursement tracker** (`/reimbursements`, Finance/CFO roles) -
  mark approved claims as paid.
- **Analytics** (`/analytics`) - the same live feeds Power BI
  connects to (see `../docs/PowerBI_Setup_Guide.md`), rendered with
  Recharts: spend by category/employee, approval status summary,
  reimbursement liability, AI accuracy KPIs.

There's no real backend auth (out of scope for the proposal's demo);
`/login` is a lightweight role switcher backed by `localStorage`, not
a security boundary.

## Development

```bash
npm install
npm run dev      # http://127.0.0.1:5173, proxies /api -> http://127.0.0.1:8000
npm run lint
npm run build
```

Set `VITE_API_BASE_URL` (see `.env` / Render env vars) to point at a
non-local backend in production; it defaults to the relative
`/api/v1` path, which works with the dev proxy and with any
same-origin production deployment.
