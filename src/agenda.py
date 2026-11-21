"""Lógica da agenda, sem interface (Fase 3, tarefas 3.3 e 3.4; Fase 4, tarefa 4.3).

Tudo aqui são funções puras: recebem dados, devolvem dados.
Por isso são fáceis de testar com pytest (tests/test_agenda.py).
"""

import unicodedata
from datetime import UTC, date, datetime, timedelta
from urllib.parse import quote, urlencode

from models import Evento

# ---------------------------------------------------------------------------
# Hora de Portugal continental, sem depender de zoneinfo (que pode não
# existir no browser). Regra da UE: hora de verão (+1 h) entre o último
# domingo de março e o último domingo de outubro, às 01:00 UTC.
# ---------------------------------------------------------------------------


def _ultimo_domingo(ano: int, mes: int) -> date:
    ultimo_dia = date(ano, mes + 1, 1) - timedelta(days=1)
    return ultimo_dia - timedelta(days=(ultimo_dia.weekday() - 6) % 7)


def desvio_lisboa(dt_utc: datetime) -> timedelta:
    """0 h no inverno, +1 h no verão."""
    ano = dt_utc.year
    inicio_verao = datetime.combine(_ultimo_domingo(ano, 3), datetime.min.time(), UTC)
    fim_verao = datetime.combine(_ultimo_domingo(ano, 10), datetime.min.time(), UTC)
    inicio_verao += timedelta(hours=1)
    fim_verao += timedelta(hours=1)
    return timedelta(hours=1) if inicio_verao <= dt_utc < fim_verao else timedelta(0)


def hora_local(dt_utc: datetime) -> datetime:
    """Converte UTC para a hora de Lisboa (devolve datetime sem fuso)."""
    dt_utc = dt_utc.astimezone(UTC)
    return (dt_utc + desvio_lisboa(dt_utc)).replace(tzinfo=None)


def agora_local() -> datetime:
    return hora_local(datetime.now(UTC))


# ---------------------------------------------------------------------------
# Períodos e filtros
# ---------------------------------------------------------------------------

PERIODOS = {
    "hoje": "Hoje",
    "fim_de_semana": "Fim de semana",
    "30_dias": "Próximos 30 dias",
}


def intervalo(periodo: str, agora: datetime) -> tuple[datetime, datetime]:
    """Devolve (início, fim) em hora local para um período. O fim é exclusivo."""
    hoje = datetime(agora.year, agora.month, agora.day)
    if periodo == "hoje":
        return hoje, hoje + timedelta(days=1)
    if periodo == "fim_de_semana":
        # sexta às 18:00 até segunda às 00:00 (weekday: seg=0 ... dom=6)
        sexta = hoje + timedelta(days=(4 - hoje.weekday()) % 7)
        if hoje.weekday() >= 5:  # sábado ou domingo: o fim de semana é este
            sexta = hoje - timedelta(days=hoje.weekday() - 4)
        inicio = max(sexta + timedelta(hours=18), hoje)
        return inicio, sexta + timedelta(days=3)
    if periodo == "30_dias":
        return hoje, hoje + timedelta(days=30)
    raise ValueError(f"Período desconhecido: {periodo}")


def normalizar(texto: str) -> str:
    """Minúsculas e sem acentos: 'Música' -> 'musica'."""
    sem_acentos = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in sem_acentos if not unicodedata.combining(c)).lower().strip()


def decorre_em(evento: Evento, inicio: datetime, fim: datetime) -> bool:
    """True se o evento acontece (pelo menos em parte) entre início e fim (hora local)."""
    ev_inicio = hora_local(evento.inicio)
    ev_fim = hora_local(evento.fim) if evento.fim else ev_inicio
    return ev_inicio < fim and ev_fim >= inicio


def filtrar(
    eventos: list[Evento],
    periodo: str | None = None,
    categoria: str | None = None,
    texto: str = "",
    agora: datetime | None = None,
) -> list[Evento]:
    agora = agora or agora_local()
    resultado = eventos
    if periodo:
        inicio, fim = intervalo(periodo, agora)
        resultado = [e for e in resultado if decorre_em(e, inicio, fim)]
    if categoria:
        resultado = [e for e in resultado if e.categoria == categoria]
    procura = normalizar(texto)
    if procura:
        resultado = [
            e
            for e in resultado
            if procura in normalizar(f"{e.titulo} {e.local} {e.descricao or ''}")
        ]
    return sorted(resultado, key=lambda e: e.inicio)


def agrupar_por_dia(eventos: list[Evento]) -> list[tuple[date, list[Evento]]]:
    grupos: dict[date, list[Evento]] = {}
    for ev in sorted(eventos, key=lambda e: e.inicio):
        grupos.setdefault(hora_local(ev.inicio).date(), []).append(ev)
    return list(grupos.items())


# ---------------------------------------------------------------------------
# Formatação em português
# ---------------------------------------------------------------------------

DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def formatar_dia(dia: date, hoje: date) -> str:
    if dia == hoje:
        return "Hoje"
    if dia == hoje + timedelta(days=1):
        return "Amanhã"
    return f"{DIAS[dia.weekday()].capitalize()}, {dia.day} de {MESES[dia.month - 1]}"


def formatar_hora(evento: Evento) -> str:
    inicio = hora_local(evento.inicio)
    texto = f"{inicio:%H:%M}"
    if evento.fim:
        fim = hora_local(evento.fim)
        texto += f"–{fim:%H:%M}" if fim.date() == inicio.date() else f" até {fim.day}/{fim.month}"
    return texto


def resumo(evento: Evento, hoje: date) -> str:
    """Ex.: 'Amanhã · 21:30 · Sala Exemplo'."""
    dia = formatar_dia(hora_local(evento.inicio).date(), hoje)
    return f"{dia} · {formatar_hora(evento)} · {evento.local}"


# ---------------------------------------------------------------------------
# FASE 4: links para mapa, calendário e partilha
# ---------------------------------------------------------------------------


def url_mapa(evento: Evento, cidade: str) -> str:
    consulta = f"{evento.local}, {cidade}" if cidade else evento.local
    return "https://www.google.com/maps/search/?api=1&query=" + quote(consulta)


def url_calendario(evento: Evento, cidade: str = "") -> str:
    """Link 'Adicionar ao Google Calendar' (datas em UTC)."""
    fmt = "%Y%m%dT%H%M%SZ"
    fim = evento.fim or evento.inicio + timedelta(hours=2)
    params = {
        "action": "TEMPLATE",
        "text": evento.titulo,
        "dates": f"{evento.inicio.astimezone(UTC):{fmt}}/{fim.astimezone(UTC):{fmt}}",
        "location": f"{evento.local}, {cidade}" if cidade else evento.local,
        "details": f"Mais informação: {evento.url}",
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params)


def texto_partilha(evento: Evento, nome_app: str) -> str:
    inicio = hora_local(evento.inicio)
    dia = f"{DIAS[inicio.weekday()]}, {inicio.day} de {MESES[inicio.month - 1]}"
    return (
        f"{evento.titulo}\n{dia.capitalize()}, {formatar_hora(evento)} · {evento.local}\n"
        f"{evento.url}\n\nVi no {nome_app}"
    )
