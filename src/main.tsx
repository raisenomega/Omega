import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { initErrorReporter } from "./lib/error_reporter";

// Capa 9 · captura global de errores (window.onerror + unhandledrejection) → SENTINEL.
initErrorReporter();

createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>,
);
