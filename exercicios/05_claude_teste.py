"""Exercício 05 (Fase 0, tarefa 0.7): o primeiro pedido à Claude API.

Usa a chave de DESENVOLVIMENTO que o Luis te der (com limite de gasto baixo):
    export ANTHROPIC_API_KEY="sk-ant-..."
Correr:  python exercicios/05_claude_teste.py

O texto abaixo imita um pedaço de uma página de agenda. O Claude devolve os
eventos em JSON. Custa uma fração de cêntimo.

Desafio 1: muda o texto para incluir um evento sem hora. O que devolve?
Desafio 2: pede também o preço de cada evento.
"""

import json

import anthropic

TEXTO = """Agenda de dezembro
Sáb 5 dez · 21h30 · Concerto de Natal · Sala Exemplo · 10 €
Dom 6 dez · 11h · Oficina de postais para famílias · Biblioteca Exemplo · grátis
"""

cliente = anthropic.Anthropic()
resposta = cliente.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": "Extrai os eventos deste texto como uma lista JSON com os campos "
                   "titulo, data (AAAA-MM-DD, ano 2026), hora (HH:MM) e local. "
                   "Responde só com o JSON.\n\n" + TEXTO,
    }],
)
texto = resposta.content[0].text
print(texto)
uso = resposta.usage
print(f"\nTokens: {uso.input_tokens} de entrada, {uso.output_tokens} de saída")
try:
    print(f"\nO Claude encontrou {len(json.loads(texto))} eventos.")
except json.JSONDecodeError:
    print("\nA resposta não é JSON válido. É por isto que o scraper usa uma ferramenta (tool).")
