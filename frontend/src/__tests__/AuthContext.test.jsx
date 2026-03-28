import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { AuthProvider, useAuth } from '../context/AuthContext'

// Mock Firebase
vi.mock('../lib/firebase', () => ({ auth: {} }))
vi.mock('firebase/auth', () => ({
  onAuthStateChanged: vi.fn((auth, cb) => { cb(null); return () => {} }),
}))
vi.mock('../lib/api', () => ({
  default: { post: vi.fn().mockResolvedValue({ data: { subscription: { plan: 'free', status: 'active' } } }) },
}))

function TestComponent() {
  const { currentUser, subscription, loading } = useAuth()
  if (loading) return <div>loading</div>
  return <div>{currentUser ? 'logged-in' : 'logged-out'} {subscription?.plan}</div>
}

test('shows logged-out state when no Firebase user', async () => {
  render(<AuthProvider><TestComponent /></AuthProvider>)
  await waitFor(() => expect(screen.queryByText('loading')).not.toBeInTheDocument())
  expect(screen.getByText('logged-out free')).toBeInTheDocument()
})
