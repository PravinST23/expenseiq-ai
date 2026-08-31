import { useState } from 'react'
import { Button } from './ui'

/**
 * Paginates `items` into fixed-size pages and renders one page at a
 * time via `renderPage(pageItems, pageIndex)`.
 */
export default function Pagination({ items, pageSize = 10, renderPage }) {
  const [page, setPage] = useState(0)

  const totalPages = Math.max(1, Math.ceil(items.length / pageSize))
  const current = Math.min(page, totalPages - 1)
  const start = current * pageSize
  const pageItems = items.slice(start, start + pageSize)

  return (
    <div>
      <div key={current} className="route-fade">
        {renderPage(pageItems, current)}
      </div>

      {totalPages > 1 ? (
        <div className="mt-4 flex items-center justify-between">
          <p className="text-xs text-slate-500">
            Showing {start + 1}-{Math.min(start + pageSize, items.length)} of{' '}
            {items.length}
          </p>

          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setPage(current - 1)}
              disabled={current === 0}
            >
              Previous
            </Button>

            <span className="text-xs font-medium text-slate-500">
              Page {current + 1} of {totalPages}
            </span>

            <Button
              type="button"
              variant="ghost"
              onClick={() => setPage(current + 1)}
              disabled={current === totalPages - 1}
            >
              Next
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  )
}
