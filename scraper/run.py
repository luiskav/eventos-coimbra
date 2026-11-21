"""Programa principal do scraper (Fase 2, tarefas 2.7 e 2.8).

Uso:
  python -m scraper.run                          # todas as fontes ativas, grava no Supabase
  python -m scraper.run --fonte tagv             # só uma fonte
  python -m scraper.run --fonte tagv --ensaio    # NÃO grava; usa tests/fixtures/tagv.html
  python -m scraper.run --fonte exemplo --ensaio --offline
        # nem sequer chama o Claude: usa a resposta guardada em tests/fixtures/exemplo.json
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import yaml

from scraper import extract, fetch
from scraper.models import validar_eventos

RAIZ = Path(__file__).resolve().parent.parent
FONTES_PADRAO = RAIZ / "scraper" / "fontes.yaml"
FIXTURES = RAIZ / "tests" / "fixtures"
PAUSA_ENTRE_FONTES = 3  # segundos, para não sobrecarregar ninguém


def carregar_fontes(caminho: Path) -> tuple[str, list[dict]]:
    with caminho.open(encoding="utf-8") as f:
        dados = yaml.safe_load(f)
    return dados.get("cidade", ""), dados.get("fontes", [])


class ClaudeFalso:
    """Devolve a resposta guardada num JSON, como se fosse o Claude (modo --offline).

    No JSON, "{hoje+3}" é substituído pela data de daqui a 3 dias, para os
    exemplos estarem sempre no futuro.
    """

    def __init__(self, caminho: Path, hoje: date | None = None):
        self.caminho = caminho
        self.hoje = hoje or datetime.now(UTC).date()

    def extrair(self, **_):
        texto = self.caminho.read_text(encoding="utf-8")
        texto = re.sub(
            r"\{hoje\+(\d+)\}",
            lambda m: (self.hoje + timedelta(days=int(m.group(1)))).isoformat(),
            texto,
        )
        return extract.Resultado(eventos=json.loads(texto))


def processar_fonte(fonte: dict, cidade: str, ensaio: bool, offline: bool,
                    armazem=None, cliente_http=None, agora: datetime | None = None) -> dict:
    agora = agora or datetime.now(UTC)
    registo = {"inicio": agora.isoformat(), "estado": "ok", "encontrados": 0, "validos": 0,
               "novos": 0, "tokens_entrada": 0, "tokens_saida": 0, "erro": None}
    base_url = fonte.get("url") or ""

    # 1. obter o HTML
    guardado = FIXTURES / f"{fonte['id']}.html"
    if ensaio and guardado.exists():
        html = guardado.read_text(encoding="utf-8")
        base_url = base_url or "https://example.org/agenda/"
    else:
        if not base_url:
            raise fetch.ErroRecolha("Fonte sem URL")
        html = fetch.obter_pagina(base_url, cliente_http)

    # 2. limpar e 3. extrair com o Claude
    texto = fetch.limpar_html(html, base_url, fonte.get("seletor") or "")
    argumentos = dict(texto=texto, fonte=fonte["nome"], hoje=agora.date().isoformat(),
                      cidade=cidade, categoria=fonte.get("categoria", "outro"))
    if offline:
        resultado = ClaudeFalso(FIXTURES / f"{fonte['id']}.json", agora.date()).extrair(
            **argumentos)
    else:
        resultado = extract.extrair_eventos(**argumentos)
    registo["encontrados"] = len(resultado.eventos)
    registo["tokens_entrada"] = resultado.tokens_entrada
    registo["tokens_saida"] = resultado.tokens_saida

    # 4. validar
    validos, rejeitados = validar_eventos(resultado.eventos, base_url, agora)
    registo["validos"] = len(validos)
    for motivo in rejeitados:
        print(f"  rejeitado — {motivo}")

    # 5. gravar (ou só mostrar, em ensaio)
    if ensaio:
        for ev in validos:
            print(f"  {ev.inicio:%Y-%m-%d %H:%M} UTC | {ev.categoria:<9} | "
                  f"{ev.titulo} @ {ev.local}")
    else:
        source_id = armazem.garantir_fonte(fonte)
        registo["source_id"] = source_id
        registo["novos"] = armazem.gravar_eventos(source_id, validos)
    return registo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scraper de eventos com Claude")
    parser.add_argument("--fonte", help="id de uma fonte do fontes.yaml")
    parser.add_argument("--ensaio", action="store_true", help="não grava no Supabase")
    parser.add_argument("--offline", action="store_true",
                        help="não chama o Claude (usa tests/fixtures/<id>.json)")
    parser.add_argument("--fontes", type=Path, default=FONTES_PADRAO)
    args = parser.parse_args(argv)
    if args.offline and not args.ensaio:
        parser.error("--offline só pode ser usado com --ensaio")

    cidade, fontes = carregar_fontes(args.fontes)
    if args.fonte:
        fontes = [f for f in fontes if f["id"] == args.fonte]
        if not fontes:
            parser.error(f"Fonte desconhecida: {args.fonte}")
    else:
        fontes = [f for f in fontes if f.get("ativa")]
    if not fontes:
        print("Nenhuma fonte ativa. Ativa pelo menos uma no fontes.yaml.")
        return 0

    armazem = None
    if not args.ensaio:
        from scraper.store import Armazem

        armazem = Armazem(os.environ.get("SUPABASE_URL", ""),
                          os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))

    falhas = 0
    with fetch.novo_cliente() as cliente_http:
        for i, fonte in enumerate(fontes):
            if i and not args.ensaio:
                time.sleep(PAUSA_ENTRE_FONTES)
            print(f"[{fonte['id']}] {fonte['nome']}")
            try:
                registo = processar_fonte(fonte, cidade, args.ensaio, args.offline,
                                          armazem, cliente_http)
            except Exception as erro:  # uma fonte com erro não pára as outras
                falhas += 1
                registo = {"estado": "erro", "erro": f"{type(erro).__name__}: {erro}"[:500]}
                print(f"  ERRO: {registo['erro']}")
            registo["fim"] = datetime.now(UTC).isoformat()
            print(f"  encontrados={registo.get('encontrados', 0)} "
                  f"validos={registo.get('validos', 0)} novos={registo.get('novos', 0)} "
                  f"tokens={registo.get('tokens_entrada', 0)}/{registo.get('tokens_saida', 0)}")
            if armazem is not None:
                if "source_id" not in registo:
                    try:
                        registo["source_id"] = armazem.garantir_fonte(fonte)
                    except Exception:
                        continue
                armazem.registar_execucao(registo)

    return 1 if falhas == len(fontes) else 0


if __name__ == "__main__":
    sys.exit(main())
