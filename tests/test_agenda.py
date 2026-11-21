"""Testes da lógica da agenda (Fase 3, tarefa 3.4; Fase 4, tarefa 4.3)."""

from datetime import UTC, date, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest

import agenda
from tests.conftest import fazer_evento


# ---------- hora de Lisboa ----------
@pytest.mark.parametrize(
    "utc, esperado",
    [
        (datetime(2026, 1, 15, 12, 0, tzinfo=UTC), "12:00"),   # inverno: igual a UTC
        (datetime(2026, 7, 15, 12, 0, tzinfo=UTC), "13:00"),   # verão: +1
        (datetime(2026, 3, 29, 0, 59, tzinfo=UTC), "00:59"),   # último domingo de março, antes
        (datetime(2026, 3, 29, 1, 0, tzinfo=UTC), "02:00"),    # muda às 01:00 UTC
        (datetime(2026, 10, 25, 0, 59, tzinfo=UTC), "01:59"),  # último domingo de outubro, antes
        (datetime(2026, 10, 25, 1, 0, tzinfo=UTC), "01:00"),   # volta ao inverno
    ],
)
def test_hora_local(utc, esperado):
    assert f"{agenda.hora_local(utc):%H:%M}" == esperado


def test_ultimo_domingo():
    assert agenda._ultimo_domingo(2026, 3) == date(2026, 3, 29)
    assert agenda._ultimo_domingo(2026, 10) == date(2026, 10, 25)
    assert agenda._ultimo_domingo(2027, 3) == date(2027, 3, 28)


# ---------- períodos ----------
def test_intervalo_hoje():
    inicio, fim = agenda.intervalo("hoje", datetime(2026, 11, 16, 15, 0))
    assert inicio == datetime(2026, 11, 16) and fim == datetime(2026, 11, 17)


@pytest.mark.parametrize(
    "agora, inicio, fim",
    [
        (datetime(2026, 11, 16, 9), datetime(2026, 11, 20, 18), datetime(2026, 11, 23)),  # seg
        (datetime(2026, 11, 20, 9), datetime(2026, 11, 20, 18), datetime(2026, 11, 23)),  # sex
        (datetime(2026, 11, 21, 9), datetime(2026, 11, 21), datetime(2026, 11, 23)),      # sáb
        (datetime(2026, 11, 22, 9), datetime(2026, 11, 22), datetime(2026, 11, 23)),      # dom
    ],
)
def test_intervalo_fim_de_semana(agora, inicio, fim):
    assert agenda.intervalo("fim_de_semana", agora) == (inicio, fim)


def test_intervalo_desconhecido():
    with pytest.raises(ValueError):
        agenda.intervalo("sempre", datetime(2026, 11, 16))


# ---------- filtros ----------
AGORA = datetime(2026, 11, 16, 9, 0)


def test_filtrar_hoje(eventos):
    assert [e.id for e in agenda.filtrar(eventos, "hoje", agora=AGORA)] == [1]


def test_filtrar_fim_de_semana_inclui_exposicao_a_decorrer(eventos):
    ids = [e.id for e in agenda.filtrar(eventos, "fim_de_semana", agora=AGORA)]
    assert ids == [4, 2, 3]  # exposição (começou antes), peça de sexta às 19h, jazz de sábado


def test_filtrar_fim_de_semana_sexta_ao_fim_da_tarde():
    sexta = fazer_evento(9, inicio=datetime(2026, 11, 20, 19, 0, tzinfo=UTC))
    manha = fazer_evento(10, inicio=datetime(2026, 11, 20, 10, 0, tzinfo=UTC))
    ids = [e.id for e in agenda.filtrar([sexta, manha], "fim_de_semana", agora=AGORA)]
    assert ids == [9]


def test_filtrar_30_dias_exclui_longe(eventos):
    ids = [e.id for e in agenda.filtrar(eventos, "30_dias", agora=AGORA)]
    assert 5 not in ids and len(ids) == 4


def test_filtrar_categoria(eventos):
    assert [e.id for e in agenda.filtrar(eventos, categoria="teatro", agora=AGORA)] == [2]


@pytest.mark.parametrize("texto", ["fado", "FADO", "concerto de fado"])
def test_filtrar_texto(eventos, texto):
    assert [e.id for e in agenda.filtrar(eventos, texto=texto, agora=AGORA)] == [1]


def test_filtrar_texto_sem_acentos_e_descricao(eventos):
    assert [e.id for e in agenda.filtrar(eventos, texto="exposicao", agora=AGORA)] == [4]
    assert [e.id for e in agenda.filtrar(eventos, texto="rua", agora=AGORA)] == [4]
    assert [e.id for e in agenda.filtrar(eventos, texto="teatro exemplo", agora=AGORA)] == [2]


def test_agrupar_por_dia(eventos):
    grupos = agenda.agrupar_por_dia(eventos[:3])
    assert [d for d, _ in grupos] == [date(2026, 11, 16), date(2026, 11, 20), date(2026, 11, 21)]


# ---------- formatação ----------
def test_formatar_dia():
    hoje = date(2026, 11, 16)
    assert agenda.formatar_dia(hoje, hoje) == "Hoje"
    assert agenda.formatar_dia(hoje + timedelta(days=1), hoje) == "Amanhã"
    assert agenda.formatar_dia(date(2026, 11, 21), hoje) == "Sábado, 21 de novembro"


def test_formatar_hora():
    inicio = datetime(2026, 7, 4, 20, 30, tzinfo=UTC)  # verão: 21:30 em Lisboa
    assert agenda.formatar_hora(fazer_evento(inicio=inicio)) == "21:30"
    com_fim = fazer_evento(inicio=inicio, fim=inicio + timedelta(hours=2))
    assert agenda.formatar_hora(com_fim) == "21:30–23:30"
    varios_dias = fazer_evento(inicio=inicio, fim=inicio + timedelta(days=3))
    assert agenda.formatar_hora(varios_dias) == "21:30 até 7/7"


# ---------- FASE 4: links ----------
def test_url_mapa(evento):
    assert agenda.url_mapa(evento, "Coimbra").endswith("Sala%20Exemplo%2C%20Coimbra")


def test_url_calendario(evento):
    q = parse_qs(urlparse(agenda.url_calendario(evento, "Coimbra")).query)
    assert q["action"] == ["TEMPLATE"]
    assert q["text"] == ["Concerto"]
    assert q["dates"] == ["20261121T213000Z/20261121T233000Z"]  # sem fim: +2 h


def test_texto_partilha(evento):
    texto = agenda.texto_partilha(evento, "Eventos Coimbra")
    assert "Concerto" in texto and "Sábado, 21 de novembro, 21:30" in texto
    assert evento.url in texto and texto.endswith("Vi no Eventos Coimbra")
