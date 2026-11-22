"""Páginas legais do site (versão beta): privacidade.html e termos.html.

Converte docs/privacidade.md e docs/termos.md em páginas HTML simples, com o aspeto
da app (fundo preto, letra Inter, destaque dourado), e grava-as ao lado do
index.html do site. O link público fica <url_site>/privacidade.html, que é o que
se indica na Google Play.

Os textos usam {nome}, {cidade}, {responsavel}, {contacto} e {data}, preenchidos a
partir do src/conf/config.json.

Uso:  python scripts/paginas_legais.py dist
(o scripts/splash.py também as gera, por isso o workflow não precisa de mudar)
"""

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PAGINAS = {"privacidade": "Política de privacidade", "termos": "Termos de utilização"}


def _inline(texto: str) -> str:
    texto = html.escape(texto, quote=False)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"\*(.+?)\*", r"<em>\1</em>", texto)
    texto = re.sub(r"([\w.+-]+@[\w-]+(?:\.[\w-]+)+)", r'<a href="mailto:\1">\1</a>', texto)
    texto = re.sub(r"\b(www(?:\.[\w-]+)+)", r'<a href="https://\1">\1</a>', texto)
    return texto


def markdown_simples(md: str) -> str:
    """Só o que os nossos textos usam: títulos #/##, parágrafos, listas com '-'."""
    partes, lista, paragrafo = [], [], []

    def fechar():
        if paragrafo:
            partes.append(f"<p>{_inline(' '.join(paragrafo))}</p>")
            paragrafo.clear()
        if lista:
            partes.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in lista) + "</ul>")
            lista.clear()

    for linha in md.splitlines():
        linha = linha.rstrip()
        if not linha.strip():
            fechar()
        elif linha.startswith("#"):
            fechar()
            nivel = min(len(linha) - len(linha.lstrip("#")), 3)
            partes.append(f"<h{nivel}>{_inline(linha.lstrip('#').strip())}</h{nivel}>")
        elif linha.startswith("- "):
            if paragrafo:
                fechar()
            lista.append(linha[2:].strip())
        elif linha.startswith("  ") and lista:
            lista[-1] += " " + linha.strip()
        else:
            if lista:
                fechar()
            paragrafo.append(linha.strip())
    fechar()
    return "\n".join(partes)


def _valores(cfg: dict) -> dict:
    return {
        "nome": cfg.get("nome", ""),
        "cidade": cfg.get("cidade", ""),
        "responsavel": cfg.get("responsavel") or cfg.get("nome", ""),
        "contacto": cfg.get("contacto", ""),
        "data": cfg.get("data_textos_legais") or date.today().isoformat(),
    }


def pagina(nome: str, cfg: dict) -> str:
    md = (RAIZ / "docs" / f"{nome}.md").read_text(encoding="utf-8")
    corpo = markdown_simples(md.format(**_valores(cfg)))
    titulo = f"{PAGINAS[nome]} — {cfg.get('nome', '')}"
    fundo = cfg.get("cor_fundo", "#0A0A0A")
    return f"""<!DOCTYPE html>
<html lang="pt-PT"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<style>
  body {{ margin: 0; background: {fundo}; color: {cfg.get('cor_texto', '#F5F5F7')};
    font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif; }}
  main {{ max-width: 720px; margin: 0 auto; padding: 40px 22px 64px; }}
  h1 {{ font-size: 32px; line-height: 1.15; letter-spacing: -.5px; margin: 0 0 8px; }}
  h2 {{ font-size: 19px; margin: 32px 0 8px; color: {cfg.get('cor_destaque', '#C9A55C')}; }}
  p, li {{ color: {cfg.get('cor_texto_2', '#8E8E93')}; }}
  strong {{ color: {cfg.get('cor_texto', '#F5F5F7')}; }}
  a {{ color: {cfg.get('cor_destaque', '#C9A55C')}; }}
  .voltar {{ display: inline-block; margin-bottom: 28px; text-decoration: none; }}
</style></head>
<body><main>
<a class="voltar" href="./">← {html.escape(cfg.get('nome', ''))}</a>
{corpo}
</main></body></html>
"""


def gerar(pasta: Path, cfg: dict | None = None) -> list[Path]:
    cfg = cfg or json.loads((RAIZ / "src" / "conf" / "config.json").read_text(encoding="utf-8"))
    feitos = []
    for nome in PAGINAS:
        destino = pasta / f"{nome}.html"
        destino.write_text(pagina(nome, cfg), encoding="utf-8")
        feitos.append(destino)
    return feitos


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    for f in gerar(Path(sys.argv[1])):
        print(f"gerada: {f}")
