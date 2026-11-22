"""Modelo de dados da app (Fase 3, tarefa 3.2)."""

from dataclasses import dataclass
from datetime import UTC, datetime


def _data(valor: str | None) -> datetime | None:
    """Converte o texto ISO 8601 do Supabase numa data em UTC."""
    if not valor:
        return None
    dt = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


@dataclass(frozen=True)
class Evento:
    id: int
    titulo: str
    inicio: datetime  # sempre em UTC
    local: str
    categoria: str
    url: str
    fim: datetime | None = None
    preco: str | None = None
    descricao: str | None = None
    imagem: str | None = None
    permanente: bool = False  # sem data de fim: mostra "fim: N/A"

    @classmethod
    def de_dict(cls, d: dict) -> "Evento":
        inicio = _data(d.get("inicio"))
        if inicio is None:
            raise ValueError(f"Evento sem data de início: {d.get('titulo')!r}")
        return cls(
            id=int(d["id"]),
            titulo=str(d["titulo"]).strip(),
            inicio=inicio,
            fim=_data(d.get("fim")),
            local=str(d.get("local") or "").strip(),
            categoria=str(d.get("categoria") or "outro"),
            preco=d.get("preco"),
            descricao=d.get("descricao"),
            url=str(d.get("url") or ""),
            imagem=d.get("imagem"),
            permanente=bool(d.get("permanente")),
        )

    def para_dict(self) -> dict:
        """O inverso de de_dict, para guardar a cópia local (bloco G, passo 29)."""
        return {
            "id": self.id, "titulo": self.titulo, "inicio": self.inicio.isoformat(),
            "fim": self.fim.isoformat() if self.fim else None, "local": self.local,
            "categoria": self.categoria, "preco": self.preco, "descricao": self.descricao,
            "url": self.url, "imagem": self.imagem, "permanente": self.permanente,
        }
