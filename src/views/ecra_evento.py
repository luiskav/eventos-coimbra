"""Ecrã de detalhe de um evento (Fase 3, tarefa 3.8; botões extra na Fase 4, tarefa 4.4)."""

import flet as ft

import agenda
from models import Evento
from theme import icone_categoria


def _linha(icone, texto: str) -> ft.Control:
    return ft.Row(
        [ft.Icon(icone, size=20), ft.Text(texto, expand=True, selectable=True)],
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


def construir(app, evento: Evento) -> ft.View:
    hoje = app.agora().date()
    cor = app.config.cor_categoria(evento.categoria)
    favorito = app.favoritos.contem(evento.id)  # FASE 4
    dia = agenda.formatar_dia(agenda.hora_local(evento.inicio).date(), hoje)

    conteudo = [
        ft.Container(
            content=ft.Row(
                [ft.Icon(icone_categoria(evento.categoria), color=ft.Colors.WHITE, size=18),
                 ft.Text(app.config.rotulo_categoria(evento.categoria), color=ft.Colors.WHITE)],
                tight=True,
            ),
            bgcolor=cor,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=12,
        ),
        ft.Text(evento.titulo, size=24, weight=ft.FontWeight.BOLD, selectable=True),
        _linha(ft.Icons.CALENDAR_TODAY, f"{dia}, {agenda.formatar_hora(evento)}"),
        _linha(ft.Icons.PLACE, evento.local),
    ]
    if evento.preco:
        conteudo.append(_linha(ft.Icons.EURO, evento.preco))
    if evento.imagem:
        conteudo.append(ft.Image(src=evento.imagem, border_radius=8, fit=ft.BoxFit.COVER,
                                 height=200))
    if evento.descricao:
        conteudo.append(ft.Text(evento.descricao, selectable=True))

    conteudo.append(
        ft.Button(
            content=ft.Text("Ver na fonte"),
            icon=ft.Icons.OPEN_IN_NEW,
            url=evento.url,
        )
    )
    # FASE 4: mapa, calendário e partilha
    conteudo.append(
        ft.Row(
            [
                ft.OutlinedButton(
                    content=ft.Text("Mapa"), icon=ft.Icons.MAP,
                    url=agenda.url_mapa(evento, app.config.cidade),
                ),
                ft.OutlinedButton(
                    content=ft.Text("Calendário"), icon=ft.Icons.EVENT_AVAILABLE,
                    url=agenda.url_calendario(evento, app.config.cidade),
                ),
                ft.OutlinedButton(
                    content=ft.Text("Partilhar"), icon=ft.Icons.SHARE,
                    on_click=lambda e: app.pedir_partilha(evento),
                ),
            ],
            wrap=True,
        )
    )
    conteudo.append(
        ft.Text("Confirma sempre data, hora e preço na fonte.", size=12,
                color=ft.Colors.OUTLINE, italic=True)
    )

    return ft.View(
        route=f"/evento/{evento.id}",
        appbar=ft.AppBar(
            title=ft.Text(app.config.nome),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.FAVORITE if favorito else ft.Icons.FAVORITE_BORDER,
                    tooltip="Favorito",
                    on_click=lambda e: app.pedir_alternar_favorito(evento),
                )
            ],
        ),
        controls=[ft.Column(conteudo, spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)],
        padding=16,
    )
