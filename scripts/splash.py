"""Ecrã de carregamento animado do site (bloco G, passo 25).

O `flet publish` gera um index.html que mostra uma imagem parada enquanto o
browser descarrega o motor do Flutter, e depois um ecrã do próprio Flet enquanto
descarrega o Python. Juntos, são os segundos mais longos do arranque.

Este script, corrido a seguir ao `flet publish`, acrescenta ao index.html:
  1. um ecrã preto com o logótipo e um anel dourado a rodar, por cima de tudo;
  2. um pequeno script que só o retira quando a app em Python envia a primeira
     mensagem (ou seja, quando o ecrã de arranque da app já está desenhado).

Uso:  python scripts/splash.py dist/index.html
Se o index.html não tiver o formato esperado, não altera nada e avisa (código 0),
para nunca impedir a publicação do site.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCA = "<!-- splash-eventos -->"
TEMPO_MAXIMO_MS = 90_000  # rede de segurança: retira o ecrã ao fim de 90 s


def _cores() -> dict:
    cfg = json.loads((RAIZ / "src" / "conf" / "config.json").read_text(encoding="utf-8"))
    return {
        "fundo": cfg.get("cor_fundo", "#0A0A0A"),
        "superficie": cfg.get("cor_superficie", "#161618"),
        "superficie_2": cfg.get("cor_superficie_2", "#1F1F22"),
        "texto": cfg.get("cor_texto", "#F5F5F7"),
        "texto_2": cfg.get("cor_texto_2", "#8E8E93"),
        "destaque": cfg.get("cor_destaque", "#C9A55C"),
        "nome": cfg.get("nome", "Eventos"),
    }


def estilo(c: dict) -> str:
    return f"""{MARCA}
<style>
  html, body {{ background: {c['fundo']}; }}
  #loading {{ background: {c['fundo']} !important; }}
  #loading img {{ display: none; }}
  #ec-splash {{ position: fixed; inset: 0; z-index: 2147483647; background: {c['fundo']};
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 22px; font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto,
    sans-serif; transition: opacity .35s ease; }}
  #ec-splash.ec-sai {{ opacity: 0; pointer-events: none; }}
  #ec-splash .ec-nome {{ color: {c['texto']}; font-size: 17px; font-weight: 600;
    letter-spacing: -.2px; text-align: center; }}
  #ec-splash .ec-frase {{ color: {c['texto_2']}; font-size: 13px; margin-top: 6px;
    text-align: center; }}
  @keyframes ec-roda {{ to {{ transform: rotate(360deg); }} }}
  @keyframes ec-pulsa {{ 0%, 100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
  @keyframes ec-ponto {{ 0%, 80%, 100% {{ opacity: .2; }} 40% {{ opacity: 1; }} }}
  #ec-splash .ec-anel {{ transform-origin: 60px 60px; animation: ec-roda 1.1s linear infinite; }}
  #ec-splash .ec-mono {{ animation: ec-pulsa 2.2s ease-in-out infinite; }}
  #ec-splash .ec-p {{ animation: ec-ponto 1.4s infinite; }}
  #ec-splash .ec-p:nth-child(2) {{ animation-delay: .2s; }}
  #ec-splash .ec-p:nth-child(3) {{ animation-delay: .4s; }}
  @media (prefers-reduced-motion: reduce) {{
    #ec-splash .ec-anel, #ec-splash .ec-mono, #ec-splash .ec-p {{ animation: none; }}
  }}
</style>"""


def ecra(c: dict) -> str:
    return f"""<div id="ec-splash" role="status" aria-label="A carregar">
  <svg width="120" height="120" viewBox="0 0 120 120" aria-hidden="true">
    <circle cx="60" cy="60" r="52" fill="none" stroke="{c['superficie_2']}" stroke-width="4"/>
    <circle class="ec-anel" cx="60" cy="60" r="52" fill="none" stroke="{c['destaque']}"
      stroke-width="4" stroke-linecap="round" stroke-dasharray="80 247"/>
    <g class="ec-mono">
      <rect x="30" y="30" width="60" height="60" rx="16" fill="{c['superficie']}"/>
      <text x="60" y="69" text-anchor="middle" font-size="26" font-weight="700"
        fill="{c['texto']}" font-family="-apple-system, Inter, sans-serif"
        letter-spacing="-1">EC</text>
    </g>
  </svg>
  <div>
    <div class="ec-nome">{c['nome']}</div>
    <div class="ec-frase">A preparar a agenda<span class="ec-p">.</span><span
      class="ec-p">.</span><span class="ec-p">.</span></div>
  </div>
</div>"""


SCRIPT = f"""<script>
(function () {{
  var fechado = false;
  function fechar() {{
    if (fechado) return;
    fechado = true;
    var e = document.getElementById("ec-splash");
    if (!e) return;
    e.classList.add("ec-sai");
    setTimeout(function () {{ e.remove(); }}, 400);
  }}
  // O python.js define jsConnect; envolvemo-lo para saber quando o Python fala pela 1.a vez.
  var original = globalThis.jsConnect;
  if (typeof original === "function") {{
    globalThis.jsConnect = function (appId, args, dartOnMessage) {{
      var primeira = true;
      var envolvida = function (dados) {{
        if (primeira) {{ primeira = false; setTimeout(fechar, 150); }}
        return dartOnMessage(dados);
      }};
      return original(appId, args, envolvida).catch(function (erro) {{
        fechar();
        throw erro;
      }});
    }};
  }} else {{
    window.addEventListener("flutter-first-frame", fechar, {{ once: true }});
  }}
  setTimeout(fechar, {TEMPO_MAXIMO_MS});
}})();
</script>"""


def aplicar(html: str, cores: dict | None = None) -> tuple[str, str]:
    """Devolve (html novo, mensagem). Se não reconhecer o ficheiro, devolve-o igual."""
    if MARCA in html:
        return html, "já tinha o ecrã de carregamento; nada a fazer"
    pontos = ['<script src="python.js"></script>', "</head>", "<body>"]
    if any(p not in html for p in pontos):
        return html, "AVISO: index.html com formato inesperado; ficou o carregamento original"
    c = cores or _cores()
    html = html.replace('<script src="python.js"></script>',
                        '<script src="python.js"></script>\n' + SCRIPT, 1)
    html = html.replace("</head>", estilo(c) + "\n</head>", 1)
    html = html.replace("<body>", "<body>\n" + ecra(c), 1)
    return html, "ecrã de carregamento animado acrescentado"


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 1
    caminho = Path(argv[0])
    novo, mensagem = aplicar(caminho.read_text(encoding="utf-8"))
    caminho.write_text(novo, encoding="utf-8")
    print(f"{caminho}: {mensagem}")
    # Versão beta: páginas legais ao lado do index.html (privacidade.html, termos.html)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from paginas_legais import gerar

    for f in gerar(caminho.parent):
        print(f"gerada: {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
