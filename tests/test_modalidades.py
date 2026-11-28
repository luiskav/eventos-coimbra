"""Modalidade dos eventos de desporto."""

from datetime import UTC, datetime

import httpx

from scraper import fetch, modalidades, run
from scraper.models import validar_eventos
from scraper.store import Armazem

AGORA = datetime(2026, 11, 28, 9, 0, tzinfo=UTC)


def test_detetar():
    d = modalidades.detetar
    assert d("AAC X Sampaense Basket") == "Basquetebol"
    assert d("48.ª Corrida São Silvestre de Coimbra") == "Atletismo"
    assert d("EUROCUP 2026 Jiu-Jitsu") == "Jiu-Jitsu"
    assert d("Torneio de Ténis de Mesa") == "Ténis de mesa"
    assert d("Futebol de Praia — Taça") == "Futebol de praia"
    assert d("Jogo da AAC: hóquei em patins, 2.ª divisão") == "Hóquei em patins"
    assert d("AAC X AD Galomar") is None
    assert d("Remodelação do pavilhão") is None  # 'remo' só como palavra inteira


def test_oficial_e_titulo():
    assert modalidades.oficial("basket") == "Basquetebol"
    assert modalidades.oficial("Curling") == "Curling"
    assert modalidades.oficial("") is None
    assert modalidades.com_modalidade("AAC X AD Galomar", "Basquetebol") == \
        "Basquetebol: AAC X AD Galomar"
    assert modalidades.com_modalidade("Basquetebol: AAC X Y", "Basquetebol") == \
        "Basquetebol: AAC X Y"
    assert modalidades.com_modalidade("Concerto", None) == "Concerto"


def _eventos():
    validos, _ = validar_eventos([
        {"titulo": "AAC X AD Galomar", "inicio": "2026-11-29T15:00:00", "local": "Pavilhão",
         "categoria": "desporto", "url": "https://agenda.exemplo.pt/event/galomar"},
        {"titulo": "AAC X Sampaense Basket", "inicio": "2026-11-29T18:30:00",
         "local": "Pavilhão", "categoria": "desporto", "url": "https://agenda.exemplo.pt/"},
        {"titulo": "Concerto", "inicio": "2026-11-29T21:00:00", "local": "Sala",
         "categoria": "musica", "url": "https://agenda.exemplo.pt/event/x"},
    ], "https://agenda.exemplo.pt/", AGORA)
    return validos


def test_completar_abre_a_pagina_do_evento_so_quando_preciso():
    pedidos = []

    def responder(pedido: httpx.Request):
        pedidos.append(str(pedido.url))
        if pedido.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /\n")
        return httpx.Response(200, html="<html><body><h1>AAC X AD Galomar</h1>"
                                        "<p>Basquetebol | Proliga</p></body></html>")

    eventos = _eventos()
    run.completar_modalidades(eventos, "https://agenda.exemplo.pt/",
                              fetch.novo_cliente(httpx.MockTransport(responder)))
    assert [e.modalidade for e in eventos] == ["Basquetebol", "Basquetebol", None]
    assert [p for p in pedidos if "event" in p] == ["https://agenda.exemplo.pt/event/galomar"]


def test_titulo_gravado_tem_modalidade_e_chave_nao_muda():
    eventos = _eventos()
    eventos[0].modalidade = "Basquetebol"
    linha = Armazem.para_linha(eventos[0], 1)
    assert linha["titulo"] == "Basquetebol: AAC X AD Galomar"
    assert linha["chave"].startswith("aac-x-ad-galomar|")
