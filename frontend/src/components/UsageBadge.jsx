export default function UsageBadge({ used, limit, plan }) {
  if (plan !== 'free') return null
  const pct = limit > 0 ? (used / limit) * 100 : 0
  const color = pct >= 80
    ? 'text-red-600 bg-red-50 border-red-200'
    : 'text-muted-foreground bg-background border-border'

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${color}`}>
      <span>{used} / {limit}</span>
      <span className="hidden sm:inline">planeaciones este mes</span>
    </span>
  )
}
