"""Gera src/conf/secrets.json a partir das variáveis de ambiente (Fase 6, tarefa 6.3).

Usado no GitHub Actions antes de publicar o site ou gerar o APK:
    SUPABASE_URL=... SUPABASE_ANON_KEY=... python scripts/gerar_secrets.py

Só usa a chave PÚBLICA (anon). A service_role nunca vai para a app.
"""

import json
import os
import sys
from pathlib import Path

DESTINO = Path(__file__).resolve().parent.parent / "src" / "conf" / "secrets.json"


def main() -> int:
    url = os.environ.get("SUPABASE_URL", "").strip()
    chave = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    if not url or not chave:
        print("ERRO: faltam SUPABASE_URL e/ou SUPABASE_ANON_KEY", file=sys.stderr)
        return 1
    if "service_role" in chave:
        print("ERRO: isto parece a chave service_role. Usa a chave anon.", file=sys.stderr)
        return 1
    DESTINO.write_text(
        json.dumps({"supabase_url": url, "supabase_anon_key": chave}, indent=2),
        encoding="utf-8",
    )
    print(f"Criado {DESTINO.relative_to(DESTINO.parent.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
