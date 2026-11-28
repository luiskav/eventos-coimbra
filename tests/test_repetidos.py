"""Segunda folha (tarefa agendada), categoria Cinema, eventos sem fim e repetidos."""

import json
from datetime import UTC, date, datetime, timedelta

import httpx

from scraper import folha, repetidos, run
from scraper.models import validar_eventos
from scraper.store import Armazem

AGORA = datetime(2026, 11, 22, 9, 0, tzinfo=UTC)
FIXTURE = run.FIXTURES / "tarefa-claude.csv"


def _ler():
    texto = run.datas_relativas(FIXTURE.read_text(encoding="utf-8"), AGORA.date())
    brutos, ignoradas = folha.ler_folha(texto)
    return validar_eventos(brutos, "", AGORA)


def test_folha_da_tarefa_categorias_e_sem_fim():
    validos, rejeitados = _ler()
    por_titulo = {e.titulo: e for e in validos}
    assert por_titulo["Bora Ver: Filme de Teste"].categoria == "cinema"
    assert por_titulo["Conversa de Viajantes"].categoria == "academico"   # Conferência
    assert por_titulo["Oficina de Ilustração"].categoria == "academico"   # Workshop
    nucleo = por_titulo["Núcleo da Guitarra e do Fado de Coimbra"]         # Data fim N/A
    assert nucleo.permanente and nucleo.fim is None and nucleo.preco == "3 €"
    mares = por_titulo["Sob Mares Frágeis"]                                # com Data fim
    assert not mares.permanente and mares.fim.date() == date(2027, 3, 31)
    assert not por_titulo["Concerto de Teste – Café Duplo"].permanente
    assert any("Concerto que já passou" in r for r in rejeitados)


def _ev(titulo, inicio, fim=None, permanente=False):
    return {"titulo": titulo, "inicio": inicio, "fim": fim, "permanente": permanente}


def test_provavel_repetido():
    p = repetidos.provavel_repetido
    assert p(_ev("Al Di Meola – Misty Fest 2026", "2026-11-24T21:00:00+00:00"),
             _ev("Al Di Meola - Misty Fest 2026", "2026-11-24T21:00:00+00:00"))
    assert p(_ev("Tartufo, de Molière | Teatrão", "2026-11-26T21:30:00+00:00"),
             _ev("Teatro Tartufo, de Molière", "2026-11-26T00:00:00+00:00"))   # sem hora
    assert not p(_ev("Mundos Possíveis", "2026-11-25T21:30:00+00:00"),
                 _ev("Mundos Possíveis", "2026-11-26T21:30:00+00:00"))         # outro dia
    assert not p(_ev("Mundos Possíveis", "2026-11-25T15:00:00+00:00"),
                 _ev("Mundos Possíveis", "2026-11-25T21:30:00+00:00"))         # outra sessão
    assert not p(_ev("Concerto de Fado", "2026-11-25T21:30:00+00:00"),
                 _ev("Noite de Jazz", "2026-11-25T21:30:00+00:00"))
    # exposições: períodos que se sobrepõem
    assert p(_ev("Sob Mares Frágeis", "2026-09-30T09:00:00+00:00", "2027-03-31T22:59:00+00:00"),
             _ev("Exposição: Sob Mares Frágeis", "2026-09-25T14:00:00+00:00",
                 permanente=True))
    assert not p(_ev("Juan Muñoz", "2026-10-31T10:00:00+00:00", "2027-02-28T18:00:00+00:00"),
                 _ev("Visita guiada Juan Muñoz", "2026-11-21T10:00:00+00:00"))


def test_complemento_nao_substitui():
    existente = {"inicio": "2026-11-24T21:00:00+00:00", "preco": "10 €", "imagem": None,
                 "descricao": None, "categoria": "outro", "permanente": False}
    novo = {"preco": "12 €", "imagem": "https://x/i.jpg", "descricao": "Concerto.",
            "categoria": "musica", "fim": "2026-11-24T23:00:00+00:00"}
    assert repetidos.complemento(existente, novo) == {
        "imagem": "https://x/i.jpg", "descricao": "Concerto.", "fim": "2026-11-24T23:00:00+00:00",
        "categoria": "musica"}


