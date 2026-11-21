"""Normalização de texto e chave única de cada evento (Fase 2, tarefa 2.6)."""

import re
import unicodedata
from datetime import UTC, datetime


def normalizar(texto: str) -> str:
    """'Concerto: Fado à Noite!' -> 'concerto fado a noite'."""
    sem_acentos = unicodedata.normalize("NFKD", texto or "")
    sem_acentos = "".join(c for c in sem_acentos if not unicodedata.combining(c))
    so_letras = re.sub(r"[^a-z0-9]+", " ", sem_acentos.lower())
    return so_letras.strip()


# Palavras que não ajudam a distinguir eventos (ex.: "Teatro TAGV" vs "TAGV")
_PALAVRAS_VAZIAS = {"o", "a", "os", "as", "de", "do", "da", "dos", "das", "e", "em", "no", "na"}


def _resumir(texto: str, maximo: int) -> str:
    palavras = [p for p in normalizar(texto).split() if p not in _PALAVRAS_VAZIAS]
    return "-".join(palavras)[:maximo]


def chave_evento(titulo: str, inicio_utc: datetime, local: str) -> str:
    """Chave estável: o mesmo evento visto duas vezes dá sempre a mesma chave.

    Usa a data e a hora (ao minuto) em UTC, o título e o local normalizados.
    """
    inicio_utc = inicio_utc.astimezone(UTC)
    return f"{_resumir(titulo, 80)}|{inicio_utc:%Y%m%d%H%M}|{_resumir(local, 40)}"
