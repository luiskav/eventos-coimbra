"""Testes da camada de dados com um servidor falso (Fase 3, tarefa 3.2)."""

from dataclasses import replace
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import pytest

from data import ErroDados, FonteDados

AGORA = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)
LINHA = {"id": 1, "titulo": "Fado", "inicio": "2026-11-20T21:30:00+00:00", "fim": None,
         "local": "Sala", "categoria": "musica", "preco": "10 €", "descricao": None,
         "url": "https://x.pt", "imagem": None}


class ServidorFalso:
    def __init__(self, resposta=None, erro=None):
        self.resposta, self.erro, self.pedidos = resposta, erro, []

    def __call__(self, url, cabecalhos):
        self.pedidos.append((url, cabecalhos))
        if self.erro:
            raise self.erro
        return self.resposta


def test_le_eventos_do_supabase(config):
    servidor = ServidorFalso([LINHA, {"id": 2, "titulo": "estragado"}])
    dados = FonteDados(config, http_get=servidor)
    eventos = dados.carregar(AGORA)
    assert [e.titulo for e in eventos] == ["Fado"]  # a linha estragada é ignorada
    assert dados.origem == "supabase"


def test_pedido_tem_chave_e_filtros(config):
    servidor = ServidorFalso([])
    FonteDados(config, http_get=servidor).eventos_supabase(AGORA)
    url, cabecalhos = servidor.pedidos[0]
    assert url.startswith("https://teste.supabase.co/rest/v1/events?")
    assert cabecalhos == {"apikey": "chave-anon", "Authorization": "Bearer chave-anon"}
    q = parse_qs(urlparse(url).query)
    assert q["order"] == ["inicio.asc"] and q["limit"] == ["500"]
    assert q["inicio"] == ["lt.2026-12-17T12:00:00Z"]           # 30 dias + 1
    assert q["or"] == ["(inicio.gte.2026-11-16T00:00:00Z,fim.gte.2026-11-16T00:00:00Z)"]


def test_sem_rede_usa_exemplos(config):
    dados = FonteDados(config, http_get=ServidorFalso(erro=ErroDados("sem rede")))
    eventos = dados.carregar(AGORA)
    assert dados.origem == "exemplo" and len(eventos) == 4
    assert eventos[0].inicio == datetime(2026, 11, 16, 21, 30, tzinfo=UTC)  # dias=0, 21:30


def test_sem_segredos_usa_exemplos(config):
    sem = replace(config, supabase_url="", supabase_anon_key="")
    servidor = ServidorFalso([LINHA])
    dados = FonteDados(sem, http_get=servidor)
    dados.carregar(AGORA)
    assert dados.origem == "exemplo" and servidor.pedidos == []


def test_resposta_que_nao_e_lista(config):
    dados = FonteDados(config, http_get=ServidorFalso({"message": "erro"}))
    with pytest.raises(ErroDados):
        dados.eventos_supabase(AGORA)
