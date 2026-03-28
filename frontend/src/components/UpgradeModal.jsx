import { Link } from 'react-router-dom'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog'
import { Button } from './ui/button'

export default function UpgradeModal({ open, onClose }) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <div className="text-3xl mb-2" aria-hidden="true">🚀</div>
          <DialogTitle>Alcanzaste el límite del mes</DialogTitle>
          <DialogDescription>
            Has usado tus 5 planeaciones gratuitas este mes. Actualiza a Pro para generar
            planeaciones ilimitadas por solo $149 MXN al mes.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-2 mt-2">
          <Button asChild className="w-full" onClick={onClose}>
            <Link to="/billing">Ver planes y actualizar</Link>
          </Button>
          <Button variant="ghost" className="w-full" onClick={onClose}>
            Ahora no
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
