import { Terminal } from "lucide-react";
import { DevPlaceholder } from "./DevPlaceholder";

export function DevTerminalTab() {
  return (
    <DevPlaceholder
      icon={Terminal}
      title="Code Terminal"
      description="Terminal en sandbox E2B · Claude puede clonar el repo, correr tests y abrir PRs sin tocar producción."
    />
  );
}
