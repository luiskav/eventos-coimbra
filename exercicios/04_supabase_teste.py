"""Exercício 04 (Fase 0, tarefa 0.6): ler eventos do Supabase pela API REST.

Antes de correr, define as variáveis (no Codespace, no terminal):
    export SUPABASE_URL="https://O-TEU-PROJETO.supabase.co"
    export SUPABASE_ANON_KEY="a-chave-anon"
Correr:  python exercicios/04_supabase_teste.py

Desafio 1: mostra só os eventos de música (acrescenta "categoria=eq.musica" ao URL).
Desafio 2: tenta inserir um evento com a chave anon. Deve FALHAR (é o RLS a funcionar).
"""

import json
import os
import urllib.request

url = os.environ["SUPABASE_URL"].rstrip("/")
chave = os.environ["SUPABASE_ANON_KEY"]

pedido = urllib.request.Request(
    f"{url}/rest/v1/events?select=titulo,inicio,local&order=inicio.asc&limit=5",
    headers={"apikey": chave, "Authorization": f"Bearer {chave}"},
)
with urllib.request.urlopen(pedido, timeout=10) as resposta:
    eventos = json.loads(resposta.read())

print(f"Recebidos {len(eventos)} eventos:")
for ev in eventos:
    print(f"- {ev['inicio'][:16]}  {ev['titulo']}  ({ev['local']})")
