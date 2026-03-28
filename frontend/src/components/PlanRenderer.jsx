function Section({ title, accent, children }) {
  return (
    <section className="bg-white rounded-xl border border-border overflow-hidden">
      <div className={`px-5 py-3 border-b border-border flex items-center justify-between ${accent ? 'bg-primary-50' : 'bg-bg'}`}>
        <h2 className="font-semibold text-text-primary">{title}</h2>
        {accent && <span className="text-xs text-primary font-medium">{accent}</span>}
      </div>
      <div className="px-5 py-4">{children}</div>
    </section>
  )
}

function ActivityList({ items }) {
  return (
    <ol className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex gap-3 text-sm text-muted-foreground">
          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary-50 text-primary text-xs flex items-center justify-center font-medium mt-0.5">
            {i + 1}
          </span>
          {item}
        </li>
      ))}
    </ol>
  )
}

export default function PlanRenderer({ content }) {
  const {
    proposito,
    inicio,
    desarrollo,
    cierre,
    materiales,
    evaluacion,
    competencias,
    aprendizajes_esperados,
  } = content

  return (
    <div className="space-y-4">
      {/* Propósito */}
      <Section title="Propósito de la sesión">
        <p className="text-sm text-muted-foreground leading-relaxed">{proposito ?? ''}</p>
      </Section>

      {/* Secuencia didáctica */}
      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { key: 'inicio', label: 'Inicio', data: inicio },
          { key: 'desarrollo', label: 'Desarrollo', data: desarrollo },
          { key: 'cierre', label: 'Cierre', data: cierre },
        ].map(({ key, label, data }) => (
          <Section key={key} title={label} accent={data?.duracion}>
            <ActivityList items={data?.actividades ?? []} />
          </Section>
        ))}
      </div>

      {/* Aprendizajes esperados */}
      {aprendizajes_esperados?.length > 0 && (
        <Section title="Aprendizajes esperados">
          <ul className="space-y-1">
            {aprendizajes_esperados.map((a, i) => (
              <li key={i} className="flex gap-2 text-sm text-muted-foreground">
                <span className="text-primary" aria-hidden="true">✓</span>
                {a}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Materiales + Evaluación */}
      <div className="grid sm:grid-cols-2 gap-4">
        <Section title="Materiales necesarios">
          <ul className="space-y-1">
            {materiales?.map((m, i) => (
              <li key={i} className="flex gap-2 text-sm text-muted-foreground">
                <span className="text-accent" aria-hidden="true">·</span>
                {m}
              </li>
            ))}
          </ul>
        </Section>
        <Section title="Evaluación">
          <p className="text-sm text-muted-foreground leading-relaxed">{evaluacion ?? ''}</p>
        </Section>
      </div>

      {/* Competencias */}
      {competencias?.length > 0 && (
        <Section title="Competencias que se favorecen">
          <div className="flex flex-wrap gap-2">
            {competencias.map((c, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded-full bg-primary-50 text-primary text-xs font-medium"
              >
                {c}
              </span>
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}
