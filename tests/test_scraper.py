"""Testes do scraper sem rede e sem gastar a chave (Fase 2, tarefas 2.3 a 2.8)."""

import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
import pytest

from scraper import extract, fetch, run
from scraper.models import EventoExtraido, validar_eventos
from scraper.normalize import chave_evento, normalizar
from scraper.store import Armazem, ErroArmazem

FIXTURES = run.FIXTURES
AGORA = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)


# ---------- normalize (2.6) ----------
def test_normalizar():
    assert normalizar("Concerto: Fado à Noite!") == "concerto fado a noite"


def test_chave_estavel_e_tolerante():
    inicio = datetime(2026, 12, 5, 21, 30, tzinfo=UTC)
    a = chave_evento("Fado à Noite", inicio, "Teatro da Cerca")
    b = chave_evento("  FADO À NOITE!! ", inicio, "teatro  da  cerca")
    assert a == b == "fado-noite|202612052130|teatro-cerca"
    assert a != chave_evento("Fado à Noite", inicio + timedelta(days=1), "Teatro da Cerca")


# ---------- fetch (2.2, 2.3) ----------
def test_limpar_html_tira_lixo_e_mantem_links():
    html = (FIXTURES / "exemplo.html").read_text(encoding="utf-8")
    texto = fetch.limpar_html(html, "https://example.org/agenda/", "#agenda")
    assert "Concerto de Inverno [link: https://example.org/agenda/concerto-de-inverno]" in texto
    assert "[imagem: https://example.org/img/concerto.jpg]" in texto
    assert "console.log" not in texto and "Início" not in texto and "info@" not in texto
    assert "\n\n\n" not in texto


def test_limpar_html_sem_seletor_e_corte():
    html = "<html><body><header>Menu</header><p>" + "a" * 500 + "</p></body></html>"
    texto = fetch.limpar_html(html, "https://x.pt/", max_caracteres=100)
    assert len(texto) == 100 and "Menu" not in texto


def transporte(rotas: dict):
    def responder(pedido: httpx.Request):
        resposta = rotas.get(str(pedido.url))
        if resposta is None:
            return httpx.Response(404)
        estado, corpo = resposta
        return httpx.Response(estado, text=corpo)

    return httpx.MockTransport(responder)


def test_robots_bloqueia_e_permite():
    rotas = {"https://a.pt/robots.txt": (200, "User-agent: *\nDisallow: /privado/\n"),
             "https://a.pt/agenda/": (200, "<p>ok</p>")}
    with fetch.novo_cliente(transporte(rotas)) as cliente:
        assert fetch.pode_visitar("https://a.pt/agenda/", cliente)
        assert not fetch.pode_visitar("https://a.pt/privado/x", cliente)
        assert fetch.obter_pagina("https://a.pt/agenda/", cliente) == "<p>ok</p>"
        with pytest.raises(fetch.ErroRecolha):
            fetch.obter_pagina("https://a.pt/privado/x", cliente)


def test_sem_robots_permite_e_erro_http():
    rotas = {"https://b.pt/agenda/": (500, "erro")}
    with fetch.novo_cliente(transporte(rotas)) as cliente:
        assert fetch.pode_visitar("https://b.pt/agenda/", cliente)  # robots 404
        with pytest.raises(fetch.ErroRecolha):
            fetch.obter_pagina("https://b.pt/agenda/", cliente)


# ---------- extract (2.4) ----------
class ClaudeFalso:
    def __init__(self, eventos):
        self.pedidos = []
        self.messages = self
        self.eventos = eventos

    def create(self, **kwargs):
        self.pedidos.append(kwargs)
        bloco = SimpleNamespace(type="tool_use", input={"eventos": self.eventos})
        return SimpleNamespace(content=[bloco],
                               usage=SimpleNamespace(input_tokens=1200, output_tokens=300))


def test_extrair_eventos_usa_ferramenta():
    falso = ClaudeFalso([{"titulo": "A"}])
    r = extract.extrair_eventos("texto da página", "Sala X", "2026-11-16", cliente=falso)
    assert r.eventos == [{"titulo": "A"}] and r.tokens_entrada == 1200
    pedido = falso.pedidos[0]
    assert pedido["model"] == "claude-haiku-5-5"
    assert pedido["tool_choice"] == {"type": "tool", "name": "guardar_eventos"}
    conteudo = pedido["messages"][0]["content"]
    assert "Hoje é 2026-11-16" in conteudo and "texto da página" in conteudo


# ---------- models (2.5) ----------
def test_validar_converte_hora_de_lisboa_e_urls():
    brutos = [
        {"titulo": "Verão", "inicio": "2027-07-04T21:30:00", "local": "Sala",
         "categoria": "Música", "url": "/e/1"},
        {"titulo": "Inverno", "inicio": "2026-12-05T21:30:00", "local": "Sala",
         "categoria": "exposição", "url": "https://x.pt/e/2", "fim": "2026-12-05T20:00:00"},
    ]
    validos, rejeitados = validar_eventos(brutos, "https://x.pt/agenda/", AGORA)
    assert rejeitados == []
    verao, inverno = validos
    assert verao.inicio == datetime(2027, 7, 4, 20, 30, tzinfo=UTC)  # Lisboa +1 no verão
    assert verao.url == "https://x.pt/e/1" and verao.categoria == "musica"  # 'Música' -> 'musica'
    assert inverno.categoria == "exposicao" and inverno.fim is None  # fim antes do início


