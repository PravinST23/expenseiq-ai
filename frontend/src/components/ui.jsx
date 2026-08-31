import { STATUS } from '../theme'

const STATUS_STYLES = {
  good: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  warning: 'bg-amber-50 text-amber-800 ring-amber-600/20',
  serious: 'bg-orange-50 text-orange-800 ring-orange-600/20',
  critical: 'bg-red-50 text-red-700 ring-red-600/20',
  neutral: 'bg-slate-100 text-slate-700 ring-slate-600/10',
}

export function Badge({ tone = 'neutral', icon, children }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${STATUS_STYLES[tone]}`}
    >
      {icon ? <span aria-hidden="true">{icon}</span> : null}
      {children}
    </span>
  )
}

export function Dot({ tone = 'neutral' }) {
  const color =
    tone === 'neutral' ? '#94a3b8' : STATUS[tone] || STATUS.warning
  return (
    <span
      className="inline-block h-2 w-2 rounded-full"
      style={{ backgroundColor: color }}
    />
  )
}

export function Card({ className = '', children }) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
    >
      {children}
    </div>
  )
}

export function StatCard({ label, value, sub, tone = 'neutral' }) {
  return (
    <Card className="p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
      {sub ? (
        <p
          className="mt-1 text-xs font-medium"
          style={{
            color: tone === 'neutral' ? '#64748b' : STATUS[tone],
          }}
        >
          {sub}
        </p>
      ) : null}
    </Card>
  )
}

export function Button({
  variant = 'primary',
  className = '',
  children,
  ...props
}) {
  const variants = {
    primary:
      'bg-accent-600 text-white hover:bg-accent-700 disabled:bg-slate-200 disabled:text-slate-400',
    dark:
      'bg-primary-900 text-white hover:bg-primary-800 disabled:bg-slate-300',
    success:
      'bg-emerald-600 text-white hover:bg-emerald-700 disabled:bg-emerald-300',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300',
    ghost:
      'bg-white text-slate-700 ring-1 ring-inset ring-slate-300 hover:bg-slate-50',
  }

  return (
    <button
      className={`inline-flex items-center justify-center gap-1.5 rounded-lg px-4 py-2 text-sm font-semibold transition-all duration-150 active:scale-[0.98] disabled:cursor-not-allowed disabled:active:scale-100 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

export function Spinner({ label = 'Loading...' }) {
  return (
    <div className="flex items-center gap-2 py-10 justify-center text-slate-500 text-sm">
      <svg
        className="h-4 w-4 animate-spin"
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        />
      </svg>
      {label}
    </div>
  )
}

export function EmptyState({ title, description }) {
  return (
    <div className="flex flex-col items-center justify-center gap-1 py-14 text-center">
      <p className="text-sm font-medium text-slate-700">{title}</p>
      {description ? (
        <p className="text-xs text-slate-500 max-w-sm">{description}</p>
      ) : null}
    </div>
  )
}

export function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-inset ring-red-600/20">
      {message}
    </div>
  )
}

export function Field({ label, children, hint }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-600">
        {label}
      </span>
      {children}
      {hint ? (
        <span className="mt-1 block text-xs text-slate-400">{hint}</span>
      ) : null}
    </label>
  )
}

export const inputClass =
  'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-accent-600 focus:outline-none focus:ring-2 focus:ring-accent-600/20'
