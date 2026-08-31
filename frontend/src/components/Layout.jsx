import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useSession, ROLES } from '../context/session'
import BrandMark from './BrandMark'

const ALL_ROLES = ['EMPLOYEE', 'HR_HEAD', 'CFO']

const NAV_ITEMS = [
  { to: '/submit', label: 'Submit Expense', roles: ALL_ROLES },
  { to: '/my-expenses', label: 'My Expenses', roles: ALL_ROLES },
  { to: '/approvals', label: 'Approval Queue', roles: ALL_ROLES },
  { to: '/reimbursements', label: 'Reimbursements', roles: ['CFO'] },
  { to: '/teams', label: 'Teams & Projects', roles: ['HR_HEAD'] },
  { to: '/analytics', label: 'Analytics', roles: ALL_ROLES },
]

export default function Layout() {
  const { session, signOut } = useSession()
  const location = useLocation()

  const role = ROLES.find((r) => r.value === session?.role)

  const items = NAV_ITEMS.filter((item) =>
    item.roles.includes(session?.role),
  )

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 flex-col bg-primary-950">
        <div className="border-b border-white/10 px-5 py-5">
          <BrandMark dark />
          <p className="mt-1 text-xs text-white/50">
            ExpenseIQ - AI Expense Management
          </p>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-accent-600 text-white'
                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 px-4 py-4">
          <p className="text-xs font-medium text-white/40">Signed in as</p>
          <p className="truncate text-sm font-semibold text-white">
            {session?.name}
          </p>
          <p className="text-xs text-accent-400">{role?.label}</p>
          <button
            type="button"
            onClick={signOut}
            className="mt-3 w-full rounded-lg border border-white/20 px-3 py-1.5 text-xs font-medium text-white/80 hover:bg-white/10"
          >
            Sign Out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div
          key={location.pathname}
          className="route-fade mx-auto max-w-6xl px-6 py-8"
        >
          <Outlet />
        </div>
      </main>
    </div>
  )
}
