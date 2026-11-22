"""Peças de interface reutilizadas por vários ecrãs (Fase 3, tarefa 3.6; bloco G, 26 e 28)."""

from datetime import date

import flet as ft

import agenda
import theme
from models import Evento


def cabecalho_dia(app, dia: date, hoje: date) -> ft.Control:
    cfg = app.config
    return ft.Container(
        content=theme.destaque(cfg, agenda.formatar_dia(dia, hoje), 17),
        padding=ft.Padding.only(left=20, top=22, bottom=8),
    )


def _data_em_bloco(app, evento: Evento) -> ft.Control:
    """Quadrado com o dia em grande e o mês por baixo (ex.: 21 / NOV)."""
    cfg = app.config
    local = agenda.hora_local(evento.inicio)
    return ft.Container(
        content=ft.Column(
            [ft.Text(str(local.day), size=22, font_family=cfg.fonte_titulos,
                     color=cfg.cor_texto),
             ft.Text(agenda.MESES[local.month - 1][:3].upper(), size=11,
                     font_family=cfg.fonte_destaque, color=cfg.cor_destaque)],
            spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=56, height=60, bgcolor=cfg.cor_superficie_2, border_radius=14,
    )


def cartao_evento(app, evento: Evento, hoje: date, mostrar_dia: bool = False) -> ft.Control:
    cfg = app.config
    linha = agenda.resumo(evento, hoje) if mostrar_dia else (
        f"{agenda.formatar_hora(evento)} · {evento.local}"
    )
    favorito = app.favoritos.contem(evento.id)  # FASE 4

    corpo = ft.Row(
        [
            _data_em_bloco(app, evento),
            ft.Column(
                [
                    theme.etiqueta_categoria(cfg, evento.categoria),
                    theme.destaque(cfg, evento.titulo, 16, max_lines=2,
                                   overflow=ft.TextOverflow.ELLIPSIS),
                    theme.secundario(cfg, linha, 13, max_lines=1,
                                     overflow=ft.TextOverflow.ELLIPSIS),
                ],
                spacing=6, expand=True,
            ),
            # FASE 4: coração para guardar nos favoritos
            ft.IconButton(
                icon=ft.Icons.FAVORITE if favorito else ft.Icons.FAVORITE_BORDER,
                icon_color=cfg.cor_destaque if favorito else cfg.cor_texto_2,
                tooltip="Remover dos favoritos" if favorito else "Guardar nos favoritos",
                on_click=lambda e: app.pedir_alternar_favorito(evento),
            ),
        ],
        spacing=14, vertical_alignment=ft.CrossAxisAlignment.START,
    )

    partes: list[ft.Control] = []
    if evento.imagem:
        partes.append(ft.Image(
            src=evento.imagem, height=150, fit=ft.BoxFit.COVER,
            error_content=ft.Container(height=0),
        ))
    partes.append(ft.Container(corpo, padding=ft.Padding.only(left=14, top=14, right=4,
                                                               bottom=14)))
    return ft.Container(
        content=ft.Column(partes, spacing=0),
        bgcolor=cfg.cor_superficie,
        border_radius=theme.RAIO_CARTAO,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        margin=ft.Margin.symmetric(horizontal=16, vertical=6),
        on_click=lambda e: app.abrir_evento(evento),
        ink=True,
    )


def cartao_esqueleto(app) -> ft.Control:
    """Cartão cinzento mostrado enquanto os eventos chegam (passo 26)."""
    cfg = app.config

    def barra(largura, altura=12):
        return ft.Container(width=largura, height=altura, bgcolor=cfg.cor_superficie_2,
                            border_radius=6)

    return ft.Container(
        content=ft.Row(
            [ft.Container(width=56, height=60, bgcolor=cfg.cor_superficie_2,
                          border_radius=14),
             ft.Column([barra(70, 10), barra(200, 14), barra(140, 10)], spacing=10)],
            spacing=14,
        ),
        bgcolor=cfg.cor_superficie, border_radius=theme.RAIO_CARTAO, padding=14,
        margin=ft.Margin.symmetric(horizontal=16, vertical=6),
        opacity=0.7,
    )


def mensagem_vazia(app, texto: str, icone=ft.Icons.EVENT_BUSY) -> ft.Control:
    cfg = app.config
    return ft.Container(
        content=ft.Column(
            [ft.Icon(icone, size=44, color=cfg.cor_texto_2),
             theme.secundario(cfg, texto, 15, text_align=ft.TextAlign.CENTER)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
        ),
        padding=48,
        alignment=ft.Alignment.CENTER,
    )
