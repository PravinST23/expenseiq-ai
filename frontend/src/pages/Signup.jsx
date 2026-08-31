import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi, employeesApi, teamsApi } from '../api/resources'
import { useSession } from '../context/session'
import {
  Button,
  Card,
  ErrorBanner,
  Field,
  inputClass,
  Spinner,
} from '../components/ui'
import BrandMark from '../components/BrandMark'

export default function Signup() {
  const { signIn } = useSession()
  const navigate = useNavigate()

  const [teams, setTeams] = useState(null)
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    phone_number: '',
    department: '',
    designation: '',
    team_id: '',
    manager_id: '',
  })

  useEffect(() => {
    Promise.all([teamsApi.list(), employeesApi.list()])
      .then(([teamList, employeeList]) => {
        setTeams(teamList)
        setEmployees(employeeList)
        if (teamList.length) {
          setForm((f) => ({ ...f, team_id: teamList[0].id }))
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const result = await authApi.signup({
        ...form,
        manager_id: form.manager_id || null,
      })

      signIn({
        token: result.access_token,
        expiresAt: result.expires_at,
        role: result.role,
        employeeId: result.employee_id,
        employeeCode: result.employee_code,
        name: result.full_name,
      })

      navigate('/submit')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-primary-950 px-4 py-10">
      <Card className="w-full max-w-lg p-8">
        <div className="mb-6">
          <BrandMark size="lg" />
          <p className="mt-2 text-xs text-slate-500">
            Create your ExpenseIQ account
          </p>
        </div>

        <ErrorBanner message={error} />

        {loading ? (
          <Spinner label="Loading teams..." />
        ) : (
          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Field label="Full Name">
                <input
                  className={inputClass}
                  value={form.full_name}
                  onChange={(e) => update('full_name', e.target.value)}
                  required
                />
              </Field>

              <Field label="Email">
                <input
                  type="email"
                  autoComplete="username"
                  className={inputClass}
                  value={form.email}
                  onChange={(e) => update('email', e.target.value)}
                  required
                />
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Field label="Password">
                <input
                  type="password"
                  autoComplete="new-password"
                  className={inputClass}
                  value={form.password}
                  onChange={(e) => update('password', e.target.value)}
                  minLength={6}
                  required
                />
              </Field>

              <Field label="Phone Number (optional)">
                <input
                  className={inputClass}
                  value={form.phone_number}
                  onChange={(e) => update('phone_number', e.target.value)}
                />
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Field label="Department">
                <input
                  className={inputClass}
                  value={form.department}
                  onChange={(e) => update('department', e.target.value)}
                  required
                />
              </Field>

              <Field label="Designation">
                <input
                  className={inputClass}
                  value={form.designation}
                  onChange={(e) => update('designation', e.target.value)}
                  required
                />
              </Field>
            </div>

            <Field
              label="MAC Team"
              hint={
                teams.length === 0
                  ? 'No teams set up yet - ask HR to create one first.'
                  : undefined
              }
            >
              <select
                className={inputClass}
                value={form.team_id}
                onChange={(e) => update('team_id', e.target.value)}
                required
              >
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.team_code} - {team.team_name}
                  </option>
                ))}
              </select>
            </Field>

            <Field
              label="Reporting Manager (optional)"
              hint="Drives your expense approval routing."
            >
              <select
                className={inputClass}
                value={form.manager_id}
                onChange={(e) => update('manager_id', e.target.value)}
              >
                <option value="">No manager / top of chain</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.full_name} - {emp.designation}
                  </option>
                ))}
              </select>
            </Field>

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>
        )}

        <p className="mt-5 text-center text-xs text-slate-500">
          Already have an account?{' '}
          <Link
            to="/login"
            className="font-semibold text-accent-700 hover:underline"
          >
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  )
}
