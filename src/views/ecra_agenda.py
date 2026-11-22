"""Ecrã principal: lista de eventos com filtros (Fase 3, tarefas 3.6 e 3.7; pesquisa na
Fase 4; novo aspeto no bloco G, passo 28).

É uma classe porque guarda o estado dos filtros e só redesenha a lista quando
algo muda (assim a caixa de pesquisa não perde o foco enquanto se escreve).
O cabeçalho (título grande, pesquisa e filtros) é o primeiro elemento da lista,
por isso desliza com os eventos, como nas apps da Apple.
"""

import flet as ft

import agenda
import theme
from views.componentes import cabecalho_dia, cartao_esqueleto, cartao_evento, mensagem_vazia

TITULOS = {
    "hoje": "Hoje em {cidade}",
    "fim_de_semana": "Este fim de semana",
    "30_dias": "Próximos 30 dias",
}
POR_PAGINA = 60  # cartões desenhados de cada vez; "Ver mais" mostra os seguintes


class EcraAgenda:
    def __init__(self, app):
        self.app = app
        cfg = app.config
        self.periodo = "hoje"
        self.categoria: str | None = None
        self.texto = ""
        self.limite = POR_PAGINA

        self.titulo = theme.titulo(cfg, "", 32)
        self.subtitulo = theme.secundario(cfg, "", 14)
        # FASE 4: pesquisa por texto
        self.pesquisa = ft.TextField(
            hint_text="Pesquisar evento ou local",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            filled=True,
            fill_color=cfg.cor_superficie_2,
            border=ft.NoInputBorder(),
            border_radius=14,
            color=cfg.cor_texto,
            cursor_color=cfg.cor_destaque,
            hint_style=ft.TextStyle(color=cfg.cor_texto_2),
            on_change=self._ao_pesquisar,
        )
        self.linha_periodos = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=8)
        self.linha_categorias = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=8)
        self.aviso = ft.Container(visible=False)
        self.cabecalho = ft.Container(
            content=ft.Column(
                [self.subtitulo, self.titulo, self.pesquisa, self.linha_periodos,
                 self.linha_categorias, self.aviso],
                spacing=12,
            ),
            padding=ft.Padding.only(left=20, right=20, top=12, bottom=4),
        )
        self.lista = ft.ListView(expand=True, spacing=0, padding=ft.Padding.only(bottom=24))
        self.controlo = self.lista
        self.atualizar()

    # ----- eventos da interface -----
    def _ao_pesquisar(self, e):
        self.texto = e.control.value or ""
        self.limite = POR_PAGINA
        self.atualizar(redesenhar=True)

    def _escolher_periodo(self, periodo: str):
        self.periodo = periodo
        self.limite = POR_PAGINA
        self.atualizar(redesenhar=True)

    def _escolher_categoria(self, categoria: str | None):
        self.categoria = None if categoria == self.categoria else categoria
        self.limite = POR_PAGINA
        self.atualizar(redesenhar=True)

    def _ver_mais(self, e=None):
        self.limite += POR_PAGINA
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

    def _desenhar_cabecalho(self):
        cfg = self.app.config
        agora = self.app.agora()
        self.titulo.value = TITULOS[self.periodo].format(cidade=cfg.cidade)
        self.subtitulo.value = (f"{agenda.DIAS[agora.weekday()].capitalize()}, "
                                f"{agora.day} de {agenda.MESES[agora.month - 1]}")
        self.linha_periodos.controls = [
            theme.pilula(cfg, rotulo, codigo == self.periodo,
                         on_click=lambda e, c=codigo: self._escolher_periodo(c))
            for codigo, rotulo in agenda.PERIODOS.items()
        ]
        self.linha_categorias.controls = [
            theme.pilula(cfg, rotulo, codigo == self.categoria,
                         icone=theme.icone_categoria(codigo),
                         on_click=lambda e, c=codigo: self._escolher_categoria(c))
            for codigo, rotulo in cfg.categorias.items()
        ]
        if self.app.dados.origem == "exemplo":
            self.aviso.content = theme.secundario(
                cfg, "Sem ligação: a mostrar eventos de exemplo.", 13,
                color="#FFB4B0")
            self.aviso.bgcolor = "#3A1517"
            self.aviso.padding = ft.Padding.symmetric(horizontal=12, vertical=8)
            self.aviso.border_radius = 12
            self.aviso.visible = True
        else:
            self.aviso.visible = False

    def atualizar(self, redesenhar: bool = False):
        self._desenhar_cabecalho()
        controlos: list[ft.Control] = [self.cabecalho]

        if self.app.a_carregar and not self.app.eventos:
            controlos += [cartao_esqueleto(self.app) for _ in range(4)]
        else:
            hoje = self.app.agora().date()
            visiveis = self.eventos_visiveis()
            desde = agenda.intervalo(self.periodo, self.app.agora())[0].date()
            for dia, eventos in agenda.agrupar_por_dia(visiveis[: self.limite], desde):
                controlos.append(cabecalho_dia(self.app, dia, hoje))
                controlos.extend(cartao_evento(self.app, ev, hoje) for ev in eventos)
            if len(visiveis) > self.limite:
                controlos.append(ft.Container(
                    theme.botao(self.app.config, f"Ver mais ({len(visiveis) - self.limite})",
                                on_click=self._ver_mais),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    alignment=ft.Alignment.CENTER,
                ))
            if not visiveis:
                controlos.append(mensagem_vazia(self.app, "Não há eventos para estes filtros."))
        self.lista.controls = controlos

        if redesenhar:
            self.app.redesenhar()
