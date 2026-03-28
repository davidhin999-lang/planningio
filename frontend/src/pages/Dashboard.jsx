import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import NavBar from '../components/NavBar'
import PlanCard from '../components/PlanCard'
import { Button } from '../components/ui/button'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [plans, setPlans] = useState([])
  const [usage, setUsage] = useState({ used: 0, limit: 5 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [plansRes, meRes] = await Promise.all([
          api.get('/planeaciones'),
          api.get('/auth/me'),
        ])
        setPlans(plansRes.data)
        setUsage(meRes.data.usage ?? { used: 0, limit: 5 })
      } catch {
        toast.error('Error al cargar tus planeaciones.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  async function handleDelete(id) {
    if (!window.confirm('¿Eliminar esta planeación?')) return
    try {
      await api.delete(`/planeaciones/${id}`)
      setPlans((prev) => prev.filter((p) => p.id !== id))
      toast.success('Planeación eliminada.')
    } catch {
      toast.error('No se pudo eliminar.')
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <NavBar usageStats={usage} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Mis planeaciones</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              {loading
                ? 'Cargando...'
                : plans.length === 0
                ? 'Aún no tienes planeaciones.'
                : `${plans.length} planeación${plans.length !== 1 ? 'es' : ''}`}
            </p>
          </div>
          <Button asChild>
            <Link to="/generate">+ Nueva planeación</Link>
          </Button>
        </div>

        {loading ? (
          <div className="grid sm:grid-cols-2 gap-4" aria-busy="true" aria-label="Cargando planeaciones">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="bg-white rounded-xl border border-border p-5 animate-pulse"
              >
                <div className="h-4 bg-border rounded w-3/4 mb-2" />
                <div className="h-3 bg-border rounded w-1/2 mb-1" />
                <div className="h-3 bg-border rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : plans.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-4xl mb-4" aria-hidden="true">📋</p>
            <h2 className="font-semibold text-text-primary mb-1">
              Aún no tienes planeaciones
            </h2>
            <p className="text-sm text-muted-foreground mb-6">
              Genera tu primera planeación didáctica en segundos.
            </p>
            <Button asChild>
              <Link to="/generate">Generar ahora</Link>
            </Button>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-4">
            {plans.map((plan) => (
              <PlanCard key={plan.id} plan={plan} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
