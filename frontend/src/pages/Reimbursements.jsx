import { useCallback, useEffect, useState } from 'react'
import { expensesApi } from '../api/resources'
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  Spinner,
} from '../components/ui'
import { ReimbursementBadge } from '../components/badges'

export default function Reimbursements() {
  const [expenses, setExpenses] = useState(null)
  const [error, setError] = useState(null)
  const [busyId, setBusyId] = useState(null)

  const load = useCallback(() => {
    expensesApi
      .list()
      .then((data) =>
        setExpenses(data.filter((e) => e.status === 'Approved')),
      )
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  async function markPaid(expense) {
    setBusyId(expense.id)
    setError(null)

    try {
      // processed_by is intentionally omitted - the backend takes
      // it from the JWT identity (CFO only).
      await expensesApi.updateReimbursement(expense.id, {
        reimbursement_state: 'PAID',
      })
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyId(null)
    }
  }

  const outstanding =
    expenses?.filter((e) => e.reimbursement_state === 'APPROVED') || []
  const paid = expenses?.filter((e) => e.reimbursement_state === 'PAID') || []

  return (
    <div>
      <h1 className="text-xl font-semibold text-slate-900">
        Reimbursement Tracker
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Approved claims move from APPROVED to PAID once finance settles
        them.
      </p>

      <ErrorBanner message={error} />

      {expenses === null ? (
        <Spinner />
      ) : expenses.length === 0 ? (
        <EmptyState
          title="Nothing approved yet"
          description="Once claims clear the approval workflow, they'll show up here."
        />
      ) : (
        <div className="mt-6 space-y-6">
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Outstanding ({outstanding.length})
            </h2>
            <Card className="mt-2 divide-y divide-slate-100">
              {outstanding.length === 0 ? (
                <p className="p-4 text-xs text-slate-400">
                  Nothing outstanding.
                </p>
              ) : (
                outstanding.map((expense) => (
                  <div
                    key={expense.id}
                    className="flex items-center justify-between p-4"
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-900">
                        {expense.expense_number} - {expense.merchant_name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {expense.currency}{' '}
                        {Number(expense.amount).toFixed(2)}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <ReimbursementBadge
                        state={expense.reimbursement_state}
                      />
                      <Button
                        disabled={busyId === expense.id}
                        onClick={() => markPaid(expense)}
                      >
                        Mark as Paid
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </Card>
          </section>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Paid ({paid.length})
            </h2>
            <Card className="mt-2 divide-y divide-slate-100">
              {paid.length === 0 ? (
                <p className="p-4 text-xs text-slate-400">
                  No payouts recorded yet.
                </p>
              ) : (
                paid.map((expense) => (
                  <div
                    key={expense.id}
                    className="flex items-center justify-between p-4"
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-900">
                        {expense.expense_number} - {expense.merchant_name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {expense.currency}{' '}
                        {Number(expense.amount).toFixed(2)} - paid by{' '}
                        {expense.reimbursement_processed_by}
                      </p>
                    </div>
                    <ReimbursementBadge state={expense.reimbursement_state} />
                  </div>
                ))
              )}
            </Card>
          </section>
        </div>
      )}
    </div>
  )
}
