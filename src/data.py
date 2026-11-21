"""Camada de dados: tudo o que fala com o Supabase (Fase 3, tarefas 3.2 e 3.5).

A app só LÊ. Usa a API REST do Supabase (PostgREST) com pedidos HTTP simples,
porque as bibliotecas oficiais podem não funcionar no browser (Pyodide).

- No computador e no Android: urllib (com os certificados do certifi).
- No browser (Pyodide): XMLHttpRequest síncrono do JavaScript.
- Sem ligação ou sem segredos: eventos de exemplo (conf/eventos_exemplo.json).
"""

import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

from config import PASTA_CONF, Config
from models import Evento

CAMPOS = "id,titulo,inicio,fim,local,categoria,preco,descricao,url,imagem"
LIMITE = 500


class ErroDados(Exception):
    """Falha ao obter dados do Supabase."""


HttpGet = Callable[[str, dict[str, str]], object]


def _get_urllib(url: str, cabecalhos: dict[str, str]) -> object:
    import ssl
    import urllib.error
    import urllib.request

    try:
        import certifi

        contexto = ssl.create_default_context(cafile=certifi.where())
    except ImportError:  # pragma: no cover
        contexto = ssl.create_default_context()
    pedido = urllib.request.Request(url, headers=cabecalhos)
    try:
        with urllib.request.urlopen(pedido, timeout=10, context=contexto) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as erro:
        raise ErroDados(str(erro)) from erro


def _get_pyodide(url: str, cabecalhos: dict[str, str]) -> object:  # pragma: no cover
    from js import XMLHttpRequest  # só existe no browser

    xhr = XMLHttpRequest.new()
    xhr.open("GET", url, False)  # síncrono: permitido porque o Python corre num web worker
    for nome, valor in cabecalhos.items():
        xhr.setRequestHeader(nome, valor)
    try:
        xhr.send(None)
    except Exception as erro:
        raise ErroDados(str(erro)) from erro
    if xhr.status != 200:
        raise ErroDados(f"HTTP {xhr.status}")
    return json.loads(xhr.responseText)


def http_get_padrao() -> HttpGet:
    return _get_pyodide if sys.platform == "emscripten" else _get_urllib


class FonteDados:
    def __init__(self, config: Config, http_get: HttpGet | None = None,
                 pasta_conf: Path = PASTA_CONF):
        self.config = config
        self.http_get = http_get or http_get_padrao()
        self.pasta_conf = pasta_conf
        self.origem = "nenhuma"  # "supabase" ou "exemplo", para mostrar no ecrã

    def _cabecalhos(self) -> dict[str, str]:
        chave = self.config.supabase_anon_key
        return {"apikey": chave, "Authorization": f"Bearer {chave}"}

    def _url_eventos(self, agora_utc: datetime) -> str:
        desde = (agora_utc - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
        ate = (agora_utc + timedelta(days=self.config.dias_agenda + 1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        consulta = urlencode(
            [
                ("select", CAMPOS),
                ("inicio", f"lt.{ate}"),
                ("or", f"(inicio.gte.{desde},fim.gte.{desde})"),
                ("order", "inicio.asc"),
                ("limit", str(LIMITE)),
            ]
        )
        return f"{self.config.supabase_url}/rest/v1/events?{consulta}"

    def eventos_supabase(self, agora_utc: datetime | None = None) -> list[Evento]:
        if not self.config.tem_supabase:
            raise ErroDados("Supabase não configurado (falta secrets.json)")
        agora_utc = agora_utc or datetime.now(UTC)
        linhas = self.http_get(self._url_eventos(agora_utc), self._cabecalhos())
        if not isinstance(linhas, list):
            raise ErroDados("Resposta inesperada do Supabase")
        eventos = []
        for linha in linhas:
            try:
                eventos.append(Evento.de_dict(linha))
            except (KeyError, ValueError, TypeError):
                continue  # ignora linhas estragadas em vez de rebentar a app
        return eventos

    def eventos_exemplo(self, agora_utc: datetime | None = None) -> list[Evento]:
        """Eventos fictícios com datas relativas a hoje (dias=0 é hoje)."""
        agora_utc = agora_utc or datetime.now(UTC)
        hoje = datetime(agora_utc.year, agora_utc.month, agora_utc.day, tzinfo=UTC)
        with (self.pasta_conf / "eventos_exemplo.json").open(encoding="utf-8") as f:
            brutos = json.load(f)
        eventos = []
        for b in brutos:
            hora, minuto = (int(x) for x in b["hora"].split(":"))
            inicio = hoje + timedelta(days=b["dias"], hours=hora, minutes=minuto)
            fim = inicio + timedelta(minutes=b["duracao_min"]) if b.get("duracao_min") else None
            eventos.append(
                Evento(id=b["id"], titulo=b["titulo"], inicio=inicio, fim=fim,
                       local=b["local"], categoria=b["categoria"], preco=b.get("preco"),
                       descricao=b.get("descricao"), url=b["url"])
            )
        return eventos

    def carregar(self, agora_utc: datetime | None = None) -> list[Evento]:
        """Tenta o Supabase; se falhar, devolve os eventos de exemplo."""
        try:
            eventos = self.eventos_supabase(agora_utc)
            self.origem = "supabase"
            return eventos
        except ErroDados:
            self.origem = "exemplo"
            return self.eventos_exemplo(agora_utc)
