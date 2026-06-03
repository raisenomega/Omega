import { Component, ErrorInfo, ReactNode } from "react";
import { reportError } from "@/lib/error_reporter";

// ErrorBoundary global · captura errores de render (que window.onerror no atrapa) y los
// reporta al mismo endpoint SENTINEL. Fallback UI honesto · sin pantalla en blanco.
interface Props {
  children: ReactNode;
}
interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    try {
      reportError(error, info.componentStack ?? undefined);
    } catch {
      /* noop · nunca romper por el reporte */
    }
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center gap-3 p-6 text-center">
          <p className="text-lg font-medium">Algo salió mal.</p>
          <p className="text-sm text-muted-foreground">Estamos notificados. Probá refrescar la página.</p>
          <button
            onClick={() => location.reload()}
            className="rounded bg-primary px-4 py-2 text-sm text-primary-foreground"
          >
            Refrescar
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
