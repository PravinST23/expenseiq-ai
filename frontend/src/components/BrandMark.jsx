// Product mark for ExpenseIQ - a simple ascending-bars glyph (the
// standard finance/analytics visual language) plus a plain wordmark.

export function BrandIcon({ className = 'h-8 w-8' }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <rect
        x="2"
        y="2"
        width="28"
        height="28"
        rx="8"
        fill="var(--color-primary-800)"
      />
      <rect x="9" y="17" width="4" height="8" rx="1.5" fill="var(--color-accent-500)" />
      <rect x="15" y="11" width="4" height="14" rx="1.5" fill="var(--color-accent-500)" />
      <rect x="21" y="7" width="4" height="18" rx="1.5" fill="var(--color-accent-400)" />
    </svg>
  )
}

export default function BrandMark({ size = 'md', dark = false }) {
  const textSize = size === 'lg' ? 'text-2xl' : 'text-lg'
  const iconSize = size === 'lg' ? 'h-9 w-9' : 'h-7 w-7'

  return (
    <div className="flex items-center gap-2">
      <BrandIcon className={iconSize} />
      <span
        className={`${textSize} font-bold tracking-tight leading-none ${
          dark ? 'text-white' : 'text-primary-900'
        }`}
      >
        Expense<span className="text-accent-600">IQ</span>
      </span>
    </div>
  )
}
