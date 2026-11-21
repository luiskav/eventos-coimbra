"""Separador Sobre (Fase 5, tarefa 5.3)."""

import flet as ft


def construir(app) -> ft.Control:
    cfg = app.config
    itens: list[ft.Control] = []
    if cfg.logotipo:
        itens.append(ft.Image(src=cfg.logotipo, width=120, height=120))
    itens += [
        ft.Text(cfg.nome, size=24, weight=ft.FontWeight.BOLD),
        ft.Text(cfg.slogan, italic=True),
        ft.Text(cfg.texto_sobre),
        ft.Text(f"Eventos carregados: {len(app.eventos)} (origem: {app.dados.origem})",
                size=12, color=ft.Colors.OUTLINE),
        ft.Button(content=ft.Text("Atualizar eventos"), icon=ft.Icons.REFRESH,
                  on_click=lambda e: app.recarregar()),
    ]
    if cfg.contacto:
        itens.append(
            ft.TextButton(content=ft.Text(f"Contacto: {cfg.contacto}"),
                          url=f"mailto:{cfg.contacto}")
        )
    return ft.Container(
        ft.Column(itens, spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  scroll=ft.ScrollMode.AUTO),
        padding=24,
        expand=True,
    )
