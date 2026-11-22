# Introdução manual de eventos

Há duas maneiras de juntar eventos à mão, além do scraper.

## 1. Google Sheet (recomendado para o dia a dia)

Folha: **Eventos Coimbra — introdução manual** (no Google Drive do Luis).

- Cada linha do separador `eventos` é um evento. O separador `Como preencher` explica as colunas.
- Obrigatório: **Nome**, **Data início** (dd/mm/aaaa) e **Local**. O resto é opcional.
- A folha tem de estar partilhada como **Qualquer pessoa com o link: Leitor**. O scraper
  lê-a pelo link de exportação em CSV, sem login.
- Os eventos entram na app na recolha diária (04:17 UTC). Para ser já:
  GitHub → Actions → Scraper → Run workflow → fonte `manual`.
- Não gasta Claude: a folha já está organizada, por isso a fonte `manual` tem
  `tipo: folha` no `scraper/fontes.yaml`.
- Editar uma linha (por exemplo, mudar o preço) atualiza o evento. Mudar o nome, a data ou o
  local cria um evento novo, porque a chave única muda. Nesse caso, oculta o antigo
  no Supabase (coluna `estado` = `oculto`).
- Apagar uma linha da folha não apaga o evento da app. Para o esconder, usa a coluna
  `estado` = `oculto` no Supabase.

## 2. Supabase Table Editor (rápido, aparece logo)

Uma vez só: correr `supabase/04_manual.sql` no SQL Editor.

Depois: **Table Editor → events → Insert → Insert row** e preencher `titulo`, `inicio`
(data e hora), `local`, `categoria` (um destes: musica, teatro, exposicao, desporto,
academico, familia, feira, outro) e `url`. A `chave` e a fonte preenchem-se sozinhas.
O evento aparece na app no momento seguinte em que alguém a abrir.
