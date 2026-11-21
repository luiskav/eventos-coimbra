"""Separador dos favoritos (Fase 4, tarefa 4.2)."""

import flet as ft

from views.componentes import cartao_evento, mensagem_vazia


def construir(app) -> ft.Control:
    hoje = app.agora().date()
    eventos = sorted(
        (e for e in app.eventos if app.favoritos.contem(e.id)), key=lambda e: e.inicio
    )
    if not eventos:
        return mensagem_vazia(
            "Ainda não guardaste eventos.\nToca no coração de um evento para o guardar aqui.",
            ft.Icons.FAVORITE_BORDER,
        )
    return ft.ListView(
        [cartao_evento(app, ev, hoje, mostrar_dia=True) for ev in eventos],
        expand=True,
        padding=ft.Padding.only(top=8, bottom=16),
    )
