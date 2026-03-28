import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Textarea } from './ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select'

const GRADE_GROUPS = [
  {
    group: 'Preescolar',
    items: ['preescolar_1', 'preescolar_2', 'preescolar_3'],
  },
  {
    group: 'Primaria',
    items: ['primaria_1', 'primaria_2', 'primaria_3', 'primaria_4', 'primaria_5', 'primaria_6'],
  },
  {
    group: 'Secundaria',
    items: ['secundaria_1', 'secundaria_2', 'secundaria_3'],
  },
  {
    group: 'Preparatoria',
    items: ['preparatoria_1', 'preparatoria_2', 'preparatoria_3'],
  },
]

const GRADE_LABELS = {
  preescolar_1: 'Preescolar 1°', preescolar_2: 'Preescolar 2°', preescolar_3: 'Preescolar 3°',
  primaria_1: 'Primaria 1°', primaria_2: 'Primaria 2°', primaria_3: 'Primaria 3°',
  primaria_4: 'Primaria 4°', primaria_5: 'Primaria 5°', primaria_6: 'Primaria 6°',
  secundaria_1: 'Secundaria 1°', secundaria_2: 'Secundaria 2°', secundaria_3: 'Secundaria 3°',
  preparatoria_1: 'Preparatoria 1°', preparatoria_2: 'Preparatoria 2°', preparatoria_3: 'Preparatoria 3°',
}

export default function GenerateForm({ onSubmit, loading }) {
  function handleSubmit(e) {
    e.preventDefault()
    const fd = new FormData(e.target)
    onSubmit({
      subject: fd.get('subject'),
      grade_level: fd.get('grade_level'),
      topic: fd.get('topic'),
      objective: fd.get('objective'),
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div className="grid sm:grid-cols-2 gap-5">
        <div className="space-y-1.5">
          <Label htmlFor="subject">Materia</Label>
          <Input
            id="subject"
            name="subject"
            placeholder="Ej. Matemáticas, Español, Ciencias..."
            required
            disabled={loading}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="grade_level">Grado</Label>
          <Select name="grade_level" required disabled={loading}>
            <SelectTrigger id="grade_level">
              <SelectValue placeholder="Selecciona un grado" />
            </SelectTrigger>
            <SelectContent>
              {GRADE_GROUPS.map(({ group, items }) => (
                <div key={group}>
                  <div className="px-2 py-1 text-xs font-semibold text-muted-foreground">
                    {group}
                  </div>
                  {items.map((val) => (
                    <SelectItem key={val} value={val}>
                      {GRADE_LABELS[val]}
                    </SelectItem>
                  ))}
                </div>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="topic">Tema</Label>
        <Input
          id="topic"
          name="topic"
          placeholder="Ej. Fracciones equivalentes, La célula, El cuento..."
          required
          disabled={loading}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="objective">Propósito / Aprendizaje esperado</Label>
        <Textarea
          id="objective"
          name="objective"
          placeholder="Ej. El alumno identificará fracciones equivalentes usando materiales concretos."
          rows={3}
          required
          disabled={loading}
          className="resize-none"
        />
        <p className="text-xs text-muted-foreground">
          Describe qué lograrán los alumnos al final de la sesión.
        </p>
      </div>

      <Button type="submit" className="w-full" size="lg" disabled={loading}>
        {loading ? (
          <span className="flex items-center gap-2">
            <span
              className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
              aria-hidden="true"
            />
            Generando tu planeación...
          </span>
        ) : (
          '✦ Generar planeación'
        )}
      </Button>
    </form>
  )
}
