"""Modalidade dos eventos de desporto.

Todos os eventos de desporto devem dizer qual é a modalidade. Na app o título fica
"Basquetebol: AAC x AD Galomar" em vez de só "AAC x AD Galomar".

A modalidade vem, por esta ordem:
  1. do Claude (campo "modalidade"), quando a página da agenda a mostra;
  2. de palavras no título ou na descrição (ex.: "Sampaense Basket");
  3. da página do próprio evento, aberta só para os jogos em que 1 e 2 falharam.
"""

import re

from scraper.normalize import normalizar

# Nome mostrado na app -> palavras (já normalizadas) que a identificam
MODALIDADES: dict[str, tuple[str, ...]] = {
    "Futsal": ("futsal", "futebol de salao"),
    "Futebol de praia": ("futebol de praia", "beach soccer"),
    "Futebol": ("futebol", "liga portugal", "liga 3", "campeonato de portugal",
                "taca da liga", "primeira liga"),
    "Basquetebol": ("basquetebol", "basquete", "basket", "basketball", "proliga",
                    "liga betclic"),
    "Andebol": ("andebol", "handball"),
    "Voleibol de praia": ("voleibol de praia", "volei de praia", "beach volley"),
    "Voleibol": ("voleibol", "volei", "volleyball"),
    "Hóquei em patins": ("hoquei em patins", "hoquei patins", "hoquei"),
    "Rugby": ("rugby", "raguebi"),
    "Polo aquático": ("polo aquatico",),
    "Natação": ("natacao", "swimming"),
    "Atletismo": ("atletismo", "corrida", "maratona", "meia maratona", "sao silvestre",
                  "estafeta", "trail", "caminhada"),
    "Ciclismo": ("ciclismo", "btt", "bicicleta"),
    "Triatlo": ("triatlo", "duatlo", "aquatlo"),
    "Ténis de mesa": ("tenis de mesa", "ping pong"),
    "Ténis": ("tenis", "tennis"),
    "Padel": ("padel",),
    "Badminton": ("badminton",),
    "Ginástica": ("ginastica", "gimnica"),
    "Patinagem": ("patinagem", "patinagem artistica"),
    "Judo": ("judo",),
    "Jiu-Jitsu": ("jiu jitsu", "jiujitsu", "bjj"),
    "Karaté": ("karate",),
    "Taekwondo": ("taekwondo",),
    "Boxe": ("boxe", "boxing", "kickboxing"),
    "Esgrima": ("esgrima",),
    "Xadrez": ("xadrez", "chess"),
    "Remo": ("remo", "rowing"),
    "Canoagem": ("canoagem", "kayak", "canoa"),
    "Escalada": ("escalada",),
    "Golfe": ("golfe", "golf"),
    "Hipismo": ("hipismo", "equestre"),
    "Tiro com arco": ("tiro com arco",),
}

# Ordem de procura: as expressões mais longas primeiro ("futebol de praia" antes de
# "futebol", "tenis de mesa" antes de "tenis")
_ORDEM = sorted(((palavra, nome) for nome, palavras in MODALIDADES.items()
                 for palavra in palavras), key=lambda par: -len(par[0]))


def _procurar(texto_normalizado: str) -> dict[str, int]:
    """Quantas vezes cada modalidade aparece no texto (palavras inteiras)."""
    contagem: dict[str, int] = {}
    restante = f" {texto_normalizado} "
    for palavra, nome in _ORDEM:
        padrao = rf"(?<![a-z0-9]){re.escape(palavra)}(?![a-z0-9])"
        n = len(re.findall(padrao, restante))
        if n:
            contagem[nome] = contagem.get(nome, 0) + n
            restante = re.sub(padrao, " ", restante)  # "tenis de mesa" não conta como "tenis"
    return contagem


def detetar(texto: str | None) -> str | None:
    """A modalidade mais mencionada no texto, ou None."""
    if not texto:
        return None
    contagem = _procurar(normalizar(texto))
    if not contagem:
        return None
    return max(contagem.items(), key=lambda par: par[1])[0]


def oficial(nome: str | None) -> str | None:
    """'basket' -> 'Basquetebol'; um nome que não se reconhece fica como veio."""
    if not nome or not nome.strip():
        return None
    return detetar(nome) or nome.strip().capitalize()


def com_modalidade(titulo: str, modalidade: str | None) -> str:
    """'AAC X AD Galomar' + 'Basquetebol' -> 'Basquetebol: AAC X AD Galomar'."""
    if not modalidade:
        return titulo
    if normalizar(titulo).startswith(normalizar(modalidade)):
        return titulo
    return f"{modalidade}: {titulo}"
