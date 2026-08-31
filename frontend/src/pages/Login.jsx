import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/resources'
import { useSession } from '../context/session'
import {
  Button,
  Card,
  ErrorBanner,
  Field,
  inputClass,
} from '../components/ui'
import BrandMark from '../components/BrandMark'

const HOME_BY_ROLE = {
  EMPLOYEE: '/submit',
  HR_HEAD: '/approvals',
  CFO: '/approvals',
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
    <div className="flex min-h-screen items-center justify-center bg-primary-950 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="mb-6">
          <BrandMark size="lg" />
          <p className="mt-2 text-xs text-slate-500">
            AI-First Expense Management
          </p>
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

        <p className="mt-5 text-center text-xs text-slate-500">
          New here?{' '}
          <Link
            to="/signup"
            className="font-semibold text-accent-700 hover:underline"
          >
            Create an account
          </Link>
        </p>
      </Card>
    </div>
  )
}
