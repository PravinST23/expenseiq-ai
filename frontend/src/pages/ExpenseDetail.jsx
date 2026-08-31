import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  aiAnalysisApi,
  approvalsApi,
  duplicateChecksApi,
  expensesApi,
} from '../api/resources'
import { Card, ErrorBanner, Spinner } from '../components/ui'
import {
  DuplicateBadge,
  EngineBadge,
  RecommendationBadge,
  ReimbursementBadge,
  RiskBadge,
  StatusBadge,
} from '../components/badges'

export default function ExpenseDetail() {
  const { id } = useParams()

  const [expense, setExpense] = useState(null)
  const [analyses, setAnalyses] = useState([])
  const [approvals, setApprovals] = useState([])
  const [duplicate, setDuplicate] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      expensesApi.get(id),
      aiAnalysisApi.byExpense(id),
      approvalsApi.byExpense(id),
      duplicateChecksApi.byExpense(id),
    ])
      .then(([exp, ai, approvalHistory, dup]) => {
        setExpense(exp)
        setAnalyses(ai)
        setApprovals(approvalHistory)
        setDuplicate(dup)
      })
      .catch((err) => setError(err.message))
  }, [id])

  if (error) return <ErrorBanner message={error} />
  if (!expense) return <Spinner />

  const analysis = analyses[0]

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        to="/my-expenses"
        className="text-xs font-medium text-slate-500 hover:text-slate-900"
      >
        ← Back to My Expenses
      </Link>

      <div className="mt-3 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">
            {expense.expense_number} - {expense.merchant_name}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {expense.expense_category} - {expense.currency}{' '}
            {Number(expense.amount).toFixed(2)} on {expense.expense_date}
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <StatusBadge status={expense.status} />
          <ReimbursementBadge state={expense.reimbursement_state} />
        </div>
      </div>

      <Card className="mt-6 p-6">
        <h2 className="text-sm font-semibold text-slate-900">
          AI Pipeline Result
        </h2>

        <div className="mt-3 flex flex-wrap gap-2">
          <RecommendationBadge recommendation={expense.ai_recommendation} />
          <DuplicateBadge isDuplicate={expense.is_duplicate} />
          <EngineBadge engine={expense.processing_engine} />
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <RiskBadge label="Fraud Risk" score={expense.fraud_risk_score} />
          <RiskBadge
            label="Compliance Risk"
            score={expense.compliance_risk_score}
          />
          <RiskBadge
            label="AI Confidence"
            score={expense.ai_confidence_score}
          />
        </div>

        {analysis ? (
          <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-slate-600">
            <p>
              <span className="font-medium text-slate-900">
                Policy status:
              </span>{' '}
              {analysis.policy_status}
            </p>
            <p>
              <span className="font-medium text-slate-900">
                Requires manager approval:
              </span>{' '}
              {String(analysis.requires_manager_approval)}
            </p>
            <p className="col-span-2">
              <span className="font-medium text-slate-900">
                Policy reason:
              </span>{' '}
              {analysis.policy_reason}
            </p>
            {analysis.risk_reason ? (
              <p className="col-span-2">
                <span className="font-medium text-slate-900">
                  Auto-approval rationale:
                </span>{' '}
                {analysis.risk_reason}
              </p>
            ) : null}
          </div>
        ) : (
          <p className="mt-4 text-xs text-slate-400">
            No AI analysis yet - upload a receipt to run the pipeline.
          </p>
        )}

        {duplicate?.duplicate_found ? (
          <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 ring-1 ring-inset ring-red-600/20">
            Matched fields: {duplicate.match_fields} (confidence{' '}
            {Number(duplicate.confidence_score).toFixed(0)}%)
          </div>
        ) : null}
      </Card>

      <Card className="mt-6 p-6">
        <h2 className="text-sm font-semibold text-slate-900">
          Approval Audit Trail
        </h2>

        {approvals.length === 0 ? (
          <p className="mt-3 text-xs text-slate-400">
            No approval actions recorded yet.
          </p>
        ) : (
          <ul className="mt-3 space-y-3">
            {approvals.map((a) => (
              <li
                key={a.id}
                className="flex items-start justify-between border-b border-slate-100 pb-3 last:border-0 last:pb-0"
              >
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    {a.approver_role} - {a.approver_name}
                  </p>
                  <p className="text-xs text-slate-500">{a.comments}</p>
                </div>
                <div className="text-right">
                  <p
                    className={`text-xs font-semibold ${
                      a.action === 'Approved'
                        ? 'text-emerald-600'
                        : 'text-red-600'
                    }`}
                  >
                    {a.action}
                  </p>
                  <p className="text-xs text-slate-400">
                    {new Date(a.approved_at).toLocaleString()}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}
