import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSession } from '../context/session'
import { approvalsApi, expensesApi } from '../api/resources'
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  Spinner,
} from '../components/ui'
import {
  DuplicateBadge,
  RecommendationBadge,
  RiskBadge,
} from '../components/badges'

export default function ApprovalQueue() {
  const { session } = useSession()

  const [expenses, setExpenses] = useState(null)
  const [error, setError] = useState(null)
  const [busyId, setBusyId] = useState(null)
  const [comments, setComments] = useState({})

  const load = useCallback(() => {
    // Resolved server-side per-requester via the manager chain
    // (Reporting Manager -> Skip-Level Manager -> CFO) - not by a
    // fixed role, since any employee can be someone's manager.
    expensesApi
      .pendingForMe()
      .then(setExpenses)
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  async function act(expense, action) {
    setBusyId(expense.id)
    setError(null)

    try {
      // approver_role/approver_name are intentionally omitted - the
      // backend derives them from the JWT (see require_roles on the
      // /approvals route), never from the request body.
      await approvalsApi.create({
        expense_id: expense.id,
        action,
        comments: comments[expense.id] || `${action} by ${session.name}`,
      })

      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div>
      <h1 className="text-xl font-semibold text-slate-900">
        Approval Queue
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Claims currently routed to you, with the Smart Auto-Approval
        Engine's recommendation and full AI risk score.
      </p>

      <ErrorBanner message={error} />

      {expenses === null ? (
        <Spinner />
      ) : expenses.length === 0 ? (
        <EmptyState
          title="Queue is clear"
          description="Nothing is currently awaiting your action."
        />
      ) : (
        <div className="mt-6 space-y-4">
          {expenses.map((expense) => (
            <Card key={expense.id} className="p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    {expense.expense_number} - {expense.merchant_name}
                  </p>
                  <p className="text-xs text-slate-500">
                    {expense.expense_category} - {expense.currency}{' '}
                    {Number(expense.amount).toFixed(2)} on{' '}
                    {expense.expense_date}
                  </p>
                  <Link
                    to={`/expenses/${expense.id}`}
                    className="mt-1 inline-block text-xs font-medium text-slate-500 hover:text-slate-900"
                  >
                    View full detail →
                  </Link>
                </div>
                <RecommendationBadge
                  recommendation={expense.ai_recommendation}
                />
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                <RiskBadge
                  label="Fraud Risk"
                  score={expense.fraud_risk_score}
                />
                <RiskBadge
                  label="Compliance Risk"
                  score={expense.compliance_risk_score}
                />
                <RiskBadge
                  label="AI Confidence"
                  score={expense.ai_confidence_score}
                />
                <DuplicateBadge isDuplicate={expense.is_duplicate} />
              </div>

              <div className="mt-4 flex items-center gap-2">
                <input
                  className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
                  placeholder="Comments (optional)"
                  value={comments[expense.id] || ''}
                  onChange={(e) =>
                    setComments((c) => ({
                      ...c,
                      [expense.id]: e.target.value,
                    }))
                  }
                />
                <Button
                  variant="success"
                  disabled={busyId === expense.id}
                  onClick={() => act(expense, 'Approved')}
                >
                  Approve
                </Button>
                <Button
                  variant="danger"
                  disabled={busyId === expense.id}
                  onClick={() => act(expense, 'Rejected')}
                >
                  Reject
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
