import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import UpgradeModal from '../components/UpgradeModal'

test('shows dialog when open=true', () => {
  render(
    <BrowserRouter>
      <UpgradeModal open={true} onClose={() => {}} />
    </BrowserRouter>
  )
  expect(screen.getByRole('dialog')).toBeInTheDocument()
  expect(screen.getByText(/límite del mes/i)).toBeInTheDocument()
})

test('calls onClose when "Ahora no" is clicked', async () => {
  const onClose = vi.fn()
  render(
    <BrowserRouter>
      <UpgradeModal open={true} onClose={onClose} />
    </BrowserRouter>
  )
  await userEvent.click(screen.getByRole('button', { name: /ahora no/i }))
  expect(onClose).toHaveBeenCalledOnce()
})

test('renders null when open=false', () => {
  const { queryByRole } = render(
    <BrowserRouter>
      <UpgradeModal open={false} onClose={() => {}} />
    </BrowserRouter>
  )
  expect(queryByRole('dialog')).not.toBeInTheDocument()
})
