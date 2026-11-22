"""Eventos introduzidos à mão numa Google Sheet (fonte do tipo "folha").

Sem Claude: as linhas da folha já vêm organizadas. O scraper descarrega a
folha em CSV, converte cada linha para o mesmo formato que o Claude devolve
e, a partir daí, segue o caminho normal (validação, chave única, gravação).

Cabeçalho aceite (linha 1, por qualquer ordem; maiúsculas e acentos ignorados):
    Nome | Data início | Hora | Data fim | Hora fim | Local | Morada |
    Categoria | Preço | Descrição | Link | Imagem
Obrigatórios: Nome, Data início e Local. As outras colunas podem ficar vazias
ou nem existir. Serve também a folha da tarefa agendada "Eventos Coimbra"
(colunas ID, Fonte e Adicionado em são ignoradas).

Data fim "N/A" (ou "permanente", "sem data") = evento sem data de fim: fica na app
até ser ocultado, com "fim: N/A". Uma exposição com a Data fim vazia conta como N/A;
os outros eventos com a Data fim vazia são de um só dia.
"""

import csv
import io
import re

from scraper.normalize import normalizar

# nome normalizado da coluna -> campo interno
SINONIMOS = {
    "nome": "titulo", "titulo": "titulo", "evento": "titulo",
    "data inicio": "data", "data": "data", "dia": "data",
    "hora": "hora", "hora inicio": "hora",
    "data fim": "data_fim",
    "hora fim": "hora_fim",
    "local": "local", "espaco": "local", "sala": "local",
    "morada": "morada",
    "categoria": "categoria",
    "preco": "preco",
    "descricao": "descricao",
    "link": "url", "url": "url",
    "imagem": "imagem",
}


SEM_FIM = {"n a", "na", "permanente", "sem data", "sem fim"}


def url_csv(url: str) -> str:
    """Aceita o link normal da folha e devolve o link de exportação em CSV.

    https://docs.google.com/spreadsheets/d/<ID>/edit#gid=<GID>
      -> https://docs.google.com/spreadsheets/d/<ID>/export?format=csv&gid=<GID>
    """
    if "format=csv" in url or "output=csv" in url:
        return url
    m = re.search(r"/spreadsheets/d/([\w-]+)", url)
    if not m:
        return url
    gid = re.search(r"[#&?]gid=(\d+)", url)
    final = f"&gid={gid.group(1)}" if gid else ""
    return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv{final}"


def _data_iso(valor: str) -> str | None:
    """'2026-12-05', '05/12/2026' ou '5-12-2026' -> '2026-12-05'."""
    valor = (valor or "").strip()
    if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", valor):
        a, m, d = valor.split("-")
        return f"{int(a):04d}-{int(m):02d}-{int(d):02d}"
    m = re.fullmatch(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", valor)
    if m:
        d, mes, a = m.groups()
        return f"{int(a):04d}-{int(mes):02d}-{int(d):02d}"
    return None


def _hora(valor: str) -> str | None:
    """'21:30', '21:30:00', '21h30', '21h', '9:00' -> '21:30'."""
    m = re.fullmatch(r"(\d{1,2})\s*[:hH]\s*(\d{2})?(?::\d{2})?", (valor or "").strip())
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2) or 0)
    return f"{h:02d}:{mi:02d}" if h < 24 and mi < 60 else None


def ler_folha(texto_csv: str, link_padrao: str = "") -> tuple[list[dict], list[str]]:
    """Devolve (eventos no formato do Claude, linhas ignoradas com o motivo)."""
    leitor = csv.reader(io.StringIO(texto_csv.lstrip("﻿")))
    linhas = list(leitor)
    if not linhas:
        return [], ["folha vazia"]
    colunas = [SINONIMOS.get(normalizar(c)) for c in linhas[0]]
    for obrigatorio in ("titulo", "data", "local"):
        if obrigatorio not in colunas:
            return [], [f"falta a coluna obrigatória '{obrigatorio}' no cabeçalho"]

    eventos, ignoradas = [], []
    for numero, linha in enumerate(linhas[1:], start=2):
        celulas = {c: (v or "").strip().lstrip("'") for c, v in zip(colunas, linha, strict=False)
                   if c}
        if not any(celulas.values()):
            continue  # linha em branco
        data = _data_iso(celulas.get("data", ""))
        if not celulas.get("titulo") or not celulas.get("local") or not data:
            ignoradas.append(f"linha {numero}: falta nome, local ou data válida")
            continue
        hora = _hora(celulas.get("hora", "")) or "00:00"
        texto_fim = normalizar(celulas.get("data_fim", ""))
        categoria = celulas.get("categoria") or "outro"
        permanente = texto_fim in SEM_FIM or (
            not texto_fim and normalizar(categoria).startswith("exposic"))
        data_fim = None if permanente else _data_iso(celulas.get("data_fim", ""))
        hora_fim = _hora(celulas.get("hora_fim", ""))
        fim = None
        if (data_fim or hora_fim) and not permanente:
            fim = f"{data_fim or data}T{hora_fim or '23:59'}:00"
            if fim == f"{data}T23:59:00" and not hora_fim and data_fim == data:
                fim = None  # evento de um só dia sem hora de fim
        local = celulas["local"]
        if celulas.get("morada"):
            local = f"{local}, {celulas['morada']}"
        eventos.append({
            "titulo": celulas["titulo"],
            "inicio": f"{data}T{hora}:00",
            "fim": fim,
            "local": local,
            "categoria": categoria,
            "preco": celulas.get("preco") or None,
            "descricao": celulas.get("descricao") or None,
            "url": celulas.get("url") or link_padrao,
            "imagem": celulas.get("imagem") or None,
            "permanente": permanente,
        })
    return eventos, ignoradas
