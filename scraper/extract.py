"""Extração dos eventos com o Claude (Fase 2, tarefa 2.4).

O Claude recebe o texto limpo da página e tem de chamar a ferramenta
"guardar_eventos", cujo esquema obriga a devolver sempre os mesmos campos.
"""

from dataclasses import dataclass

MODELO = "claude-haiku-5-5"

CATEGORIAS = ["musica", "teatro", "exposicao", "desporto", "academico", "familia", "feira",
              "outro"]

FERRAMENTA = {
    "name": "guardar_eventos",
    "description": "Guarda os eventos encontrados na página de agenda.",
    "input_schema": {
        "type": "object",
        "properties": {
            "eventos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "titulo": {"type": "string"},
                        "inicio": {
                            "type": "string",
                            "description": "Data e hora de início, ISO 8601, hora de Lisboa, "
                                           "sem fuso (ex.: 2026-12-05T21:30:00)",
                        },
                        "fim": {"type": ["string", "null"],
                                "description": "Igual a inicio; null se não aparecer"},
                        "local": {"type": "string",
                                  "description": "Sala ou espaço onde acontece"},
                        "categoria": {"type": "string", "enum": CATEGORIAS},
                        "preco": {"type": ["string", "null"],
                                  "description": "Como aparece na página (ex.: '10 €', "
                                                 "'Gratuito'); null se não aparecer"},
                        "descricao": {"type": ["string", "null"],
                                      "description": "Resumo escrito por ti, máx. 300 "
                                                     "caracteres; não copies o texto da página"},
                        "url": {"type": "string",
                                "description": "Link [link: ...] do próprio evento; se não "
                                               "houver, o link da página de agenda"},
                        "imagem": {"type": ["string", "null"]},
                    },
                    "required": ["titulo", "inicio", "local", "categoria", "url"],
                },
            }
        },
        "required": ["eventos"],
    },
}

INSTRUCOES = """Hoje é {hoje}. O texto abaixo é a página de agenda de "{fonte}", em {cidade}.
A categoria mais provável desta fonte é "{categoria}".

Regras:
- Extrai só eventos com data a partir de hoje.
- Não inventes dados: se um campo não aparecer na página, usa null.
- Se o ano não aparecer, usa o ano mais próximo no futuro.
- Se um evento tiver várias sessões em dias diferentes, cria um evento por sessão.
- Se só houver data sem hora, usa 00:00.
- Os links aparecem no texto como [link: URL] e as imagens como [imagem: URL].

Texto da página:
---
{texto}
---"""


@dataclass
class Resultado:
    eventos: list[dict]
    tokens_entrada: int = 0
    tokens_saida: int = 0


def novo_cliente():
    import anthropic  # importado aqui para os testes não precisarem da chave

    return anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente


def extrair_eventos(texto: str, fonte: str, hoje: str, cidade: str = "Coimbra",
                    categoria: str = "outro", cliente=None, modelo: str = MODELO) -> Resultado:
    cliente = cliente or novo_cliente()
    resposta = cliente.messages.create(
        model=modelo,
        max_tokens=8000,
        tools=[FERRAMENTA],
        tool_choice={"type": "tool", "name": "guardar_eventos"},
        messages=[{
            "role": "user",
            "content": INSTRUCOES.format(hoje=hoje, fonte=fonte, cidade=cidade,
                                         categoria=categoria, texto=texto),
        }],
    )
    bloco = next((b for b in resposta.content if b.type == "tool_use"), None)
    eventos = list(bloco.input.get("eventos", [])) if bloco else []
    uso = getattr(resposta, "usage", None)
    return Resultado(
        eventos=eventos,
        tokens_entrada=getattr(uso, "input_tokens", 0) or 0,
        tokens_saida=getattr(uso, "output_tokens", 0) or 0,
    )
