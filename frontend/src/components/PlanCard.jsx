import { Link } from 'react-router-dom'
import { formatDate, gradeLabel } from '../lib/utils'

export default function PlanCard({ plan, onDelete }) {
  return (
    <article className="bg-white rounded-xl border border-border p-5 hover:border-primary/40 hover:shadow-sm transition-all group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <Link
            to={`/plan/${plan.id}`}
            className="font-semibold text-text-primary hover:text-primary line-clamp-1 transition-colors"
          >
            {plan.title}
          </Link>
          <p className="text-sm text-muted-foreground mt-0.5">
            {gradeLabel(plan.grade_level)} · {plan.subject}
          </p>
          <p className="text-xs text-muted-foreground mt-1">{formatDate(plan.created_at)}</p>
        </div>
        <button
          onClick={() => onDelete(plan.id)}
          aria-label={`Eliminar ${plan.title}`}
          className="p-1.5 text-muted-foreground hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all rounded-md hover:bg-red-50 cursor-pointer min-w-[44px] min-h-[44px] flex items-center justify-center"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </article>
  )
}
