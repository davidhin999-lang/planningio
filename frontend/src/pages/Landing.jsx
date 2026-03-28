import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'

const features = [
  {
    icon: '📋',
    title: 'Formato SEP exacto',
    desc: 'Genera planeaciones alineadas a la Nueva Escuela Mexicana (NEM 2022), Plan 2011 y Plan 2017.',
  },
  {
    icon: '⚡',
    title: 'Lista en segundos',
    desc: 'Solo ingresa materia, grado, tema y propósito. El resto lo hace la IA en menos de 10 segundos.',
  },
  {
    icon: '📚',
    title: 'Historial completo',
    desc: 'Todas tus planeaciones guardadas, buscables y reutilizables cuando las necesites.',
  },
  {
    icon: '🏫',
    title: 'Para toda la escuela',
    desc: 'El plan Escuela permite hasta 20 docentes bajo un mismo administrador.',
  },
]

const plans = [
  {
    id: 'free',
    name: 'Gratis',
    price: '$0',
    period: 'para siempre',
    features: ['5 planeaciones al mes', 'Todos los grados y materias', 'Historial de planeaciones'],
    cta: 'Empezar gratis',
    href: '/login',
    highlight: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$149',
    period: 'MXN / mes',
    features: [
      'Planeaciones ilimitadas',
      'Todos los grados y materias',
      'Historial completo',
      'Soporte prioritario',
    ],
    cta: 'Comenzar ahora',
    href: '/login',
    highlight: true,
  },
  {
    id: 'escuela',
    name: 'Escuela',
    price: '$799',
    period: 'MXN / mes',
    features: [
      'Hasta 20 docentes',
      'Panel de administrador',
      'Planeaciones ilimitadas',
      'Factura fiscal disponible',
    ],
    cta: 'Contactar',
    href: '/login',
    highlight: false,
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-bg">
      {/* Nav */}
      <header className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-border">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="flex items-center gap-2 font-semibold text-text-primary">
            <span className="text-primary text-xl" aria-hidden="true">✦</span>
            PlaneaAI
          </span>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild size="sm">
              <Link to="/login">Iniciar sesión</Link>
            </Button>
            <Button asChild size="sm">
              <Link to="/login">Empezar gratis</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-4 pt-20 pb-16 text-center">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary-50 text-primary text-sm font-medium mb-6">
          ✦ Alineado a NEM 2022 · Plan 2011 · Plan 2017
        </span>
        <h1 className="text-4xl sm:text-5xl font-bold text-text-primary leading-tight mb-5">
          Tu planeación didáctica
          <br className="hidden sm:block" />
          <span className="text-primary"> lista en segundos</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
          PlaneaAI genera planeaciones didácticas completas en el formato exacto que pide la SEP —
          solo dile la materia, grado, tema y propósito.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button asChild size="lg" className="text-base px-8">
            <Link to="/login">Generar mi primera planeación →</Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="text-base px-8">
            <a href="#precios">Ver precios</a>
          </Button>
        </div>

        {/* Demo preview card */}
        <div className="mt-12 bg-white rounded-2xl border border-border shadow-sm p-6 text-left max-w-2xl mx-auto">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-2.5 h-2.5 rounded-full bg-red-400" aria-hidden="true" />
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-400" aria-hidden="true" />
            <span className="w-2.5 h-2.5 rounded-full bg-green-400" aria-hidden="true" />
            <span className="ml-2 text-xs text-muted-foreground">PlaneaAI · Matemáticas 3° · Fracciones</span>
          </div>
          <div className="space-y-3 text-sm">
            {[
              { label: 'Propósito', value: 'El alumno identificará fracciones equivalentes usando materiales concretos.' },
              { label: 'Inicio (10 min)', value: 'Exploración con círculos fraccionarios: los alumnos comparan ½ y 2/4...' },
              { label: 'Desarrollo (30 min)', value: 'En parejas, los alumnos completan una tabla de fracciones equivalentes...' },
              { label: 'Cierre (10 min)', value: 'Plenaria: cada equipo comparte una fracción equivalente que descubrió...' },
            ].map(({ label, value }) => (
              <div key={label}>
                <span className="font-semibold text-text-primary">{label}: </span>
                <span className="text-muted-foreground">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center text-text-primary mb-10">
          Todo lo que necesitas, nada que no necesitas
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map(({ icon, title, desc }) => (
            <div key={title} className="bg-white rounded-xl border border-border p-5">
              <span className="text-2xl mb-3 block" aria-hidden="true">{icon}</span>
              <h3 className="font-semibold text-text-primary mb-1">{title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="precios" className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center text-text-primary mb-2">Precios</h2>
        <p className="text-center text-muted-foreground mb-10">Empieza gratis, actualiza cuando quieras.</p>
        <div className="grid sm:grid-cols-3 gap-6">
          {plans.map(({ id, name, price, period, features, cta, href, highlight }) => (
            <div
              key={id}
              className={`rounded-2xl border p-6 flex flex-col ${
                highlight
                  ? 'border-primary bg-primary-50 shadow-md shadow-primary/10'
                  : 'border-border bg-white'
              }`}
            >
              {highlight && (
                <span className="self-start px-2.5 py-0.5 rounded-full bg-primary text-white text-xs font-semibold mb-3">
                  Más popular
                </span>
              )}
              <h3 className="font-semibold text-text-primary">{name}</h3>
              <div className="mt-2 mb-4">
                <span className="text-3xl font-bold text-text-primary">{price}</span>
                <span className="text-sm text-muted-foreground ml-1">{period}</span>
              </div>
              <ul className="space-y-2 flex-1 mb-6" aria-label={`Características del plan ${name}`}>
                {features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="text-primary mt-0.5" aria-hidden="true">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <Button
                asChild
                variant={highlight ? 'default' : 'outline'}
                className="w-full"
              >
                <Link to={href}>{cta}</Link>
              </Button>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 mt-8">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-1.5 font-medium text-text-primary">
            <span className="text-primary" aria-hidden="true">✦</span>
            PlaneaAI
          </span>
          <span>© {new Date().getFullYear()} PlaneaAI · Hecho para docentes mexicanos</span>
        </div>
      </footer>
    </div>
  )
}
