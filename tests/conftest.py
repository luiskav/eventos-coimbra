"""Peças partilhadas pelos testes."""

from datetime import UTC, datetime, timedelta

import pytest

from config import Config
from models import Evento


@pytest.fixture
def config():
    return Config(
        nome="Eventos Teste",
        cidade="Coimbra",
        slogan="",
        dias_agenda=30,
        categorias={"musica": "Música", "teatro": "Teatro", "outro": "Outros"},
        supabase_url="https://teste.supabase.co",
        supabase_anon_key="chave-anon",
    )


def fazer_evento(id=1, titulo="Concerto", inicio=None, fim=None, local="Sala Exemplo",
                 categoria="musica", descricao=None):
    inicio = inicio or datetime(2026, 11, 21, 21, 30, tzinfo=UTC)
    return Evento(id=id, titulo=titulo, inicio=inicio, fim=fim, local=local,
                  categoria=categoria, url=f"https://example.org/{id}", descricao=descricao)


@pytest.fixture
def evento():
    return fazer_evento()


@pytest.fixture
def eventos():
    base = datetime(2026, 11, 16, 0, 0, tzinfo=UTC)  # segunda-feira, inverno (UTC = Lisboa)
    return [
        fazer_evento(1, "Concerto de Fado", base + timedelta(hours=21)),               # seg
        fazer_evento(2, "Peça Infantil", base + timedelta(days=4, hours=19),           # sex 19h
                     categoria="teatro", local="Teatro Exemplo"),
        fazer_evento(3, "Jazz no Largo", base + timedelta(days=5, hours=22)),          # sáb
        fazer_evento(4, "Exposição", base + timedelta(days=1, hours=10),               # ter
                     fim=base + timedelta(days=12, hours=18), categoria="outro",
                     descricao="Fotografia de rua"),
        fazer_evento(5, "Festival de Inverno", base + timedelta(days=40, hours=15)),   # longe
    ]
