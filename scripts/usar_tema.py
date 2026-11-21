"""Troca a app para outra cidade/tema (Fase 5, tarefa 5.5).

Um tema é uma pasta em temas/<nome>/ com:
    config.json   -> copiado para src/conf/config.json
    fontes.yaml   -> copiado para scraper/fontes.yaml
    logo.png      -> copiado para src/assets/logo.png (opcional)

Uso:
    python scripts/usar_tema.py exemplo-aveiro
    python scripts/usar_tema.py coimbra
"""

import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINOS = {
    "config.json": RAIZ / "src" / "conf" / "config.json",
    "fontes.yaml": RAIZ / "scraper" / "fontes.yaml",
    "logo.png": RAIZ / "src" / "assets" / "logo.png",
}
OBRIGATORIOS = ("config.json", "fontes.yaml")


def usar_tema(nome: str, raiz: Path = RAIZ, destinos: dict[str, Path] | None = None) -> list[str]:
    destinos = destinos or DESTINOS
    pasta = raiz / "temas" / nome
    if not pasta.is_dir():
        disponiveis = sorted(p.name for p in (raiz / "temas").iterdir() if p.is_dir())
        raise SystemExit(f"Tema '{nome}' não existe. Disponíveis: {', '.join(disponiveis)}")
    for obrigatorio in OBRIGATORIOS:
        if not (pasta / obrigatorio).exists():
            raise SystemExit(f"O tema '{nome}' não tem {obrigatorio}")
    json.loads((pasta / "config.json").read_text(encoding="utf-8"))  # valida o JSON

    copiados = []
    for ficheiro, destino in destinos.items():
        origem = pasta / ficheiro
        if origem.exists():
            shutil.copyfile(origem, destino)
            copiados.append(ficheiro)
    return copiados


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    feitos = usar_tema(sys.argv[1])
    print(f"Tema '{sys.argv[1]}' aplicado: {', '.join(feitos)}")
