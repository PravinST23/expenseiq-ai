import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/resources'
import { useSession } from '../context/session'
import {
  Button,
  Card,
  ErrorBanner,
  Field,
  inputClass,
} from '../components/ui'

const HOME_BY_ROLE = {
  EMPLOYEE: '/submit',
  L1_MANAGER: '/approvals',
  L2_FINANCE: '/approvals',
  L3_CFO: '/approvals',
}

export default function Login() {
  const { signIn } = useSession()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const result = await authApi.login(email, password)

      signIn({
        token: result.access_token,
        expiresAt: result.expires_at,
        role: result.role,
        employeeId: result.employee_id,
        employeeCode: result.employee_code,
        name: result.full_name,
      })

      navigate(HOME_BY_ROLE[result.role] || '/submit')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-sm font-bold text-white">
            IQ
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-900">
              ExpenseIQ
            </h1>
            <p className="text-xs text-slate-500">
              AI-First Expense Management
            </p>
          </div>
        </div>

        <ErrorBanner message={error} />

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <Field label="Email">
            <input
              type="email"
              autoComplete="username"
              className={inputClass}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </Field>

          <Field label="Password">
            <input
              type="password"
              autoComplete="current-password"
              className={inputClass}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>

          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>

        <div className="mt-6 rounded-lg bg-slate-50 p-3 text-xs text-slate-500 ring-1 ring-inset ring-slate-200">
          <p className="font-medium text-slate-600">
            Demo accounts (run scripts/seed_demo_data.py first)
          </p>
          <p className="mt-1">
            Any seeded email · password <code>Demo@12345</code>
          </p>
          <ul className="mt-1 space-y-0.5">
            <li>ananya.sharma@psiog.demo - Employee</li>
            <li>karthik.iyer@psiog.demo - L1 Manager</li>
            <li>fatima.khan@psiog.demo - L2 Finance</li>
            <li>meera.krishnan@psiog.demo - L3 CFO</li>
          </ul>
        </div>
      </Card>
    </div>
  )
}