def test_armazem_completa_repetido_e_grava_novo():
    pedidos = []
    existente = {"id": 9, "chave": "outra|202611242100|grande-auditorio",
                 "titulo": "Al Di Meola - Misty Fest 2026", "inicio": "2026-11-24T21:00:00+00:00",
                 "fim": None, "categoria": "musica", "preco": None, "descricao": "x",
                 "imagem": None, "permanente": False}

    def responder(pedido: httpx.Request):
        pedidos.append(pedido)
        if pedido.method == "GET" and "permanente.is.true" in str(pedido.url):
            return httpx.Response(200, json=[existente])
        if pedido.method == "GET":
            return httpx.Response(200, json=[])
        return httpx.Response(201)

    armazem = Armazem("https://p.supabase.co", "service", httpx.MockTransport(responder))
    eventos, _ = validar_eventos(
        [{"titulo": "Al Di Meola – Misty Fest 2026", "inicio": "2026-11-24T21:00:00",
          "local": "Convento São Francisco", "preco": "35 €", "url": "https://a"},
         {"titulo": "Noite de Jazz", "inicio": "2026-11-24T21:00:00", "local": "Salão Brazil",
          "url": "https://b"}], "", AGORA)
    novos = armazem.gravar_eventos(5, eventos)
    assert novos == 1 and len(armazem.repetidos) == 1 and "#9" in armazem.repetidos[0]
    patch = next(p for p in pedidos if p.method == "PATCH")
    assert patch.url.params["id"] == "eq.9" and json.loads(patch.content) == {"preco": "35 €"}
    post = next(p for p in pedidos if p.method == "POST")
    assert [linha["titulo"] for linha in json.loads(post.content)] == ["Noite de Jazz"]


def test_run_ensaio_fonte_tarefa(capsys, tmp_path):
    fontes = tmp_path / "fontes.yaml"
    fontes.write_text("cidade: Coimbra\nfontes:\n  - id: tarefa-claude\n    nome: Tarefa\n"
                      "    tipo: folha\n    url: https://docs.google.com/x\n    ativa: true\n",
                      encoding="utf-8")
    assert run.main(["--fonte", "tarefa-claude", "--ensaio", "--fontes", str(fontes)]) == 0
    saida = capsys.readouterr().out
    assert "cinema" in saida and "Pêndulo" in saida


def test_app_permanente_e_agrupamento():
    import agenda
    from models import Evento

    inicio = datetime(2026, 9, 30, 9, 0, tzinfo=UTC)
    expo = Evento(id=1, titulo="Núcleo", inicio=inicio, local="Torre", categoria="exposicao",
                  url="https://x", permanente=True)
    assert agenda.formatar_hora(expo) == "10:00 · fim: N/A"
    agora = datetime(2026, 11, 22, 10, 0)
    assert agenda.filtrar([expo], periodo="hoje", agora=agora) == [expo]
    hoje = agora.date()
    concerto = Evento(id=2, titulo="Fado", inicio=datetime(2026, 11, 23, 21, 0, tzinfo=UTC),
                      local="Sala", categoria="musica", url="https://y")
    grupos = agenda.agrupar_por_dia([concerto, expo], hoje)
    assert [d for d, _ in grupos] == [hoje, hoje + timedelta(days=1)]
    assert Evento.de_dict({**expo.para_dict(), "id": 1}).permanente


def test_mesmo_filme_em_cinemas_diferentes_nao_e_repetido():
    p = repetidos.provavel_repetido
    forum = {"titulo": "Michael — Cinemas NOS Fórum Coimbra", "inicio": "2026-11-26T13:45:00+00:00",
             "fim": "2026-12-02T23:59:00+00:00", "local": "Cinemas NOS Fórum Coimbra"}
    alma = {"titulo": "Michael — Cinemas NOS Alma Shopping", "inicio": "2026-11-26T13:20:00+00:00",
            "fim": "2026-12-02T23:59:00+00:00", "local": "Cinemas NOS Alma Shopping"}
    assert not p(forum, alma)
    assert p(forum, {**forum, "titulo": "Michael - Cinemas NOS Forum Coimbra"})
    # exposição: o mesmo museu escrito de outra forma continua a ser repetido
    assert p({"titulo": "Sob Mares Frágeis", "inicio": "2026-09-30T09:00:00+00:00",
              "fim": "2027-03-31T22:59:00+00:00", "local": "UC Exploratório"},
             {"titulo": "Exposição: Sob Mares Frágeis", "inicio": "2026-09-25T14:00:00+00:00",
              "fim": "2027-03-31T17:00:00+00:00",
              "local": "UC Exploratório - Rotunda das Lages, Coimbra"})
