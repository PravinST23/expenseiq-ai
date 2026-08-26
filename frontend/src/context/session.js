import { createContext, useContext } from 'react'

export const SessionContext = createContext(null)

export const ROLES = [
  { value: 'EMPLOYEE', label: 'Employee', level: null },
  { value: 'L1_MANAGER', label: 'L1 Manager', level: 1 },
  { value: 'L2_FINANCE', label: 'L2 Finance', level: 2 },
  { value: 'L3_CFO', label: 'L3 CFO', level: 3 },
]

export const SESSION_STORAGE_KEY = 'expenseiq.session'

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) {
    throw new Error('useSession must be used inside a SessionProvider')
  }
  return ctx
}
