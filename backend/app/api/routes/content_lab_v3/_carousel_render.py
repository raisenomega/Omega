"""Pieza 1 · A2.4 · ensamblado del prompt por placa (Q1-A · helper puro · sin IO · testable aislado).

Por cada slide: visual_note (qué dibujar) + brand_block (marca · A2.1) + el text a renderizar (Q1-A:
Gemini dibuja el copy español, envuelto en instrucción inglesa · comillas RECTAS). Q1-B (overlay) = debt
si la prueba en vivo muestra que Gemini deletrea mal el español.
"""
from typing import List

from app.api.routes.content_lab_v3.models.content_lab_models import CarouselSlide


def build_placa_prompts(slides: List[CarouselSlide], brand_block: str) -> List[str]:
    """N slides + el brand_block (mismo para todas) → N prompts de imagen, en orden. Puro."""
    return [
        f'{s.visual_note}{brand_block}, render this exact text on the design: "{s.text}"'
        for s in slides
    ]
