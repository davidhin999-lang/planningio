import { render, screen } from '@testing-library/react'
import UsageBadge from '../components/UsageBadge'

test('shows usage count for free plan', () => {
  render(<UsageBadge used={3} limit={5} plan="free" />)
  expect(screen.getByText(/3 \/ 5/)).toBeInTheDocument()
})

test('hidden for pro plan', () => {
  const { container } = render(<UsageBadge used={999} limit={null} plan="pro" />)
  expect(container.firstChild).toBeNull()
})

test('hidden for escuela plan', () => {
  const { container } = render(<UsageBadge used={0} limit={null} plan="escuela" />)
  expect(container.firstChild).toBeNull()
})
