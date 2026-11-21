"""Testes da configuração e do modelo Evento (Fase 3, tarefas 3.1 e 3.2; Fase 5)."""

import json
from datetime import UTC, datetime

import pytest

from config import carregar_config
from models import Evento


def escrever(pasta, nome, dados):
    (pasta / nome).write_text(json.dumps(dados), encoding="utf-8")


def test_config_padrao_e_segredos(tmp_path, monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    escrever(tmp_path, "config.json", {"nome": "X", "categorias": {"musica": "Música"}})
    escrever(tmp_path, "secrets.json",
             {"supabase_url": "https://a.supabase.co/", "supabase_anon_key": "k"})
    cfg = carregar_config(tmp_path)
    assert cfg.nome == "X" and cfg.dias_agenda == 30
    assert cfg.supabase_url == "https://a.supabase.co"  # sem a barra final
    assert cfg.tem_supabase


def test_config_variaveis_de_ambiente_ganham(tmp_path, monkeypatch):
    escrever(tmp_path, "config.json", {"categorias": {"outro": "Outros"}})
    monkeypatch.setenv("SUPABASE_URL", "https://env.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "env")
    assert carregar_config(tmp_path).supabase_anon_key == "env"


def test_config_sem_segredos(tmp_path, monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    escrever(tmp_path, "config.json", {"categorias": {"outro": "Outros"}})
    assert not carregar_config(tmp_path).tem_supabase


@pytest.mark.parametrize("dias", [0, 400, "30"])
def test_config_dias_invalidos(tmp_path, dias):
    escrever(tmp_path, "config.json", {"dias_agenda": dias, "categorias": {"o": "O"}})
    with pytest.raises(ValueError):
        carregar_config(tmp_path)


def test_config_real_do_projeto_carrega():
    cfg = carregar_config()
    assert cfg.nome and "musica" in cfg.categorias
    assert cfg.rotulo_categoria("musica") == "Música"
    assert cfg.cor_categoria("inexistente") == cfg.cor_primaria


def test_evento_de_dict():
    ev = Evento.de_dict({"id": 7, "titulo": " Fado ", "inicio": "2026-12-05T21:30:00+00:00",
                         "fim": None, "local": "Sala", "categoria": "musica",
                         "url": "https://x.pt"})
    assert ev.titulo == "Fado"
    assert ev.inicio == datetime(2026, 12, 5, 21, 30, tzinfo=UTC)


def test_evento_de_dict_com_z_e_sem_fuso():
    a = Evento.de_dict({"id": 1, "titulo": "A", "inicio": "2026-12-05T21:30:00Z", "url": ""})
    b = Evento.de_dict({"id": 2, "titulo": "B", "inicio": "2026-12-05T21:30:00", "url": ""})
    assert a.inicio == b.inicio


def test_evento_sem_inicio_falha():
    with pytest.raises(ValueError):
        Evento.de_dict({"id": 1, "titulo": "A", "inicio": None})
