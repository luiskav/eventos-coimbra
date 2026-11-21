"""Testes dos scripts de apoio (Fase 5, tarefa 5.5; Fase 6, tarefa 6.3; Fase 2, tarefa 2.1)."""

import json
import shutil

import pytest

from config import carregar_config
from scripts import gerar_secrets, usar_tema, verificar_fonte


def test_usar_tema(tmp_path):
    shutil.copytree(usar_tema.RAIZ / "temas", tmp_path / "temas")
    (tmp_path / "conf").mkdir()
    destinos = {"config.json": tmp_path / "conf" / "config.json",
                "fontes.yaml": tmp_path / "fontes.yaml",
                "logo.png": tmp_path / "logo.png"}
    copiados = usar_tema.usar_tema("exemplo-aveiro", tmp_path, destinos)
    assert copiados == ["config.json", "fontes.yaml", "logo.png"]
    cfg = carregar_config(tmp_path / "conf")
    assert cfg.cidade == "Aveiro" and "academico" not in cfg.categorias
    with pytest.raises(SystemExit):
        usar_tema.usar_tema("nao-existe", tmp_path, destinos)


def test_tema_coimbra_igual_ao_config_atual():
    tema = json.loads((usar_tema.RAIZ / "temas/coimbra/config.json").read_text("utf-8"))
    atual = json.loads((usar_tema.RAIZ / "src/conf/config.json").read_text("utf-8"))
    assert tema == atual


def test_gerar_secrets(tmp_path, monkeypatch):
    destino = tmp_path / "secrets.json"
    monkeypatch.setattr(gerar_secrets, "DESTINO", destino)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    assert gerar_secrets.main() == 1
    monkeypatch.setenv("SUPABASE_URL", "https://p.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    monkeypatch.setattr(gerar_secrets.Path, "relative_to", lambda self, other: self)
    assert gerar_secrets.main() == 0
    assert json.loads(destino.read_text())["supabase_anon_key"] == "anon"


def test_estimativa_de_custo():
    tokens, custo = verificar_fonte.estimar("a" * 35_000)
    assert tokens == 10_400
    assert custo == pytest.approx(10_400 * 0.10e-6 + 2_000 * 0.50e-6)
