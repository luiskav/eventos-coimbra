"""Testes da introdução manual por Google Sheet (fonte do tipo "folha")."""

from datetime import UTC, datetime

import httpx
import pytest

from scraper import fetch, folha, run

FIXTURES = run.FIXTURES
AGORA = datetime(2026, 11, 21, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize("entrada, saida", [
    ("2026-12-05", "2026-12-05"), ("05/12/2026", "2026-12-05"), ("5-12-2026", "2026-12-05"),
    ("5.12.2026", "2026-12-05"), ("amanhã", None), ("", None),
])
def test_data_iso(entrada, saida):
    assert folha._data_iso(entrada) == saida


@pytest.mark.parametrize("entrada, saida", [
    ("21:30", "21:30"), ("21:30:00", "21:30"), ("21h30", "21:30"), ("21h", "21:00"),
    ("9:05", "09:05"), ("25:00", None), ("tarde", None),
])
def test_hora(entrada, saida):
    assert folha._hora(entrada) == saida


def test_url_csv():
    base = "https://docs.google.com/spreadsheets/d/ABC-123_x/"
    assert folha.url_csv(base + "edit#gid=42") == base + "export?format=csv&gid=42"
    assert folha.url_csv(base + "edit?usp=sharing") == base + "export?format=csv"
    assert folha.url_csv(base + "export?format=csv") == base + "export?format=csv"


def test_ler_folha_cabecalho_novo():
    texto = run.datas_relativas((FIXTURES / "manual.csv").read_text("utf-8"), AGORA.date())
    eventos, ignoradas = folha.ler_folha(texto, "https://site.pt/")
    assert len(eventos) == 2 and len(ignoradas) == 2
    natal, mercado = eventos
    assert natal["inicio"] == "2026-11-26T21:30:00" and natal["fim"] is None
    assert natal["local"] == "Sé Velha, Largo da Sé Velha"
    assert natal["preco"] == "10 €"  # o apóstrofo do Sheets sai
    assert mercado["fim"] == "2026-11-30T20:00:00"
    assert mercado["url"] == "https://site.pt/"  # sem Link: usa o link_padrao


def test_ler_folha_da_tarefa_antiga():
    """A folha da tarefa agendada (ID, Data início, ..., Fonte) também serve."""
    texto = ("ID,Data início,Data fim,Hora,Nome,Categoria,Local,Morada,Preço,Descrição,Link,"
             "Fonte,Adicionado em\n"
             "20261205-x,2026-12-05,2026-12-05,21:30,Concerto X,Música,TAGV,,'10 €,,"
             "https://tagv.pt/x,TAGV,2026-10-28\n")
    eventos, ignoradas = folha.ler_folha(texto)
    assert ignoradas == [] and eventos[0]["titulo"] == "Concerto X"
    assert eventos[0]["fim"] is None  # mesmo dia, sem hora de fim


def test_ler_folha_sem_colunas_obrigatorias():
    eventos, ignoradas = folha.ler_folha("Titulo,Hora\nA,21:00\n")
    assert eventos == [] and "falta a coluna obrigatória" in ignoradas[0]


def test_ensaio_da_fonte_manual(capsys):
    codigo = run.main(["--fonte", "manual", "--ensaio",
                       "--fontes", str(FIXTURES / "fontes_teste.yaml")])
    saida = capsys.readouterr().out
    assert codigo == 0
    assert "encontrados=2 validos=2" in saida and "tokens=0/0" in saida
    assert "musica    | Concerto de Natal na Sé" in saida
    assert "feira     | Mercado de Natal" in saida
    assert saida.count("ignorada —") == 2


def transporte(estado, corpo, tipo="text/csv"):
    return httpx.MockTransport(
        lambda pedido: httpx.Response(estado, text=corpo, headers={"content-type": tipo}))


def test_folha_real_e_erros():
    fonte = {"id": "x", "nome": "X", "tipo": "folha",
             "url": "https://docs.google.com/spreadsheets/d/ABC/edit#gid=0"}
    csv_ok = "Nome,Data início,Local\nFeira,2026-12-01,Praça\n"
    with fetch.novo_cliente(transporte(200, csv_ok)) as cliente:
        r = run.ler_fonte_folha(fonte, ensaio=False, cliente_http=cliente)
        assert r.eventos[0]["titulo"] == "Feira"
    with fetch.novo_cliente(transporte(200, "<html>login</html>", "text/html")) as cliente:
        with pytest.raises(fetch.ErroRecolha, match="partilha"):
            run.ler_fonte_folha(fonte, ensaio=False, cliente_http=cliente)
    with fetch.novo_cliente(transporte(404, "")) as cliente:
        with pytest.raises(fetch.ErroRecolha, match="Leitor"):
            run.ler_fonte_folha(fonte, ensaio=False, cliente_http=cliente)
