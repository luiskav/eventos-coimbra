"""Validação dos eventos devolvidos pelo Claude (Fase 2, tarefa 2.5).

O Claude pode enganar-se: uma data mal lida, um campo inventado, um URL relativo.
Tudo o que entra no Supabase passa primeiro por aqui.
"""

from datetime import UTC, datetime, timedelta
from typing import Literal
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from scraper.normalize import normalizar

LISBOA = ZoneInfo("Europe/Lisbon")
CATEGORIAS = ("musica", "teatro", "exposicao", "desporto", "academico", "familia", "feira",
              "outro")
Categoria = Literal["musica", "teatro", "exposicao", "desporto", "academico", "familia",
                    "feira", "outro"]


def _para_utc(valor: datetime) -> datetime:
    """Datas sem fuso são hora de Lisboa (é o que os sites mostram)."""
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=LISBOA)
    return valor.astimezone(UTC)


class EventoExtraido(BaseModel):
    titulo: str = Field(min_length=2, max_length=200)
    inicio: datetime
    fim: datetime | None = None
    local: str = Field(min_length=2, max_length=200)
    categoria: Categoria = "outro"
    preco: str | None = Field(default=None, max_length=80)
    descricao: str | None = None
    url: str
    imagem: str | None = None

    @field_validator("titulo", "local", mode="before")
    @classmethod
    def limpar_espacos(cls, v):
        return " ".join(str(v).split()) if v is not None else v

    @field_validator("categoria", mode="before")
    @classmethod
    def categoria_conhecida(cls, v):
        v = normalizar(v or "outro")  # 'Exposição' -> 'exposicao'
        return v if v in CATEGORIAS else "outro"

    @field_validator("descricao", mode="before")
    @classmethod
    def cortar_descricao(cls, v):
        if not v:
            return None
        v = " ".join(str(v).split())
        return v if len(v) <= 300 else v[:297].rstrip() + "..."

    @field_validator("inicio", "fim", mode="after")
    @classmethod
    def datas_em_utc(cls, v):
        return _para_utc(v) if v is not None else v

    @model_validator(mode="after")
    def fim_depois_do_inicio(self):
        if self.fim is not None and self.fim < self.inicio:
            self.fim = None
        return self

    def com_urls_absolutos(self, base: str) -> "EventoExtraido":
        """Transforma '/agenda/123' em 'https://site.pt/agenda/123'."""
        url = urljoin(base, self.url) if base else self.url
        imagem = urljoin(base, self.imagem) if (base and self.imagem) else self.imagem
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"URL inválido: {self.url!r}")
        return self.model_copy(update={"url": url, "imagem": imagem})


def validar_eventos(
    brutos: list[dict], base_url: str, agora: datetime | None = None
) -> tuple[list[EventoExtraido], list[str]]:
    """Devolve (válidos, motivos de rejeição). Só aceita eventos de ontem a um ano."""
    agora = agora or datetime.now(UTC)
    validos, rejeitados = [], []
    for bruto in brutos:
        try:
            ev = EventoExtraido.model_validate(bruto).com_urls_absolutos(base_url)
        except (ValidationError, ValueError) as erro:
            rejeitados.append(f"{bruto.get('titulo', '?')}: {str(erro).splitlines()[0]}")
            continue
        fim = ev.fim or ev.inicio
        if fim < agora - timedelta(days=1):
            rejeitados.append(f"{ev.titulo}: já passou")
        elif ev.inicio > agora + timedelta(days=365):
            rejeitados.append(f"{ev.titulo}: data a mais de um ano")
        else:
            validos.append(ev)
    return validos, rejeitados
