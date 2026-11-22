"""Ecrã de detalhe de um evento (Fase 3, tarefa 3.8; botões extra na Fase 4, tarefa 4.4;
novo aspeto no bloco G, passo 28)."""

import flet as ft

import agenda
import theme
from models import Evento


def _linha(app, icone, texto: str) -> ft.Control:
    cfg = app.config
    return ft.Row(
        [ft.Container(ft.Icon(icone, size=18, color=cfg.cor_destaque),
                      width=36, height=36, bgcolor=cfg.cor_superficie_2, border_radius=10,
                      alignment=ft.Alignment.CENTER),
         ft.Text(texto, expand=True, selectable=True, size=15, color=cfg.cor_texto)],
        spacing=12,
    )


def construir(app, evento: Evento) -> ft.View:
    cfg = app.config
    hoje = app.agora().date()
    favorito = app.favoritos.contem(evento.id)  # FASE 4
    dia = agenda.formatar_dia(agenda.hora_local(evento.inicio).date(), hoje)

    conteudo: list[ft.Control] = []
    if evento.imagem:
        conteudo.append(ft.Container(
            ft.Image(src=evento.imagem, height=220, fit=ft.BoxFit.COVER,
                     error_content=ft.Container(height=0)),
            border_radius=theme.RAIO_CARTAO, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        ))
    conteudo += [
        theme.etiqueta_categoria(cfg, evento.categoria),
        theme.titulo(cfg, evento.titulo, 28, selectable=True),
        _linha(app, ft.Icons.CALENDAR_TODAY, f"{dia}, {agenda.formatar_hora(evento)}"),
        _linha(app, ft.Icons.PLACE, evento.local),
    ]
    if evento.preco:
        conteudo.append(_linha(app, ft.Icons.EURO, evento.preco))
    if evento.descricao:
        conteudo.append(ft.Container(
            ft.Text(evento.descricao, selectable=True, size=15, color=cfg.cor_texto_2),
            padding=ft.Padding.only(top=4),
        ))

    conteudo.append(theme.botao(cfg, "Ver na fonte", ft.Icons.OPEN_IN_NEW, url=evento.url,
                                principal=True))
    # FASE 4: mapa, calendário e partilha
    conteudo.append(ft.Row(
        [
            theme.botao(cfg, "Mapa", ft.Icons.MAP,
                        url=agenda.url_mapa(evento, cfg.cidade)),
            theme.botao(cfg, "Calendário", ft.Icons.EVENT_AVAILABLE,
                        url=agenda.url_calendario(evento, cfg.cidade)),
            theme.botao(cfg, "Partilhar", ft.Icons.SHARE,
                        on_click=lambda e: app.pedir_partilha(evento)),
        ],
        wrap=True, spacing=8, run_spacing=8,
    ))
    conteudo.append(theme.secundario(cfg, "Confirma sempre data, hora e preço na fonte.", 12,
                                     italic=True))

    return ft.View(
        route=f"/evento/{evento.id}",
        bgcolor=cfg.cor_fundo,
        appbar=ft.AppBar(
            bgcolor=cfg.cor_fundo,
            force_material_transparency=True,
            title=theme.secundario(cfg, cfg.nome, 15),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.FAVORITE if favorito else ft.Icons.FAVORITE_BORDER,
                    icon_color=cfg.cor_destaque if favorito else cfg.cor_texto,
                    tooltip="Favorito",
                    on_click=lambda e: app.pedir_alternar_favorito(evento),
                )
            ],
        ),
        controls=[ft.Column(conteudo, spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)],
        padding=ft.Padding.only(left=20, right=20, bottom=24),
    )
