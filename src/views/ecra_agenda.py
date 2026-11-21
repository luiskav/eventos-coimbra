"""Ecrã principal: lista de eventos com filtros (Fase 3, tarefas 3.6 e 3.7; pesquisa na Fase 4).

É uma classe porque guarda o estado dos filtros e só redesenha a lista quando
algo muda (assim a caixa de pesquisa não perde o foco enquanto se escreve).
"""

import flet as ft

import agenda
from views.componentes import cabecalho_dia, cartao_evento, mensagem_vazia


class EcraAgenda:
    def __init__(self, app):
        self.app = app
        self.periodo = "30_dias"
        self.categoria: str | None = None
        self.texto = ""

        # FASE 4: pesquisa por texto
        self.pesquisa = ft.TextField(
            hint_text="Pesquisar evento ou local",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            on_change=self._ao_pesquisar,
        )
        self.linha_periodos = ft.Row(scroll=ft.ScrollMode.AUTO)
        self.linha_categorias = ft.Row(scroll=ft.ScrollMode.AUTO)
        self.aviso = ft.Container(visible=False)
        self.lista = ft.ListView(expand=True, spacing=0, padding=ft.Padding.only(bottom=16))
        self.controlo = ft.Column(
            [
                ft.Container(self.pesquisa, padding=ft.Padding.only(left=12, right=12, top=8)),
                ft.Container(self.linha_periodos, padding=ft.Padding.symmetric(horizontal=12)),
                ft.Container(self.linha_categorias, padding=ft.Padding.symmetric(horizontal=12)),
                self.aviso,
                self.lista,
            ],
            expand=True,
            spacing=4,
        )
        self.atualizar()

    # ----- eventos da interface -----
    def _ao_pesquisar(self, e):
        self.texto = e.control.value or ""
        self.atualizar(redesenhar=True)

    def _escolher_periodo(self, periodo: str):
        self.periodo = periodo
        self.atualizar(redesenhar=True)

    def _escolher_categoria(self, categoria: str | None):
        self.categoria = None if categoria == self.categoria else categoria
        self.atualizar(redesenhar=True)

    # ----- desenho -----
    def eventos_visiveis(self):
        return agenda.filtrar(
            self.app.eventos,
            periodo=self.periodo,
            categoria=self.categoria,
            texto=self.texto,
            agora=self.app.agora(),
        )

    def atualizar(self, redesenhar: bool = False):
        self.linha_periodos.controls = [
            ft.Chip(
                label=ft.Text(rotulo),
                selected=codigo == self.periodo,
                on_select=lambda e, c=codigo: self._escolher_periodo(c),
            )
            for codigo, rotulo in agenda.PERIODOS.items()
        ]
        self.linha_categorias.controls = [
            ft.Chip(
                label=ft.Text(rotulo),
                selected=codigo == self.categoria,
                on_select=lambda e, c=codigo: self._escolher_categoria(c),
            )
            for codigo, rotulo in self.app.config.categorias.items()
        ]

        if self.app.dados.origem == "exemplo":
            self.aviso.content = ft.Text(
                "Sem ligação: a mostrar eventos de exemplo.", color=ft.Colors.ON_ERROR_CONTAINER
            )
            self.aviso.bgcolor = ft.Colors.ERROR_CONTAINER
            self.aviso.padding = 8
            self.aviso.visible = True
        else:
            self.aviso.visible = False

        hoje = self.app.agora().date()
        visiveis = self.eventos_visiveis()
        controlos = []
        for dia, eventos in agenda.agrupar_por_dia(visiveis):
            controlos.append(cabecalho_dia(dia, hoje))
            controlos.extend(cartao_evento(self.app, ev, hoje) for ev in eventos)
        if not controlos:
            controlos = [mensagem_vazia("Não há eventos para estes filtros.")]
        self.lista.controls = controlos

        if redesenhar:
            self.app.redesenhar()
