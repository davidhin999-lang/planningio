import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('es-MX', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function gradeLabel(grade) {
  const map = {
    preescolar_1: 'Preescolar 1°', preescolar_2: 'Preescolar 2°', preescolar_3: 'Preescolar 3°',
    primaria_1: 'Primaria 1°', primaria_2: 'Primaria 2°', primaria_3: 'Primaria 3°',
    primaria_4: 'Primaria 4°', primaria_5: 'Primaria 5°', primaria_6: 'Primaria 6°',
    secundaria_1: 'Secundaria 1°', secundaria_2: 'Secundaria 2°', secundaria_3: 'Secundaria 3°',
    preparatoria_1: 'Preparatoria 1°', preparatoria_2: 'Preparatoria 2°', preparatoria_3: 'Preparatoria 3°',
  }
  return map[grade] ?? grade
}
