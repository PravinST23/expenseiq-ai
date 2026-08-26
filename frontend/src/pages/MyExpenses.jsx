import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSession } from '../context/session'
import { expensesApi } from '../api/resources'
import { Card, EmptyState, ErrorBanner, Spinner } from '../components/ui'
import {
  DuplicateBadge,
  RecommendationBadge,
  ReimbursementBadge,
  StatusBadge,
} from '../components/badges'

export default function MyExpenses() {
  const { session } = useSession()
  const [expenses, setExpenses] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    expensesApi
      .list()
      .then((data) =>
        setExpenses(
          data
            .filter((e) => e.employee_id === session.employeeId)
            .sort((a, b) => (a.expense_number < b.expense_number ? 1 : -1)),
        ),
      )
      .catch((err) => setError(err.message))
  }, [session.employeeId])

  return (
    <div>
      <h1 className="text-xl font-semibold text-slate-900">My Expenses</h1>
      <p className="mt-1 text-sm text-slate-500">
        Everything you have submitted, with live AI risk scoring and
        approval status.
      </p>

      <ErrorBanner message={error} />

      {expenses === null ? (
        <Spinner />
      ) : expenses.length === 0 ? (
        <EmptyState
          title="No expenses yet"
          description="Submit your first expense to see it tracked here."
        />
      ) : (
        <Card className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs font-medium uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Expense</th>
                <th className="px-4 py-3">Merchant</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">AI Recommendation</th>
                <th className="px-4 py-3">Reimbursement</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {expenses.map((expense) => (
                <tr key={expense.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {expense.expense_number}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {expense.merchant_name}
                    {expense.is_duplicate ? (
                      <span className="ml-2">
                        <DuplicateBadge isDuplicate />
                      </span>
                    ) : null}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {expense.currency} {Number(expense.amount).toFixed(2)}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={expense.status} />
                  </td>
                  <td className="px-4 py-3">
                    <RecommendationBadge
                      recommendation={expense.ai_recommendation}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <ReimbursementBadge
                      state={expense.reimbursement_state}
                    />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/expenses/${expense.id}`}
                      className="text-xs font-medium text-slate-500 hover:text-slate-900"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
