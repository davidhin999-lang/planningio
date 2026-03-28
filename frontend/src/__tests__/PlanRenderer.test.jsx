import { render, screen } from '@testing-library/react'
import PlanRenderer from '../components/PlanRenderer'

const mockContent = {
  proposito: 'Identificar fracciones equivalentes.',
  inicio: { duracion: '10 min', actividades: ['Exploración con círculos fraccionarios.'] },
  desarrollo: { duracion: '30 min', actividades: ['Completan tabla en parejas.'] },
  cierre: { duracion: '10 min', actividades: ['Plenaria de cierre.'] },
  materiales: ['Círculos fraccionarios', 'Cuaderno'],
  evaluacion: 'Observación directa y tabla completada.',
  competencias: ['Resolución de problemas matemáticos'],
  aprendizajes_esperados: ['Identifica fracciones equivalentes.'],
}

test('renders propósito', () => {
  render(<PlanRenderer content={mockContent} />)
  expect(screen.getByText('Propósito de la sesión')).toBeInTheDocument()
  expect(screen.getByText('Identificar fracciones equivalentes.')).toBeInTheDocument()
})

test('renders secuencia didáctica sections', () => {
  render(<PlanRenderer content={mockContent} />)
  expect(screen.getByText('Inicio')).toBeInTheDocument()
  expect(screen.getAllByText('10 min').length).toBeGreaterThanOrEqual(1)
  expect(screen.getByText('Exploración con círculos fraccionarios.')).toBeInTheDocument()
  expect(screen.getByText('Desarrollo')).toBeInTheDocument()
  expect(screen.getByText('Cierre')).toBeInTheDocument()
})

test('renders materiales', () => {
  render(<PlanRenderer content={mockContent} />)
  expect(screen.getByText('Materiales necesarios')).toBeInTheDocument()
  expect(screen.getByText('Círculos fraccionarios')).toBeInTheDocument()
})

test('renders competencias as pills', () => {
  render(<PlanRenderer content={mockContent} />)
  expect(screen.getByText('Resolución de problemas matemáticos')).toBeInTheDocument()
})

test('renders aprendizajes esperados', () => {
  render(<PlanRenderer content={mockContent} />)
  expect(screen.getByText('Identifica fracciones equivalentes.')).toBeInTheDocument()
})
