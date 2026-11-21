"""Verifica se uma página de agenda pode ser usada como fonte (Fase 2, tarefa 2.1).

Uso:
    python -m scripts.verificar_fonte https://site.pt/agenda/ [seletor-css]

Mostra: se o robots.txt permite, o tamanho do texto limpo, uma estimativa
de tokens e custo por execução, e as primeiras linhas do texto.
"""

import sys

from scraper import fetch

CARACTERES_POR_TOKEN = 3.5  # aproximação para texto em português
PRECO_ENTRADA = 0.10 / 1_000_000  # dólares por token, Claude Haiku 5.5 (até 100 000 tokens)
PRECO_SAIDA = 0.50 / 1_000_000
TOKENS_SAIDA_ESTIMADOS = 2_000


def estimar(texto: str) -> tuple[int, float]:
    tokens = int(len(texto) / CARACTERES_POR_TOKEN) + 400  # + instruções
    custo = tokens * PRECO_ENTRADA + TOKENS_SAIDA_ESTIMADOS * PRECO_SAIDA
    return tokens, custo


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    url, seletor = argv[0], (argv[1] if len(argv) > 1 else "")
    with fetch.novo_cliente() as cliente:
        if not fetch.pode_visitar(url, cliente):
            print("NÃO: o robots.txt não permite visitar esta página.")
            return 1
        print("OK: o robots.txt permite.")
        html = fetch.obter_pagina(url, cliente)
    texto = fetch.limpar_html(html, url, seletor)
    tokens, custo = estimar(texto)
    print(f"Texto limpo: {len(texto)} caracteres ≈ {tokens} tokens")
    print(f"Custo estimado por execução: {custo:.4f} $  (por mês, 1x/dia: {custo * 30:.2f} $)")
    if tokens > 100_000:
        print("ATENÇÃO: acima de 100 000 tokens o preço fica 5x maior. Usa um seletor.")
    print("\n--- início do texto ---")
    print("\n".join(texto.splitlines()[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
