"""Peças de interface reutilizadas por vários ecrãs (Fase 3, tarefa 3.6)."""

from datetime import date

import flet as ft

import agenda
from models import Evento
from theme import icone_categoria


def cabecalho_dia(dia: date, hoje: date) -> ft.Control:
    return ft.Container(
        content=ft.Text(agenda.formatar_dia(dia, hoje), weight=ft.FontWeight.BOLD, size=16),
        padding=ft.Padding.only(left=16, top=16, bottom=4),
    )


def cartao_evento(app, evento: Evento, hoje: date, mostrar_dia: bool = False) -> ft.Control:
    cor = app.config.cor_categoria(evento.categoria)
    linha = agenda.resumo(evento, hoje) if mostrar_dia else (
        f"{agenda.formatar_hora(evento)} · {evento.local}"
    )
    favorito = app.favoritos.contem(evento.id)  # FASE 4
    return ft.Card(
        content=ft.ListTile(
            leading=ft.Icon(icone_categoria(evento.categoria), color=cor),
            title=ft.Text(evento.titulo, weight=ft.FontWeight.W_600, max_lines=2),
            subtitle=ft.Text(linha, max_lines=2),
            # FASE 4: coração para guardar nos favoritos
            trailing=ft.IconButton(
                icon=ft.Icons.FAVORITE if favorito else ft.Icons.FAVORITE_BORDER,
                icon_color=cor if favorito else None,
                tooltip="Remover dos favoritos" if favorito else "Guardar nos favoritos",
                on_click=lambda e: app.pedir_alternar_favorito(evento),
            ),
            on_click=lambda e: app.abrir_evento(evento),
        ),
        margin=ft.Margin.symmetric(horizontal=12, vertical=4),
    )


def mensagem_vazia(texto: str, icone=ft.Icons.EVENT_BUSY) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [ft.Icon(icone, size=48, color=ft.Colors.OUTLINE),
             ft.Text(texto, text_align=ft.TextAlign.CENTER)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=40,
        alignment=ft.Alignment.CENTER,
    )
