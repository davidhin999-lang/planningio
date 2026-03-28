import { useState } from 'react'
import { Link } from 'react-router-dom'
import NavBar from '../components/NavBar'
import GenerateForm from '../components/GenerateForm'
import PlanRenderer from '../components/PlanRenderer'
import UpgradeModal from '../components/UpgradeModal'
import { Button } from '../components/ui/button'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function Generate() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null) // { id, title, content }
  const [showUpgrade, setShowUpgrade] = useState(false)

  async function handleGenerate(formData) {
    setLoading(true)
    setResult(null)
    try {
      const { data } = await api.post('/generate', formData)
      setResult(data)
    } catch (err) {
      if (err.response?.data?.error === 'limit_reached') {
        setShowUpgrade(true)
      } else {
        toast.error('Error al generar la planeación. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        {!result ? (
          <>
            <div className="mb-7">
              <h1 className="text-2xl font-bold text-text-primary">Nueva planeación</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Completa los 4 campos y la IA generará tu planeación didáctica completa.
              </p>
            </div>
            <div className="bg-white rounded-2xl border border-border p-6 shadow-sm">
              <GenerateForm onSubmit={handleGenerate} loading={loading} />
            </div>
          </>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-text-primary">{result.title}</h1>
                <p className="text-sm text-green-600 mt-0.5 font-medium">
                  ✓ Planeación generada y guardada
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setResult(null)} size="sm">
                  Nueva planeación
                </Button>
                <Button asChild size="sm">
                  <Link to="/dashboard">Ver todas</Link>
                </Button>
              </div>
            </div>
            <PlanRenderer content={result.content} />
          </>
        )}
      </main>
      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} />
    </div>
  )
}
