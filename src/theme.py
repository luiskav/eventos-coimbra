"""Ícones das categorias (Fase 3, tarefa 3.6) e tema escuro (bloco G, passo 27).

Todas as cores e letras vêm do config.json (ver docs/DESIGN.md). Os ecrãs não
escrevem cores à mão: usam as funções daqui, para o aspeto ser igual em todo o lado.
"""

import flet as ft

from config import Config

ICONES_CATEGORIAS = {
    "musica": ft.Icons.MUSIC_NOTE,
    "teatro": ft.Icons.THEATER_COMEDY,
    "exposicao": ft.Icons.PALETTE,
    "desporto": ft.Icons.SPORTS_SOCCER,
    "academico": ft.Icons.SCHOOL,
    "familia": ft.Icons.FAMILY_RESTROOM,
    "feira": ft.Icons.STOREFRONT,
    "cinema": ft.Icons.MOVIE,
    "outro": ft.Icons.EVENT,
}

# Letras incluídas em src/assets/fonts (Inter, licença SIL OFL, subconjunto latino).
# O Flet associa um ficheiro a cada nome; por isso cada peso tem o seu nome.
FONTES = {
    "Inter": "fonts/Inter-Regular.ttf",
    "InterSemi": "fonts/Inter-SemiBold.ttf",
    "InterDisplay": "fonts/InterDisplay-Bold.ttf",
}

RAIO_CARTAO = 20
RAIO_PILULA = 999


def icone_categoria(codigo: str):
    return ICONES_CATEGORIAS.get(codigo, ft.Icons.EVENT)


def construir_tema(config: Config) -> ft.Theme:
    c = config
    return ft.Theme(
        use_material3=True,
        font_family=c.fonte_texto,
        scaffold_bgcolor=c.cor_fundo,
        card_bgcolor=c.cor_superficie,
        canvas_color=c.cor_fundo,
        divider_color=c.cor_superficie_2,
        color_scheme=ft.ColorScheme(
            primary=c.cor_destaque,
            on_primary=c.cor_fundo,
            secondary=c.cor_destaque,
            on_secondary=c.cor_fundo,
            surface=c.cor_fundo,
            on_surface=c.cor_texto,
            on_surface_variant=c.cor_texto_2,
            surface_container=c.cor_superficie,
            outline=c.cor_superficie_2,
            outline_variant=c.cor_superficie_2,
            error="#FF6B6B",
            error_container="#3A1517",
            on_error_container="#FFB4B0",
        ),
    )


# ---------------------------------------------------------------------------
# Texto: três níveis, sempre com as letras do tema
# ---------------------------------------------------------------------------


def titulo(config: Config, texto: str, tamanho: int = 30, **kw) -> ft.Text:
    """Títulos grandes, estilo 'Hoje em Coimbra'."""
    return ft.Text(texto, size=tamanho, font_family=config.fonte_titulos,
                   color=config.cor_texto, **kw)


def destaque(config: Config, texto: str, tamanho: int = 16, **kw) -> ft.Text:
    return ft.Text(texto, size=tamanho, font_family=config.fonte_destaque,
                   color=kw.pop("color", config.cor_texto), **kw)


def secundario(config: Config, texto: str, tamanho: int = 13, **kw) -> ft.Text:
    return ft.Text(texto, size=tamanho, font_family=config.fonte_texto,
                   color=kw.pop("color", config.cor_texto_2), **kw)


# ---------------------------------------------------------------------------
# Peças comuns
# ---------------------------------------------------------------------------


def pilula(config: Config, texto: str, selecionada: bool, on_click=None,
           icone=None) -> ft.Container:
    """Filtro em forma de pílula (substitui o Chip do Material)."""
    cor_texto = config.cor_fundo if selecionada else config.cor_texto
    conteudo: list[ft.Control] = []
    if icone:
        conteudo.append(ft.Icon(icone, size=16, color=cor_texto))
    conteudo.append(ft.Text(texto, size=14, font_family=config.fonte_destaque,
                            color=cor_texto))
    return ft.Container(
        content=ft.Row(conteudo, spacing=6, tight=True),
        bgcolor=config.cor_destaque if selecionada else config.cor_superficie_2,
        border_radius=RAIO_PILULA,
        padding=ft.Padding.symmetric(horizontal=14, vertical=8),
        on_click=on_click,
        ink=True,
    )


def etiqueta_categoria(config: Config, codigo: str) -> ft.Container:
    cor = config.cor_categoria(codigo)
    return ft.Container(
        content=ft.Row(
            [ft.Icon(icone_categoria(codigo), size=14, color=cor),
             ft.Text(config.rotulo_categoria(codigo), size=12,
                     font_family=config.fonte_destaque, color=cor)],
            spacing=4, tight=True,
        ),
        bgcolor=ft.Colors.with_opacity(0.14, cor),
        border_radius=RAIO_PILULA,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )


def botao(config: Config, texto: str, icone=None, url: str | None = None,
          on_click=None, principal: bool = False) -> ft.Container:
    """Botão em pílula. O principal usa a cor de destaque; os outros, a superfície."""
    cor_texto = config.cor_fundo if principal else config.cor_texto
    conteudo: list[ft.Control] = []
    if icone:
        conteudo.append(ft.Icon(icone, size=18, color=cor_texto))
    conteudo.append(ft.Text(texto, size=15, font_family=config.fonte_destaque,
                            color=cor_texto))
    return ft.Container(
        content=ft.Row(conteudo, spacing=8, tight=True,
                       alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=config.cor_destaque if principal else config.cor_superficie_2,
        border_radius=RAIO_PILULA,
        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        url=url,
        on_click=on_click,
        ink=True,
    )
