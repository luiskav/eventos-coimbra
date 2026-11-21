# Eventos Coimbra

Agenda de eventos e acontecimentos de Coimbra: **site + app Android** feitos só em Python
(Flet), com os dados num Supabase alimentado por um **scraper com Claude** que corre todos
os dias no GitHub Actions.

```
sites das salas ──> scraper (GitHub Actions, diário) ──> Claude API ──> Supabase
                                                                          │ (só leitura)
                                                       site (GitHub Pages) + app Android
```

## Arrancar (Codespace ou computador)

```bash
pip install -r requirements-dev.txt
export SUPABASE_URL="https://O-TEU-PROJETO.supabase.co"
export SUPABASE_ANON_KEY="a-chave-anon"      # sem isto, a app mostra eventos de exemplo
flet run --web --port 8550 src/main.py
```

## Testes

```bash
ruff check .
pytest -q
python -m scraper.run --fonte exemplo --ensaio --offline --fontes tests/fixtures/fontes_teste.yaml
```

## Estrutura

| Pasta | O que tem |
|---|---|
| `src/` | A app Flet: `main.py`, `app.py` (navegação), `agenda.py` (lógica), `data.py` (Supabase), `favoritos.py`, `views/` (ecrãs), `conf/` (config e segredos) |
| `scraper/` | `fontes.yaml`, `fetch.py` (descarregar e limpar), `extract.py` (Claude), `models.py` (validação), `store.py` (gravar), `run.py` |
| `supabase/` | SQL das tabelas, da segurança (RLS) e dos dados de exemplo |
| `scripts/` | `gerar_secrets.py`, `usar_tema.py`, `verificar_fonte.py` |
| `temas/` | Configurações de cada cidade (`coimbra`, `exemplo-aveiro`) |
| `exercicios/` | Exercícios da Fase 0 |
| `docs/` | Nova fonte, nova cidade, deploy, testes com utilizadores, privacidade |

## Segredos

| Secret do GitHub | Usado por | Pode ir para a app? |
|---|---|---|
| `SUPABASE_URL` | app e scraper | sim |
| `SUPABASE_ANON_KEY` | app | sim (só lê, por causa do RLS) |
| `SUPABASE_SERVICE_ROLE_KEY` | scraper | **nunca** |
| `ANTHROPIC_API_KEY` | scraper | **nunca** |

Mais detalhe em `docs/DEPLOY.md`.
