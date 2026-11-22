"""Separador Sobre (Fase 5, tarefa 5.3; novo aspeto no bloco G, passo 28)."""

import flet as ft

import theme


def construir(app) -> ft.Control:
    cfg = app.config
    itens: list[ft.Control] = []
    if cfg.logotipo:
        itens.append(ft.Image(src=cfg.logotipo, width=96, height=96))
    itens += [
        theme.titulo(cfg, cfg.nome, 28, text_align=ft.TextAlign.CENTER),
        theme.secundario(cfg, cfg.slogan, 15, text_align=ft.TextAlign.CENTER),
        ft.Container(
            ft.Text(cfg.texto_sobre, size=15, color=cfg.cor_texto),
            bgcolor=cfg.cor_superficie, border_radius=theme.RAIO_CARTAO, padding=18,
        ),
        theme.secundario(cfg, f"Eventos carregados: {len(app.eventos)} "
                              f"(origem: {app.dados.origem})", 12),
        theme.botao(cfg, "Atualizar eventos", ft.Icons.REFRESH,
                    on_click=lambda e: app.recarregar(), principal=True),
    ]
    if cfg.contacto:
        itens.append(theme.botao(cfg, f"Contacto: {cfg.contacto}", ft.Icons.MAIL_OUTLINE,
                                 url=f"mailto:{cfg.contacto}"))
    return ft.Container(
        ft.Column(itens, spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  scroll=ft.ScrollMode.AUTO),
        padding=ft.Padding.only(left=20, right=20, top=24, bottom=24),
        expand=True,
    )