def test_validar_rejeita():
    brutos = [
        {"titulo": "Antigo", "inicio": "2020-01-01T10:00:00", "local": "S", "url": "https://x"},
        {"titulo": "Longe", "inicio": "2030-01-01T10:00:00", "local": "Sala", "url": "https://x"},
        {"titulo": "Sem data", "local": "Sala", "url": "https://x"},
        {"titulo": "Sem url", "inicio": "2026-12-01T10:00:00", "local": "Sala",
         "url": "mailto:a@b"},
    ]
    validos, rejeitados = validar_eventos(brutos, "", AGORA)
    assert validos == [] and len(rejeitados) == 4


def test_descricao_cortada():
    ev = EventoExtraido(titulo="Teste", inicio="2026-12-01T10:00:00", local="Sala",
                        url="https://x", descricao="a " * 400)
    assert len(ev.descricao) == 300 and ev.descricao.endswith("...")


# ---------- store (2.6, 2.7) ----------
def test_armazem_grava_e_conta_novos():
    pedidos = []

    def responder(pedido: httpx.Request):
        pedidos.append(pedido)
        if pedido.url.path.endswith("/sources"):
            return httpx.Response(201, json=[{"id": 42}])
        if pedido.method == "GET":
            return httpx.Response(200, json=[{"chave": "concerto|202612052130|sala"}])
        return httpx.Response(201)

    armazem = Armazem("https://p.supabase.co", "service", httpx.MockTransport(responder))
    eventos, _ = validar_eventos(
        [{"titulo": "Concerto", "inicio": "2026-12-05T21:30:00", "local": "Sala", "url": "https://x"},
         {"titulo": "Concerto", "inicio": "2026-12-05T21:30:00", "local": "Sala", "url": "https://x"},
         {"titulo": "Teatro", "inicio": "2026-12-06T21:00:00", "local": "Sala", "url": "https://y"}],
        "", AGORA,
    )
    fonte_id = armazem.garantir_fonte({"id": "sala", "nome": "Sala", "ativa": True})
    novos = armazem.gravar_eventos(fonte_id, eventos)
    assert fonte_id == 42 and novos == 1
    post = pedidos[-1]
    assert post.url.params["on_conflict"] == "chave"
    assert "merge-duplicates" in post.headers["Prefer"]
    linhas = json.loads(post.content)
    assert len(linhas) == 2 and all("estado" not in linha for linha in linhas)
    assert pedidos[0].headers["Authorization"] == "Bearer service"


def test_armazem_erro_e_sem_chaves():
    with pytest.raises(ErroArmazem):
        Armazem("", "")
    armazem = Armazem("https://p.supabase.co", "k",
                      httpx.MockTransport(lambda r: httpx.Response(401, text="nope")))
    with pytest.raises(ErroArmazem):
        armazem.registar_execucao({"estado": "ok"})


# ---------- run (2.8): ensaio completo, offline ----------
def test_run_ensaio_offline(capsys):
    codigo = run.main(["--fonte", "exemplo", "--ensaio", "--offline",
                       "--fontes", str(FIXTURES / "fontes_teste.yaml")])
    saida = capsys.readouterr().out
    assert codigo == 0
    assert "encontrados=4 validos=3" in saida
    assert "rejeitado — Evento antigo: já passou" in saida
    assert "Concerto de Inverno @ Sala Exemplo" in saida


def test_run_sem_fontes_ativas(capsys):
    assert run.main(["--fontes", str(FIXTURES / "fontes_teste.yaml")]) == 0
    assert "Nenhuma fonte ativa" in capsys.readouterr().out


def test_run_offline_exige_ensaio():
    with pytest.raises(SystemExit):
        run.main(["--offline"])


def test_processar_fonte_grava_com_armazem(monkeypatch):
    class ArmazemFalso:
        def garantir_fonte(self, fonte):
            return 7

        def gravar_eventos(self, source_id, eventos):
            self.gravados = (source_id, eventos)
            return 2

    html = (FIXTURES / "exemplo.html").read_text(encoding="utf-8")
    visitados = []
    monkeypatch.setattr(run.fetch, "obter_pagina", lambda url, c: visitados.append(url) or html)
    armazem = ArmazemFalso()
    fonte = {"id": "exemplo", "nome": "Sala Exemplo", "url": "https://example.org/agenda/",
             "seletor": "#agenda"}
    registo = run.processar_fonte(fonte, "Coimbra", ensaio=False, offline=True,
                                  armazem=armazem, agora=AGORA)
    assert visitados == ["https://example.org/agenda/"]
    assert registo["validos"] == 3 and registo["novos"] == 2 and registo["source_id"] == 7
    assert armazem.gravados[0] == 7 and len(armazem.gravados[1]) == 3

    sem_url = {**fonte, "url": ""}
    with pytest.raises(fetch.ErroRecolha):
        run.processar_fonte(sem_url, "Coimbra", ensaio=False, offline=True, armazem=armazem)
