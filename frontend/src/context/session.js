import { createContext, useContext } from 'react'

export const SessionContext = createContext(null)

// Mirrors the backend's Employee.role values - see
// app/schemas/employee.py EmployeeRole and
// app/workflow/manager_chain.py. There is no fixed "level" per role
// anymore: approval routing resolves Reporting Manager / Skip-Level
// Manager dynamically from each employee's manager_id chain: any
// EMPLOYEE can be someone's approver just by being their manager.
// CFO is the fixed final approver for every expense chain.
export const ROLES = [
  { value: 'EMPLOYEE', label: 'Employee' },
  { value: 'HR_HEAD', label: 'HR Head' },
  { value: 'CFO', label: 'CFO' },
]

export const SESSION_STORAGE_KEY = 'expenseiq.session'

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) {
    throw new Error('useSession must be used inside a SessionProvider')
  }
  return ctx
}
