-- Fase extra: segunda folha (tarefa agendada), categoria Cinema e eventos sem data de fim.
-- Pode correr-se mais do que uma vez sem estragar nada.

-- 1. Nova categoria "cinema"
alter table events drop constraint if exists events_categoria_check;
alter table events add constraint events_categoria_check
  check (categoria in ('musica','teatro','exposicao','desporto','academico','familia',
                       'feira','cinema','outro'));

-- 2. Eventos sem data de fim (ex.: exposições permanentes). Na app aparece "fim: N/A".
alter table events add column if not exists permanente boolean not null default false;

-- 3. A app passa a ver também os eventos que já começaram mas ainda decorrem
--    (exposições com data de fim no futuro) e os permanentes.
drop policy if exists "leitura publica de eventos futuros" on events;
create policy "leitura publica de eventos futuros" on events
  for select to anon, authenticated
  using (estado = 'publicado'
         and (permanente or coalesce(fim, inicio) >= now() - interval '1 day'));
