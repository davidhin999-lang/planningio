import { Link, useNavigate } from 'react-router-dom'
import { signOut } from 'firebase/auth'
import { auth } from '../lib/firebase'
import { useAuth } from '../context/AuthContext'
import UsageBadge from './UsageBadge'
import { Button } from './ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'
import { Avatar, AvatarFallback } from './ui/avatar'

export default function NavBar({ usageStats }) {
  const { currentUser, subscription } = useAuth()
  const navigate = useNavigate()

  const initials = currentUser?.displayName
    ? currentUser.displayName.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : currentUser?.email?.[0]?.toUpperCase() ?? '?'

  async function handleSignOut() {
    await signOut(auth)
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-30 bg-surface border-b border-border">
      <nav
        className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between"
        aria-label="Navegación principal"
      >
        <Link
          to="/dashboard"
          className="flex items-center gap-2 font-semibold text-text-primary"
        >
          <span className="text-primary text-xl" aria-hidden="true">✦</span>
          <span>PlaneaAI</span>
        </Link>

        <div className="flex items-center gap-3">
          {usageStats && (
            <UsageBadge
              used={usageStats.used}
              limit={usageStats.limit}
              plan={subscription?.plan ?? 'free'}
            />
          )}

          <Button asChild size="sm" className="hidden sm:inline-flex">
            <Link to="/generate">Nueva planeación</Link>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="rounded-full focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
                aria-label="Menú de usuario"
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary-100 text-primary text-xs font-semibold">
                    {initials}
                  </AvatarFallback>
                </Avatar>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <div className="px-2 py-1.5">
                <p className="text-xs text-muted-foreground truncate">{currentUser?.email}</p>
                <p className="text-xs font-medium mt-0.5 capitalize">{subscription?.plan ?? 'free'}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/dashboard">Mis planeaciones</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/billing">Suscripción</Link>
              </DropdownMenuItem>
              {subscription?.plan === 'escuela' && (
                <DropdownMenuItem asChild>
                  <Link to="/admin/school">Mi escuela</Link>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleSignOut}
                className="text-red-600 cursor-pointer focus:text-red-600"
              >
                Cerrar sesión
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </nav>
    </header>
  )
}
