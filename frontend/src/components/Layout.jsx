import { NavLink, Outlet } from 'react-router-dom'
import { useSession, ROLES } from '../context/session'

const NAV_ITEMS = [
  { to: '/submit', label: 'Submit Expense', roles: ['EMPLOYEE'] },
  { to: '/my-expenses', label: 'My Expenses', roles: ['EMPLOYEE'] },
  {
    to: '/approvals',
    label: 'Approval Queue',
    roles: ['L1_MANAGER', 'L2_FINANCE', 'L3_CFO'],
  },
  {
    to: '/reimbursements',
    label: 'Reimbursements',
    roles: ['L2_FINANCE', 'L3_CFO'],
  },
  {
    to: '/analytics',
    label: 'Analytics',
    roles: ['EMPLOYEE', 'L1_MANAGER', 'L2_FINANCE', 'L3_CFO'],
  },
]

export default function Layout() {
  const { session, signOut } = useSession()

  const role = ROLES.find((r) => r.value === session?.role)

  const items = NAV_ITEMS.filter((item) =>
    item.roles.includes(session?.role),
  )

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 flex-col border-r border-slate-200 bg-white">
        <div className="flex items-center gap-2 border-b border-slate-200 px-5 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-sm font-bold text-white">
            IQ
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">
              ExpenseIQ
            </p>
            <p className="text-xs text-slate-400">
              AI Expense Management
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-200 px-4 py-4">
          <p className="text-xs font-medium text-slate-500">
            Signed in as
          </p>
          <p className="truncate text-sm font-semibold text-slate-900">
            {session?.name}
          </p>
          <p className="text-xs text-slate-400">{role?.label}</p>
          <button
            type="button"
            onClick={signOut}
            className="mt-3 w-full rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            Switch Role
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
