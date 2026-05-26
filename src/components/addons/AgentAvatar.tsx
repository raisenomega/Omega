import { useState } from "react";

interface AgentAvatarProps {
  src: string;
  name: string;
  className?: string;  // tamaño + forma + borde (rounded-full / rounded-xl · h-/w- · border)
}

// Foto del agente con fallback honesto: si la imagen falla (404 · path), muestra la
// inicial del nombre sobre fondo amber en vez de un ícono roto. Reusado por card + modal.
export function AgentAvatar({ src, name, className = "" }: AgentAvatarProps) {
  const [failed, setFailed] = useState(false);
  if (failed) {
    return (
      <div
        className={`flex items-center justify-center bg-amber-500/20 text-2xl font-bold text-amber-500 ${className}`}
        aria-label={name}
      >
        {name.charAt(0).toUpperCase()}
      </div>
    );
  }
  return (
    <img
      src={src}
      alt={name}
      onError={() => setFailed(true)}
      className={`object-cover ${className}`}
    />
  );
}
