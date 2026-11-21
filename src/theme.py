"""Ícones das categorias (Fase 3, tarefa 3.6) e tema do config.json (Fase 5, tarefa 5.2)."""

import flet as ft

from config import Config

ICONES_CATEGORIAS = {
    "musica": ft.Icons.MUSIC_NOTE,
    "teatro": ft.Icons.THEATER_COMEDY,
    "exposicao": ft.Icons.PALETTE,
    "desporto": ft.Icons.SPORTS_SOCCER,
    "academico": ft.Icons.SCHOOL,
    "familia": ft.Icons.FAMILY_RESTROOM,
    "feira": ft.Icons.STOREFRONT,
    "outro": ft.Icons.EVENT,
}


# FASE 5
def construir_tema(config: Config) -> ft.Theme:
    return ft.Theme(color_scheme_seed=config.cor_primaria, use_material3=True)


def icone_categoria(codigo: str):
    return ICONES_CATEGORIAS.get(codigo, ft.Icons.EVENT)
