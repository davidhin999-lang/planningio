import { useState, useEffect } from 'react'
import NavBar from '../components/NavBar'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function AdminSchool() {
  const [users, setUsers] = useState([])
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(true)
  const [inviting, setInviting] = useState(false)

  useEffect(() => {
    api
      .get('/admin/users')
      .then((r) => setUsers(r.data))
      .catch(() => toast.error('Error al cargar los docentes.'))
      .finally(() => setLoading(false))
  }, [])

  async function handleInvite(e) {
    e.preventDefault()
    if (!email.trim()) return
    setInviting(true)
    try {
      await api.post('/admin/invite', { email: email.trim() })
      toast.success(`Invitación enviada a ${email.trim()}`)
      setEmail('')
      const r = await api.get('/admin/users')
      setUsers(r.data)
    } catch (err) {
      const msg = err.response?.data?.error
      if (msg === 'seat_limit_reached') {
        toast.error('Alcanzaste el límite de 20 docentes.')
      } else {
        toast.error('Error al enviar la invitación.')
      }
    } finally {
      setInviting(false)
    }
  }

  const atLimit = users.length >= 20

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-7">
          <h1 className="text-2xl font-bold text-text-primary">Mi escuela</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Administra los docentes de tu plan Escuela.{' '}
            <span className="font-medium text-text-primary">
              {users.length} / 20 asientos usados
            </span>
          </p>
        </div>

        {/* Invite form */}
        <div className="bg-white rounded-2xl border border-border p-6 mb-6">
          <h2 className="font-semibold text-text-primary mb-4">Invitar docente</h2>
          <form onSubmit={handleInvite} className="flex gap-3">
            <div className="flex-1">
              <Label htmlFor="invite-email" className="sr-only">
                Correo del docente
              </Label>
              <Input
                id="invite-email"
                type="email"
                placeholder="correo@docente.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={inviting || atLimit}
                autoComplete="email"
              />
            </div>
            <Button type="submit" disabled={inviting || atLimit}>
              {inviting ? 'Enviando...' : 'Invitar'}
            </Button>
          </form>
          {atLimit && (
            <p className="text-xs text-amber-600 mt-2">
              Alcanzaste el límite de 20 docentes. Actualiza tu plan para añadir más.
            </p>
          )}
        </div>

        {/* Seats table */}
        <div className="bg-white rounded-2xl border border-border overflow-hidden">
          <div className="px-5 py-3 border-b border-border">
            <h2 className="font-semibold text-text-primary">
              Docentes ({users.length})
            </h2>
          </div>

          {loading ? (
            <div className="p-5 space-y-3" aria-busy="true" aria-label="Cargando docentes">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-8 bg-border rounded animate-pulse" />
              ))}
            </div>
          ) : users.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              Aún no has invitado docentes. Usa el formulario de arriba.
            </div>
          ) : (
            <ul className="divide-y divide-border" aria-label="Lista de docentes">
              {users.map((u) => (
                <li
                  key={u.id}
                  className="px-5 py-3 flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-text-primary truncate">
                      {u.display_name || u.email}
                    </p>
                    {u.display_name && (
                      <p className="text-xs text-muted-foreground truncate">{u.email}</p>
                    )}
                  </div>
                  <Badge variant={u.status === 'active' ? 'default' : 'secondary'}>
                    {u.status === 'active' ? 'Activo' : 'Pendiente'}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}
