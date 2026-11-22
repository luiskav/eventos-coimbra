"""Separador dos favoritos (Fase 4, tarefa 4.2; novo aspeto no bloco G, passo 28)."""

import flet as ft

import theme
from views.componentes import cartao_evento, mensagem_vazia


def construir(app) -> ft.Control:
    cfg = app.config
    hoje = app.agora().date()
    eventos = sorted(
        (e for e in app.eventos if app.favoritos.contem(e.id)), key=lambda e: e.inicio
    )
    cabecalho = ft.Container(
        theme.titulo(cfg, "Favoritos", 32),
        padding=ft.Padding.only(left=20, right=20, top=12, bottom=8),
    )
    if not eventos:
        return ft.Column([
            cabecalho,
            mensagem_vazia(
                app,
                "Ainda não guardaste eventos.\nToca no coração de um evento para o guardar aqui.",
                ft.Icons.FAVORITE_BORDER,
            ),
        ], expand=True)
    return ft.ListView(
        [cabecalho] + [cartao_evento(app, ev, hoje, mostrar_dia=True) for ev in eventos],
        expand=True,
        padding=ft.Padding.only(bottom=24),
    )
