import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Generate from './pages/Generate'
import PlanView from './pages/PlanView'
import Billing from './pages/Billing'
import AdminSchool from './pages/AdminSchool'

function Spinner() {
  return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div
        className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"
        aria-label="Cargando"
        role="status"
      />
    </div>
  )
}

function RequireAuth({ children }) {
  const { currentUser, loading } = useAuth()
  if (loading) return <Spinner />
  return currentUser ? children : <Navigate to="/login" replace />
}

function RequireSchoolAdmin({ children }) {
  const { subscription } = useAuth()
  if (subscription.plan !== 'escuela') return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  const { currentUser, loading } = useAuth()

  if (loading) return <Spinner />

  return (
    <Routes>
      <Route path="/" element={currentUser ? <Navigate to="/dashboard" replace /> : <Landing />} />
      <Route path="/login" element={currentUser ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
      <Route path="/generate" element={<RequireAuth><Generate /></RequireAuth>} />
      <Route path="/plan/:id" element={<RequireAuth><PlanView /></RequireAuth>} />
      <Route path="/billing" element={<RequireAuth><Billing /></RequireAuth>} />
      <Route
        path="/admin/school"
        element={
          <RequireAuth>
            <RequireSchoolAdmin>
              <AdminSchool />
            </RequireSchoolAdmin>
          </RequireAuth>
        }
      />
    </Routes>
  )
}
