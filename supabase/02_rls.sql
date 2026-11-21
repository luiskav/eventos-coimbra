-- =====================================================================
-- Eventos Coimbra — segurança (Fase 1, tarefa 1.3)
-- Regra: a app (chave anon) só LÊ eventos publicados e futuros.
-- Só o scraper escreve, com a chave service_role, que ignora o RLS
-- e só existe nos Secrets do GitHub.
-- =====================================================================

alter table sources     enable row level security;
alter table venues      enable row level security;
alter table events      enable row level security;
alter table scrape_runs enable row level security;

-- Eventos: leitura pública só dos publicados, a partir de ontem
drop policy if exists "leitura publica de eventos futuros" on events;
create policy "leitura publica de eventos futuros" on events
  for select to anon, authenticated
  using (estado = 'publicado' and inicio >= now() - interval '1 day');

-- Locais: leitura pública (nome, morada e coordenadas não são sensíveis)
drop policy if exists "leitura publica de locais" on venues;
create policy "leitura publica de locais" on venues
  for select to anon, authenticated
  using (true);

-- sources e scrape_runs: SEM políticas -> anon não lê nem escreve.
-- Nenhuma tabela tem políticas de insert/update/delete -> anon não escreve.

-- Defesa extra: retirar permissões de escrita à chave pública
revoke insert, update, delete on events, venues, sources, scrape_runs from anon, authenticated;
