"""
Constructor de prompts para Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional

# Templates de contenido por tipo
CONTENT_TEMPLATES: dict[str, str] = {
    "caption": (
        "Crea un caption cautivador para {platform}.\n"
        "Audiencia: {audience}\n"
        "Tono: {tone}\n"
        "Objetivo: {goal}"
    ),
    "script": (
        "Escribe un script de video para {platform}.\n"
        "Audiencia: {audience}\n"
        "Tono: {tone}"
    ),
    "hashtags": (
        "Genera hashtags relevantes para {platform}.\n"
        "Audiencia: {audience}\n"
        "Cantidad: 10-15 hashtags"
    ),
    "story": (
        "Crea contenido para story de {platform}.\n"
        "Formato: Corto, directo, visual\n"
        "Audiencia: {audience}\n"
        "Tono: {tone}"
    ),
    "ad": (
        "Escribe copy publicitario para {platform}.\n"
        "Objetivo: {goal}\n"
        "Audiencia: {audience}\n"
        "CTA requerido: Sí"
    ),
    "bio": (
        "Crea una bio profesional.\n"
        "Plataforma: {platform}\n"
        "Límite: 150 caracteres\n"
        "Tono: {tone}"
    ),
    "email": (
        "Redacta un email profesional.\n"
        "Objetivo: {goal}\n"
        "Audiencia: {audience}\n"
        "Tono: {tone}"
    ),
    "carrusel": (
        "Crea contenido para carrusel de Instagram.\n"
        "Audiencia: {audience}\n"
        "Cada slide: Título + Texto conciso"
    )
}

# Mapeo de tonos
TONE_MAP: dict[str, str] = {
    "professional": "Profesional y formal",
    "casual": "Casual y cercano",
    "inspiring": "Inspirador y motivacional",
    "humorous": "Divertido con toques de humor",
    "educational": "Educativo e informativo",
    "storytelling": "Narrativo y emocional"
}

# Mapeo de objetivos
GOAL_MAP: dict[str, str] = {
    "engagement": "Maximizar engagement (likes, comentarios, shares)",
    "awareness": "Aumentar awareness de marca",
    "conversion": "Generar conversiones y ventas",
    "education": "Educar a la audiencia",
    "community": "Fortalecer comunidad"
}


def build_user_prompt(
    content_type: str,
    brief: str,
    platform: str = "Instagram",
    audience: str = "General",
    tone: str = "professional",
    goal: str = "engagement",
    **kwargs
) -> str:
    """
    Construye el prompt del usuario.

    Args:
        content_type: Tipo de contenido (caption, script, etc.)
        brief: Brief específico del usuario
        platform: Plataforma social
        audience: Audiencia objetivo
        tone: Tono del contenido
        goal: Objetivo del contenido
        **kwargs: Parámetros adicionales (duration, slides, topic, etc.)

    Returns:
        Prompt completo del usuario
    """
    # Obtener template
    template = CONTENT_TEMPLATES.get(content_type, "")

    if not template:
        return brief

    # Formatear con contexto
    formatted_template = template.format(
        platform=platform,
        audience=audience,
        tone=TONE_MAP.get(tone, tone),
        goal=GOAL_MAP.get(goal, goal),
        **kwargs
    )

    # Combinar template con brief
    return f"{formatted_template}\n\nBrief específico:\n{brief}"


def build_system_prompt(
    client_name: str,
    business_type: Optional[str] = None,
    brand_voice: Optional[str] = None,
    keywords: Optional[list[str]] = None,
    avoid_topics: Optional[list[str]] = None
) -> str:
    """
    Construye el system prompt con contexto del cliente.

    Args:
        client_name: Nombre del cliente/negocio
        business_type: Tipo de negocio
        brand_voice: Voz de marca específica
        keywords: Keywords a incluir
        avoid_topics: Temas a evitar

    Returns:
        System prompt completo
    """
    prompt_parts = [
        f"Eres el generador de contenido de OMEGA para {client_name}."
    ]

    if business_type:
        prompt_parts.append(f"Industria: {business_type}")

    if brand_voice:
        prompt_parts.append(f"Voz de marca: {brand_voice}")

    if keywords:
        keywords_str = ", ".join(keywords)
        prompt_parts.append(f"Keywords importantes: {keywords_str}")

    if avoid_topics:
        avoid_str = ", ".join(avoid_topics)
        prompt_parts.append(f"Evitar mencionar: {avoid_str}")

    prompt_parts.append(
        "\nGenera contenido de alta calidad, original y alineado "
        "con la identidad de marca del cliente."
    )

    return "\n".join(prompt_parts)
