"""Ecrã de arranque (bloco G, passo 26).

Mostrado logo que a app abre, enquanto os eventos são lidos. Usa o mesmo desenho
do ecrã de carregamento da página HTML (scripts/splash.py): logótipo ao centro,
anel dourado a rodar e a frase "A preparar a agenda…". Assim, a passagem da
página para a app não se nota.
"""

import flet as ft

import theme


def construir(config) -> ft.View:
    anel = ft.ProgressRing(
        width=120, height=120, stroke_width=4,
        color=config.cor_destaque, bgcolor=config.cor_superficie_2,
        stroke_cap=ft.StrokeCap.ROUND,
    )
    monograma = ft.Container(
        content=ft.Text("EC", size=26, font_family=config.fonte_titulos,
                        color=config.cor_texto),
        width=60, height=60, bgcolor=config.cor_superficie, border_radius=16,
        alignment=ft.Alignment.CENTER,
    )
    return ft.View(
        route="/arranque",
        bgcolor=config.cor_fundo,
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Stack([anel, ft.Container(monograma, width=120, height=120,
                                                     alignment=ft.Alignment.CENTER)],
                                 width=120, height=120),
                        theme.destaque(config, config.nome, 17),
                        theme.secundario(config, "A preparar a agenda…", 13),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=14,
                ),
                expand=True,
                alignment=ft.Alignment.CENTER,
            )
        ],
        padding=0,
    )
