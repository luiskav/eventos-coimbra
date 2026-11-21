"""Configuração da app (Fase 3, tarefa 3.1; versão final na Fase 5, tarefa 5.1).

Tudo o que muda de cidade para cidade vem de src/conf/config.json.
As ligações ao Supabase vêm de src/conf/secrets.json (gerado no CI)
ou das variáveis de ambiente SUPABASE_URL e SUPABASE_ANON_KEY (em desenvolvimento).
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

PASTA_CONF = Path(__file__).parent / "conf"

PADRAO: dict = {
    "nome": "Eventos",
    "cidade": "",
    "slogan": "",
    "dias_agenda": 30,
    "categorias": {"outro": "Outros"},
    # FASE 5: aparência e textos
    "cor_primaria": "#8E1B3A",
    "cores_categorias": {},
    "logotipo": "",
    "contacto": "",
    "texto_sobre": "",
}


@dataclass(frozen=True)
class Config:
    nome: str
    cidade: str
    slogan: str
    dias_agenda: int
    categorias: dict[str, str]
    cor_primaria: str = "#8E1B3A"
    cores_categorias: dict[str, str] = field(default_factory=dict)
    logotipo: str = ""
    contacto: str = ""
    texto_sobre: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""

    @property
    def tem_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    def rotulo_categoria(self, codigo: str) -> str:
        return self.categorias.get(codigo, codigo.capitalize())

    def cor_categoria(self, codigo: str) -> str:
        return self.cores_categorias.get(codigo, self.cor_primaria)


def _ler_json(caminho: Path) -> dict:
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8") as f:
        return json.load(f)


def carregar_config(pasta: Path = PASTA_CONF) -> Config:
    dados = {**PADRAO, **_ler_json(pasta / "config.json")}
    segredos = _ler_json(pasta / "secrets.json")

    dados["supabase_url"] = (
        os.environ.get("SUPABASE_URL") or segredos.get("supabase_url", "")
    ).rstrip("/")
    dados["supabase_anon_key"] = os.environ.get("SUPABASE_ANON_KEY") or segredos.get(
        "supabase_anon_key", ""
    )

    if not isinstance(dados["dias_agenda"], int) or not 1 <= dados["dias_agenda"] <= 365:
        raise ValueError("dias_agenda tem de ser um número inteiro entre 1 e 365")
    if not dados["categorias"]:
        raise ValueError("config.json tem de ter pelo menos uma categoria")

    campos = Config.__dataclass_fields__
    return Config(**{k: v for k, v in dados.items() if k in campos})
