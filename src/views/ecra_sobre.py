"""Separador Sobre (Fase 5, tarefa 5.3; novo aspeto no bloco G; versão beta: partilha
da app, frases de apresentação e páginas legais)."""

import flet as ft

import theme


def _cartao(cfg, controlos: list[ft.Control], **kw) -> ft.Container:
    return ft.Container(
        ft.Column(controlos, **{"spacing": 12, **kw}),
        bgcolor=cfg.cor_superficie, border_radius=theme.RAIO_CARTAO, padding=18,
    )


def _ligacao(cfg, icone, texto: str, url: str) -> ft.Control:
    """Linha de lista: ícone, texto e seta, que abre um endereço."""
    return ft.Container(
        ft.Row([ft.Icon(icone, size=20, color=cfg.cor_destaque),
                ft.Text(texto, size=15, color=cfg.cor_texto, expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color=cfg.cor_texto_2)],
               spacing=12),
        url=url, padding=ft.Padding.symmetric(vertical=6), ink=True,
    )


def construir(app) -> ft.Control:
    cfg = app.config
    itens: list[ft.Control] = []
    if cfg.logotipo:
        itens.append(ft.Image(src=cfg.logotipo, width=96, height=96))
    itens += [
        theme.titulo(cfg, cfg.nome, 30, text_align=ft.TextAlign.CENTER),
        theme.destaque(cfg, cfg.slogan, 17, color=cfg.cor_destaque,
                       text_align=ft.TextAlign.CENTER),
        _cartao(cfg, [ft.Text(cfg.texto_sobre, size=15, color=cfg.cor_texto)] + [
            ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, size=16, color=cfg.cor_destaque),
                    theme.secundario(cfg, frase, 14, expand=True)], spacing=10)
            for frase in cfg.frases_sobre
        ]),
        # Partilhar a app: o melhor marketing é um amigo a mandar o link
        ft.Row([
            theme.botao(cfg, "Partilhar a app", ft.Icons.IOS_SHARE,
                        on_click=lambda e: app.pedir_partilha_app(), principal=True),
        ], alignment=ft.MainAxisAlignment.CENTER),
    ]

    ligacoes: list[ft.Control] = []
    if cfg.contacto:
        ligacoes.append(_ligacao(cfg, ft.Icons.ADD_CIRCLE_OUTLINE, "Sugerir um evento",
                                 f"mailto:{cfg.contacto}?subject=Sugestão de evento"))
        ligacoes.append(_ligacao(cfg, ft.Icons.MAIL_OUTLINE, "Contacto",
                                 f"mailto:{cfg.contacto}"))
    if cfg.url_site:
        ligacoes += [
            _ligacao(cfg, ft.Icons.PRIVACY_TIP_OUTLINED, "Política de privacidade",
                     cfg.url_pagina("privacidade")),
            _ligacao(cfg, ft.Icons.GAVEL, "Termos de utilização", cfg.url_pagina("termos")),
        ]
    if ligacoes:
        itens.append(_cartao(cfg, ligacoes, spacing=4))

    itens += [
        theme.botao(cfg, "Atualizar eventos", ft.Icons.REFRESH,
                    on_click=lambda e: app.recarregar()),
        theme.secundario(cfg, f"Versão {cfg.versao or '—'} · {len(app.eventos)} eventos "
                              f"(origem: {app.dados.origem})", 12,
                         text_align=ft.TextAlign.CENTER),
        theme.secundario(cfg, "A informação vem dos sites das salas e entidades. "
                              "Confirma sempre na fonte antes de saíres de casa.", 12,
                         italic=True, text_align=ft.TextAlign.CENTER),
    ]
    return ft.Container(
        ft.Column(itens, spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                  scroll=ft.ScrollMode.AUTO),
        padding=ft.Padding.only(left=20, right=20, top=24, bottom=24),
        expand=True,
    )
