"""Testes dos ecrãs sem abrir janela (Fase 3, tarefa 3.10; Fase 4).

Constroem os controlos com uma página falsa e verificam o que lá aparece.
"""

import asyncio
from datetime import datetime

import flet as ft

from app import App
from data import FonteDados
from tests.test_favoritos import ArmazenamentoFalso
from views import ecra_evento, ecra_favoritos, ecra_sobre
from views.ecra_agenda import EcraAgenda

AGORA = datetime(2026, 11, 16, 9, 0)


class PaginaFalsa:
    def __init__(self):
        self.views, self.atualizacoes, self.tarefas = [], 0, []
        self.title = self.theme = self.on_view_pop = None

    def update(self):
        self.atualizacoes += 1

    def run_task(self, funcao, *args):
        self.tarefas.append(funcao)
        asyncio.run(funcao(*args))

    def show_dialog(self, dialogo):
        pass


class AppTeste(App):
    def agora(self):
        return AGORA


def criar_app(config, eventos):
    pagina = PaginaFalsa()
    dados = FonteDados(config, http_get=lambda url, cab: [])
    app = AppTeste(pagina, config=config, dados=dados, armazenamento=ArmazenamentoFalso())
    asyncio.run(app.iniciar())
    app.eventos = eventos
    app.ecra_agenda.atualizar()
    return app, pagina


def textos(controlo) -> list[str]:
    """Todos os textos dentro de um controlo (procura recursiva)."""
    encontrados = []

    def visitar(c):
        if isinstance(c, ft.Text) and c.value:
            encontrados.append(c.value)
        for nome in ("content", "controls", "title", "subtitle", "leading", "trailing",
                     "label"):
            filho = getattr(c, nome, None)
            if isinstance(filho, list):
                for f in filho:
                    visitar(f)
            elif isinstance(filho, ft.Control):
                visitar(filho)

    visitar(controlo)
    return encontrados


def test_agenda_mostra_dias_e_eventos(config, eventos):
    app, pagina = criar_app(config, eventos)
    t = textos(app.ecra_agenda.lista)
    assert "Hoje" in t and "Concerto de Fado" in t
    assert "Festival de Inverno" not in t  # está a mais de 30 dias
    assert len(pagina.views) == 1


def test_agenda_filtra_por_categoria_e_texto(config, eventos):
    app, _ = criar_app(config, eventos)
    ecra: EcraAgenda = app.ecra_agenda
    ecra._escolher_categoria("teatro")
    assert "Peça Infantil" in textos(ecra.lista) and "Concerto de Fado" not in textos(ecra.lista)
    ecra._escolher_categoria("teatro")  # segundo toque limpa o filtro
    ecra.texto = "zzz"
    ecra.atualizar()
    assert "Não há eventos para estes filtros." in textos(ecra.lista)


def test_abrir_e_fechar_evento(config, eventos):
    app, pagina = criar_app(config, eventos)
    app.abrir_evento(eventos[0])
    assert len(pagina.views) == 2 and pagina.views[1].route == "/evento/1"
    assert "Concerto de Fado" in textos(pagina.views[1].controls[0])
    app._ao_voltar(None)
    assert len(pagina.views) == 1


def test_detalhe_tem_links(config, eventos):
    app, _ = criar_app(config, eventos)
    vista = ecra_evento.construir(app, eventos[0])
    coluna = vista.controls[0]
    urls = [c.url for c in coluna.controls if getattr(c, "url", None)]
    urls += [b.url for c in coluna.controls if isinstance(c, ft.Row)
             for b in c.controls if getattr(b, "url", None)]
    assert eventos[0].url in urls
    assert any("google.com/maps" in u for u in urls)
    assert any("calendar.google.com" in u for u in urls)


def test_favoritos(config, eventos):
    app, pagina = criar_app(config, eventos)
    assert "Ainda não guardaste eventos." in " ".join(textos(ecra_favoritos.construir(app)))
    app.pedir_alternar_favorito(eventos[2])
    assert app.favoritos.contem(3)
    assert "Jazz no Largo" in textos(ecra_favoritos.construir(app))


def test_mudar_separador_e_sobre(config, eventos):
    app, pagina = criar_app(config, eventos)

    class E:
        control = type("C", (), {"selected_index": 2})()

    app._ao_mudar_separador(E())
    assert app.separador == 2 and pagina.views[0].navigation_bar.selected_index == 2
    assert "Eventos Teste" in textos(ecra_sobre.construir(app))
