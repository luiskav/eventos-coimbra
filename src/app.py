"""Classe App: estado da aplicação e navegação entre ecrãs (Fase 3, tarefa 3.5).

- page.views[0] é a vista principal, com a barra de navegação em baixo
  (Agenda / Favoritos / Sobre).
- O detalhe de um evento é uma segunda vista por cima; o botão Voltar do
  Android (ou a seta da barra) fecha-a através de page.on_view_pop.
"""

import asyncio
import sys
from datetime import datetime

import flet as ft

import agenda
from config import Config, carregar_config
from data import CacheEventos, FonteDados
from favoritos import Favoritos
from theme import FONTES, construir_tema
from views import ecra_arranque, ecra_evento, ecra_favoritos, ecra_sobre
from views.ecra_agenda import EcraAgenda

SEPARADORES = ["agenda", "favoritos", "sobre"]


class App:
    def __init__(self, page: ft.Page, config: Config | None = None,
                 dados: FonteDados | None = None, armazenamento=None):
        self.page = page
        self.config = config or carregar_config()
        self.dados = dados or FonteDados(self.config)
        armazenamento = armazenamento if armazenamento is not None else ft.SharedPreferences()
        # FASE 4: favoritos (antes disso, não há coração nos cartões)
        self.favoritos = Favoritos(armazenamento)
        self.cache = CacheEventos(armazenamento)  # bloco G: cópia local dos eventos
        self.a_carregar = True
        self.eventos = []
        self.separador = 0
        self.evento_aberto = None
        self.ecra_agenda: EcraAgenda | None = None

    # ------------------------------------------------------------------
    async def iniciar(self):
        """Arranque em duas fases (bloco G, passos 26 e 29).

        1. Mostra logo o ecrã de arranque animado e, se houver, os eventos
           guardados no dispositivo da última vez.
        2. Lê os eventos da rede e atualiza o ecrã sem ninguém ter de esperar.
        """
        cfg = self.config
        self.page.title = cfg.nome
        self.page.fonts = FONTES
        self.page.theme = construir_tema(cfg)
        self.page.dark_theme = self.page.theme
        self.page.theme_mode = ft.ThemeMode.DARK
        # Calendário e textos do sistema em português
        self.page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale("pt", "PT")], current_locale=ft.Locale("pt", "PT"))
        self.page.bgcolor = cfg.cor_fundo
        self.page.on_view_pop = self._ao_voltar
        self.page.views.clear()
        self.page.views.append(ecra_arranque.construir(cfg))
        self.page.update()

        await self.favoritos.carregar()  # FASE 4
        guardados = await self.cache.ler()
        if guardados:
            self.eventos = guardados
            self.dados.origem = "cache"
        self.ecra_agenda = EcraAgenda(self)
        self.mostrar()  # agenda com os eventos guardados, ou com cartões cinzentos

        await self.atualizar_da_rede(guardados)

    async def atualizar_da_rede(self, guardados=None):
        if sys.platform == "emscripten":  # no browser não há threads
            await asyncio.sleep(0)  # deixa o ecrã desenhar-se antes do pedido
            eventos = self.dados.carregar()
        else:
            eventos = await asyncio.to_thread(self.dados.carregar)
        if self.dados.origem == "exemplo" and guardados:
            self.dados.origem = "cache"  # sem rede: melhor os guardados do que os de exemplo
        else:
            self.eventos = eventos
            if self.dados.origem == "supabase":
                await self.cache.guardar(eventos)
        self.a_carregar = False
        self.ecra_agenda.atualizar()
        self.mostrar()

    def agora(self) -> datetime:
        return agenda.agora_local()

    # ------------------------------------------------------------------
    # Navegação
    # ------------------------------------------------------------------
    def vista_principal(self) -> ft.View:
        nome = SEPARADORES[self.separador]
        if nome == "agenda":
            conteudo = self.ecra_agenda.controlo
        elif nome == "favoritos":
            conteudo = ecra_favoritos.construir(self)
        else:
            conteudo = ecra_sobre.construir(self)

        cfg = self.config
        return ft.View(
            route="/",
            bgcolor=cfg.cor_fundo,
            controls=[ft.SafeArea(content=conteudo, expand=True)],
            navigation_bar=ft.NavigationBar(
                bgcolor=cfg.cor_superficie,
                indicator_color=ft.Colors.with_opacity(0.18, cfg.cor_destaque),
                elevation=0,
                selected_index=self.separador,
                on_change=self._ao_mudar_separador,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH, label="Agenda"),
                    ft.NavigationBarDestination(icon=ft.Icons.FAVORITE_BORDER,
                                                selected_icon=ft.Icons.FAVORITE,
                                                label="Favoritos"),
                    ft.NavigationBarDestination(icon=ft.Icons.INFO_OUTLINE, label="Sobre"),
                ],
            ),
            padding=0,
        )

    def construir_vistas(self) -> list[ft.View]:
        vistas = [self.vista_principal()]
        if self.evento_aberto is not None:
            vistas.append(ecra_evento.construir(self, self.evento_aberto))
        return vistas

    def mostrar(self):
        self.page.views.clear()
        self.page.views.extend(self.construir_vistas())
        self.page.update()

    def redesenhar(self):
        self.page.update()

    def _ao_mudar_separador(self, e):
        self.separador = int(e.control.selected_index)
        self.mostrar()

    def abrir_evento(self, evento):
        self.evento_aberto = evento
        self.mostrar()

    def fechar_evento(self):
        self.evento_aberto = None
        self.mostrar()

    def _ao_voltar(self, e):
        self.fechar_evento()

    def recarregar(self):
        self.a_carregar = True
        self._agendar(self.atualizar_da_rede, self.eventos)

    # ------------------------------------------------------------------
    # FASE 4: ações assíncronas (favoritos e partilha)
    # ------------------------------------------------------------------
    def _agendar(self, funcao, *args):
        self.page.run_task(funcao, *args)

    def pedir_alternar_favorito(self, evento):
        self._agendar(self.alternar_favorito, evento)

    async def alternar_favorito(self, evento):
        await self.favoritos.alternar(evento.id)
        self.ecra_agenda.atualizar()
        self.mostrar()

    def pedir_partilha(self, evento):
        self._agendar(self.partilhar, evento)

    async def partilhar(self, evento):
        await self._partilhar_texto(agenda.texto_partilha(evento, self.config.nome),
                                    evento.titulo)

    def pedir_partilha_app(self):
        self._agendar(self.partilhar_app)

    async def partilhar_app(self):
        cfg = self.config
        texto = f"{cfg.nome}: {cfg.slogan}"
        if cfg.url_site:
            texto += f"\n{cfg.url_site}"
        await self._partilhar_texto(texto, cfg.nome)

    async def _partilhar_texto(self, texto: str, assunto: str):
        try:
            await ft.Share().share_text(texto, subject=assunto)
        except Exception:
            # Sem partilha nativa (alguns browsers): copia para a área de transferência
            await ft.Clipboard().set(texto)
            self.page.show_dialog(ft.SnackBar(ft.Text("Texto copiado. Já podes colar.")))
