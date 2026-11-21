"""Descarregar e limpar páginas de agenda (Fase 2, tarefas 2.2 e 2.3)."""

import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "EventosCoimbraBot/1.0 (+mailto:geral@aminhaempresa.pt)"  # TROCAR o contacto
# ~150 000 caracteres ≈ 40 000 tokens: bem abaixo dos 100 000 tokens a partir dos quais
# o Claude Haiku 5.5 fica 5 vezes mais caro.
MAX_CARACTERES = 150_000


class ErroRecolha(Exception):
    """Falha ao descarregar ou ler uma página."""


def novo_cliente(transporte: httpx.BaseTransport | None = None) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT, "Accept-Language": "pt-PT,pt;q=0.9"},
        timeout=20,
        follow_redirects=True,
        transport=transporte,
    )


def pode_visitar(url: str, cliente: httpx.Client) -> bool:
    """Respeita o robots.txt do site. Sem robots.txt (404) = permitido."""
    partes = urlparse(url)
    robots_url = f"{partes.scheme}://{partes.netloc}/robots.txt"
    try:
        resposta = cliente.get(robots_url)
    except httpx.HTTPError:
        return False  # na dúvida, não visitar
    if resposta.status_code in (401, 403):
        return False
    if resposta.status_code >= 400:
        return True
    leitor = RobotFileParser()
    leitor.parse(resposta.text.splitlines())
    return leitor.can_fetch(USER_AGENT, url)


def obter_pagina(url: str, cliente: httpx.Client) -> str:
    if not pode_visitar(url, cliente):
        raise ErroRecolha(f"robots.txt não permite visitar {url}")
    try:
        resposta = cliente.get(url)
        resposta.raise_for_status()
    except httpx.HTTPError as erro:
        raise ErroRecolha(f"Erro ao descarregar {url}: {erro}") from erro
    return resposta.text


def limpar_html(html: str, base_url: str, seletor: str = "",
                max_caracteres: int = MAX_CARACTERES) -> str:
    """Fica só com o texto útil, com os links e imagens em URL absoluto.

    Exemplo: <a href="/e/1">Fado</a>  ->  'Fado [link: https://site.pt/e/1]'
    """
    sopa = BeautifulSoup(html, "html.parser")
    for lixo in sopa(["script", "style", "noscript", "svg", "iframe", "form", "nav", "footer"]):
        lixo.decompose()
    for cabecalho in sopa.select("body > header"):  # só o cabeçalho do site, não o dos eventos
        cabecalho.decompose()

    zona = sopa.select_one(seletor) if seletor else None
    zona = zona or sopa.body or sopa

    for imagem in zona.find_all("img"):
        src = imagem.get("src") or imagem.get("data-src")
        if src:
            imagem.replace_with(f" [imagem: {urljoin(base_url, src)}] ")
        else:
            imagem.decompose()
    for link in zona.find_all("a"):
        href = link.get("href")
        texto = link.get_text(" ", strip=True)
        if href and not href.startswith(("#", "mailto:", "tel:", "javascript:")):
            link.replace_with(f"{texto} [link: {urljoin(base_url, href)}]")
        else:
            link.replace_with(texto)

    texto = zona.get_text("\n")
    linhas = [" ".join(linha.split()) for linha in texto.splitlines()]
    texto = "\n".join(linha for linha in linhas if linha)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto[:max_caracteres]
