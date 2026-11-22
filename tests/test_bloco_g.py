"""Testes do bloco G: cópia local dos eventos e ecrã de carregamento do site."""

import asyncio
from datetime import UTC, datetime, timedelta

from data import CacheEventos
from scripts import splash
from tests.conftest import fazer_evento
from tests.test_favoritos import ArmazenamentoFalso

FIXTURE = splash.RAIZ / "tests" / "fixtures" / "flet_index.html"


def test_cache_guarda_le_e_ignora_passados():
    armazem = ArmazenamentoFalso()
    cache = CacheEventos(armazem)
    agora = datetime(2026, 11, 21, 12, 0, tzinfo=UTC)
    futuro = fazer_evento(1, "Futuro", agora + timedelta(days=1))
    passado = fazer_evento(2, "Passado", agora - timedelta(days=2))
    asyncio.run(cache.guardar([futuro, passado]))
    lidos = asyncio.run(cache.ler(agora))
    assert [e.titulo for e in lidos] == ["Futuro"]
    assert lidos[0] == futuro  # ida e volta sem perder nada


def test_cache_estragada_ou_indisponivel():
    assert asyncio.run(CacheEventos(ArmazenamentoFalso({"eventos.cache": "{x"})).ler()) == []
    assert asyncio.run(CacheEventos(ArmazenamentoFalso(falhar=True)).ler()) == []


def test_splash_acrescenta_uma_vez():
    original = FIXTURE.read_text(encoding="utf-8")
    novo, msg = splash.aplicar(original)
    assert "acrescentado" in msg
    assert novo.count('id="ec-splash"') == 1 and "ec-roda" in novo
    assert novo.index("globalThis.jsConnect") > novo.index('src="python.js"')
    assert "#0A0A0A" in novo and "A preparar a agenda" in novo
    outra_vez, msg2 = splash.aplicar(novo)
    assert outra_vez == novo and "nada a fazer" in msg2


def test_splash_formato_inesperado_nao_mexe():
    html = "<html><head></head><body>sem flet</body></html>"
    novo, msg = splash.aplicar(html)
    assert novo == html and msg.startswith("AVISO")


def test_splash_main(tmp_path, capsys):
    destino = tmp_path / "index.html"
    destino.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    assert splash.main([str(destino)]) == 0
    assert "ec-splash" in destino.read_text(encoding="utf-8")
