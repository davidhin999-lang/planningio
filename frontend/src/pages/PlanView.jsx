import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import NavBar from '../components/NavBar'
import PlanRenderer from '../components/PlanRenderer'
import { Button } from '../components/ui/button'
import { gradeLabel } from '../lib/utils'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function PlanView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get(`/planeaciones/${id}`)
      .then((r) => setPlan(r.data))
      .catch(() => {
        toast.error('No se encontró la planeación.')
        navigate('/dashboard')
      })
      .finally(() => setLoading(false))
  }, [id, navigate])

  if (loading) {
    return (
      <div className="min-h-screen bg-bg">
        <NavBar />
        <div className="max-w-3xl mx-auto px-4 py-8 space-y-4" aria-busy="true" aria-label="Cargando planeación">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-32 bg-white rounded-xl border border-border animate-pulse"
            />
          ))}
        </div>
      </div>
    )
  }

  if (!plan) return null

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <nav aria-label="Ruta de navegación" className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
          <Link to="/dashboard" className="hover:text-primary transition-colors">
            Mis planeaciones
          </Link>
          <span aria-hidden="true">/</span>
          <span className="text-text-primary truncate">{plan.title}</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">{plan.title}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              {gradeLabel(plan.grade_level)} · {plan.subject} · {plan.topic}
            </p>
          </div>
          <Button asChild variant="outline" size="sm">
            <Link to="/generate">Nueva planeación</Link>
          </Button>
        </div>

        <PlanRenderer content={plan.content} />
      </main>
    </div>
  )
}
