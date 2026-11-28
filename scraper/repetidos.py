"""Deteção de eventos repetidos entre fontes diferentes.

A chave única (normalize.chave_evento) só apanha o mesmo evento escrito da mesma
maneira. Duas fontes escrevem muitas vezes o mesmo evento de forma diferente:
  "Al Di Meola – Misty Fest 2026" @ Grande Auditório
  "Al Di Meola - Misty Fest 2026" @ Convento São Francisco
Aqui decide-se se dois eventos são, provavelmente, o mesmo.

Regras (todas têm de se cumprir):
  1. Nomes parecidos: pelo menos 60 % das palavras do nome mais curto aparecem no outro.
  2. Datas compatíveis:
     - eventos de um dia: mesmo dia (hora de Lisboa) e início a menos de 60 minutos,
       ou um deles sem hora (00:00);
     - eventos longos (mais de um dia, ou permanentes): os períodos sobrepõem-se e
       os locais são o mesmo (ex.: o mesmo filme no Fórum e no Alma são dois cartões).
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from scraper.normalize import _PALAVRAS_VAZIAS, normalizar

LISBOA = ZoneInfo("Europe/Lisbon")
SEMELHANCA_MINIMA = 0.6
TOLERANCIA = timedelta(minutes=60)
# Palavras que aparecem em muitos títulos e não ajudam a distinguir
_GENERICAS = _PALAVRAS_VAZIAS | {"um", "uma", "com", "para", "por", "sobre", "exposicao",
                                 "concerto", "teatro", "coimbra"}


# Palavras de locais que não distinguem uma sala de outra
_GENERICAS_LOCAL = _GENERICAS | {"cinemas", "cinema", "nos", "sala", "salas", "auditorio",
                                 "centro", "comercial", "shopping", "loja"}


def mesmo_local(a: str | None, b: str | None) -> bool:
    """Sem um dos locais, não se pode dizer que são diferentes."""
    if not a or not b:
        return True
    pa = {p for p in normalizar(a).split() if len(p) > 1 and p not in _GENERICAS_LOCAL}
    pb = {p for p in normalizar(b).split() if len(p) > 1 and p not in _GENERICAS_LOCAL}
    if not pa or not pb:
        return True
    return len(pa & pb) / min(len(pa), len(pb)) >= 0.5


def palavras(titulo: str) -> set[str]:
    return {p for p in normalizar(titulo).split() if len(p) > 1 and p not in _GENERICAS}


def semelhanca(a: str, b: str) -> float:
    pa, pb = palavras(a), palavras(b)
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / min(len(pa), len(pb))


def _data(valor) -> datetime | None:
    if valor is None or isinstance(valor, datetime):
        return valor
    return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))


def _longo(inicio: datetime, fim: datetime | None, permanente: bool) -> bool:
    return permanente or (fim is not None and fim - inicio > timedelta(days=1))


def provavel_repetido(a: dict, b: dict) -> bool:
    """a e b: dicionários com titulo, inicio, fim (podem faltar) e permanente."""
    if semelhanca(a["titulo"], b["titulo"]) < SEMELHANCA_MINIMA:
        return False
    ia, ib = _data(a["inicio"]), _data(b["inicio"])
    fa, fb = _data(a.get("fim")), _data(b.get("fim"))
    pa, pb = bool(a.get("permanente")), bool(b.get("permanente"))

    if _longo(ia, fa, pa) and _longo(ib, fb, pb):
        if not mesmo_local(a.get("local"), b.get("local")):
            return False
        fim_a = None if pa else (fa or ia)
        fim_b = None if pb else (fb or ib)
        return (fim_b is None or ia <= fim_b) and (fim_a is None or ib <= fim_a)
    if _longo(ia, fa, pa) or _longo(ib, fb, pb):
        return False  # uma exposição e uma sessão com nome parecido não são o mesmo

    la, lb = ia.astimezone(LISBOA), ib.astimezone(LISBOA)
    if la.date() != lb.date():
        return False
    sem_hora = (la.hour, la.minute) == (0, 0) or (lb.hour, lb.minute) == (0, 0)
    return sem_hora or abs(ia - ib) <= TOLERANCIA


# Campos que um repetido pode completar no evento que já existe
CAMPOS_COMPLEMENTO = ("preco", "descricao", "imagem", "fim")


def complemento(existente: dict, novo: dict) -> dict:
    """O que o novo traz e o existente não tem (nunca substitui o que já lá está)."""
    extra = {}
    for campo in CAMPOS_COMPLEMENTO:
        if campo == "fim" and existente.get("permanente"):
            continue
        if not existente.get(campo) and novo.get(campo):
            extra[campo] = novo[campo]
    if existente.get("categoria") == "outro" and novo.get("categoria") not in (None, "outro"):
        extra["categoria"] = novo["categoria"]
    if "fim" in extra and _data(extra["fim"]) < _data(existente["inicio"]):
        del extra["fim"]  # não pode acabar antes de começar
    return extra
