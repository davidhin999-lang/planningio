import { useState } from 'react'
import NavBar from '../components/NavBar'
import { Button } from '../components/ui/button'
import { useAuth } from '../context/AuthContext'
import api from '../lib/api'
import toast from 'react-hot-toast'

const PLANS = [
  {
    id: 'free',
    name: 'Gratis',
    price: '$0',
    period: '',
    features: [
      '5 planeaciones al mes',
      'Todos los grados y materias',
      'Historial de planeaciones',
    ],
    cta: 'Plan actual',
    highlight: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$149',
    period: 'MXN/mes',
    features: [
      'Planeaciones ilimitadas',
      'Todos los grados y materias',
      'Historial completo',
      'Soporte prioritario',
    ],
    cta: 'Actualizar a Pro',
    highlight: true,
  },
  {
    id: 'escuela',
    name: 'Escuela',
    price: '$799',
    period: 'MXN/mes',
    features: [
      'Hasta 20 docentes',
      'Panel de administrador',
      'Planeaciones ilimitadas para todos',
      'Factura fiscal disponible',
    ],
    cta: 'Actualizar a Escuela',
    highlight: false,
  },
]

export default function Billing() {
  const { subscription } = useAuth()
  const [loading, setLoading] = useState(null) // plan id being loaded, or 'manage'

  async function handleUpgrade(planId) {
    setLoading(planId)
    try {
      const { data } = await api.post('/billing/checkout', { plan: planId })
      window.location.href = data.checkout_url
    } catch {
      toast.error('Error al iniciar el proceso de pago. Intenta de nuevo.')
      setLoading(null)
    }
  }

  async function handleManage() {
    setLoading('manage')
    try {
      const { data } = await api.post('/billing/portal')
      window.location.href = data.portal_url
    } catch {
      toast.error('Error al abrir el portal de suscripción.')
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Suscripción</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Plan actual:{' '}
            <span className="font-medium text-text-primary capitalize">
              {subscription?.plan ?? 'free'}
            </span>
            {subscription?.plan !== 'free' && (
              <>
                {' · '}
                <button
                  onClick={handleManage}
                  disabled={loading === 'manage'}
                  className="text-primary hover:underline cursor-pointer disabled:opacity-60"
                >
                  {loading === 'manage' ? 'Redirigiendo...' : 'Administrar suscripción'}
                </button>
              </>
            )}
          </p>
        </div>

        <div className="grid sm:grid-cols-3 gap-5">
          {PLANS.map((plan) => {
            const isCurrent = (subscription?.plan ?? 'free') === plan.id
            const isUpgradeable = !isCurrent && plan.id !== 'free'

            return (
              <div
                key={plan.id}
                className={`rounded-2xl border p-6 flex flex-col ${
                  plan.highlight
                    ? 'border-primary bg-primary-50 shadow-md shadow-primary/10'
                    : 'border-border bg-white'
                } ${isCurrent ? 'ring-2 ring-primary' : ''}`}
              >
                {isCurrent && (
                  <span className="self-start px-2.5 py-0.5 rounded-full bg-primary text-white text-xs font-semibold mb-3">
                    Plan actual
                  </span>
                )}
                {!isCurrent && plan.highlight && (
                  <span className="self-start px-2.5 py-0.5 rounded-full bg-primary text-white text-xs font-semibold mb-3">
                    Más popular
                  </span>
                )}

                <h2 className="font-semibold text-text-primary">{plan.name}</h2>
                <div className="mt-2 mb-4">
                  <span className="text-3xl font-bold text-text-primary">{plan.price}</span>
                  {plan.period && (
                    <span className="text-sm text-muted-foreground ml-1">{plan.period}</span>
                  )}
                </div>

                <ul className="space-y-2 flex-1 mb-6" aria-label={`Características del plan ${plan.name}`}>
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="text-primary mt-0.5" aria-hidden="true">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>

                <Button
                  variant={plan.highlight && isUpgradeable ? 'default' : 'outline'}
                  className="w-full"
                  disabled={isCurrent || loading === plan.id}
                  onClick={() => isUpgradeable && handleUpgrade(plan.id)}
                >
                  {loading === plan.id ? (
                    <span className="flex items-center gap-2">
                      <span
                        className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
                        aria-hidden="true"
                      />
                      Redirigiendo...
                    </span>
                  ) : isCurrent ? (
                    'Plan actual'
                  ) : (
                    plan.cta
                  )}
                </Button>
              </div>
            )
          })}
        </div>

        <p className="text-xs text-muted-foreground text-center mt-6">
          Los pagos son procesados de forma segura por Stripe. OXXO Pay disponible.
        </p>
      </main>
    </div>
  )
}
