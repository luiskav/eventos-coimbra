# Deploy e manutenção

## Pipelines (GitHub Actions)

| Workflow | Quando corre | O que faz |
|---|---|---|
| `ci.yml` | cada Pull Request e push no `dev` | ruff, pytest, ensaio offline do scraper |
| `deploy-web.yml` | merge no `main` | gera `secrets.json`, `flet publish`, publica no Pages |
| `android.yml` | tag `v*` | gera o APK e junta-o à Release |
| `scraper.yml` | todos os dias às 04:17 UTC, ou à mão | recolhe eventos e grava no Supabase |

## Primeira configuração (Luis)

1. Supabase: SQL Editor → correr `supabase/01_schema.sql`, `02_rls.sql`, `03_seed.sql`.
2. Claude Console: criar duas chaves (desenvolvimento e produção) e um limite de gasto mensal.
3. GitHub → Settings → Secrets and variables → Actions: `SUPABASE_URL`,
   `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `ANTHROPIC_API_KEY` (produção).
4. Settings → Pages → Source: GitHub Actions; Custom domain + Enforce HTTPS.

## Rotina semanal (15 min)

- Supabase → Table Editor → `scrape_runs`: há fontes com `estado = erro` ou `validos = 0`?
  Normalmente é o site que mudou: corre `--ensaio` para essa fonte.
- Ver 10 eventos ao acaso na app e comparar com a fonte.
- Evento errado: no Table Editor, mudar `estado` para `oculto` (o scraper não o volta a mostrar).
- Claude Console → Usage: o gasto está dentro do previsto?

## Versões

```bash
git checkout main && git pull
git tag v1.0.0
git push origin v1.0.0     # gera o APK e a Release
```

## Antes do lançamento

- Apagar os eventos de exemplo: `delete from events where chave like 'exemplo|%';`
- Trocar `@o-teu-utilizador-github` no `CODEOWNERS`, o nome da empresa no `pyproject.toml`
  e o contacto no `scraper/fetch.py` e no `config.json`.
