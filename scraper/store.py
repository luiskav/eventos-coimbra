"""Gravação no Supabase com a chave service_role (Fase 2, tarefas 2.6 e 2.7).

Usa a API REST (PostgREST) diretamente com httpx: menos dependências e fácil
de testar com um servidor falso (httpx.MockTransport).
A chave service_role ignora o RLS: só existe nos Secrets do GitHub.
"""

from datetime import UTC, datetime, timedelta

import httpx

from scraper.models import EventoExtraido
from scraper.normalize import chave_evento


class ErroArmazem(Exception):
    """Falha ao gravar no Supabase."""


class Armazem:
    def __init__(self, url: str, chave_service: str,
                 transporte: httpx.BaseTransport | None = None):
        if not url or not chave_service:
            raise ErroArmazem("Faltam SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY")
        self.cliente = httpx.Client(
            base_url=url.rstrip("/") + "/rest/v1",
            headers={"apikey": chave_service, "Authorization": f"Bearer {chave_service}",
                     "Content-Type": "application/json"},
            timeout=30,
            transport=transporte,
        )

    def _verificar(self, resposta: httpx.Response) -> httpx.Response:
        if resposta.status_code >= 400:
            # não imprimir cabeçalhos: os logs do Actions são públicos
            raise ErroArmazem(f"Supabase HTTP {resposta.status_code}: {resposta.text[:300]}")
        return resposta

    def garantir_fonte(self, fonte: dict) -> int:
        linha = {
            "codigo": fonte["id"],
            "nome": fonte["nome"],
            "url": fonte.get("url") or None,
            "categoria_padrao": fonte.get("categoria", "outro"),
            "ativa": bool(fonte.get("ativa", True)),
        }
        resposta = self._verificar(self.cliente.post(
            "/sources", params={"on_conflict": "codigo"}, json=[linha],
            headers={"Prefer": "resolution=merge-duplicates,return=representation"},
        ))
        return int(resposta.json()[0]["id"])

    def chaves_existentes(self, source_id: int, agora: datetime | None = None) -> set[str]:
        agora = agora or datetime.now(UTC)
        desde = (agora - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        resposta = self._verificar(self.cliente.get(
            "/events",
            params={"select": "chave", "source_id": f"eq.{source_id}", "inicio": f"gte.{desde}"},
        ))
        return {linha["chave"] for linha in resposta.json()}

    @staticmethod
    def para_linha(ev: EventoExtraido, source_id: int) -> dict:
        return {
            "chave": chave_evento(ev.titulo, ev.inicio, ev.local),
            "titulo": ev.titulo,
            "inicio": ev.inicio.isoformat(),
            "fim": ev.fim.isoformat() if ev.fim else None,
            "local": ev.local,
            "categoria": ev.categoria,
            "preco": ev.preco,
            "descricao": ev.descricao,
            "url": ev.url,
            "imagem": ev.imagem,
            "source_id": source_id,
            # "estado" não vai: um evento ocultado à mão continua oculto
        }

    def gravar_eventos(self, source_id: int, eventos: list[EventoExtraido]) -> int:
        """Upsert pela chave. Devolve quantos eventos são novos."""
        if not eventos:
            return 0
        linhas = {}
        for ev in eventos:  # deduplicar dentro da mesma página
            linha = self.para_linha(ev, source_id)
            linhas[linha["chave"]] = linha
        existentes = self.chaves_existentes(source_id)
        self._verificar(self.cliente.post(
            "/events", params={"on_conflict": "chave"}, json=list(linhas.values()),
            headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
        ))
        return len(set(linhas) - existentes)

    def registar_execucao(self, registo: dict) -> None:
        self._verificar(self.cliente.post(
            "/scrape_runs", json=[registo], headers={"Prefer": "return=minimal"},
        ))
