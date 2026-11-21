-- =====================================================================
-- Eventos Coimbra — tabelas (Fase 1, tarefa 1.2)
-- Correr no Supabase: SQL Editor -> colar -> Run.
-- =====================================================================

-- Fontes de onde o scraper recolhe eventos (uma linha por site)
create table if not exists sources (
  id               bigint generated always as identity primary key,
  codigo           text unique not null,            -- ex.: 'tagv' (igual ao fontes.yaml)
  nome             text not null,
  url              text,
  categoria_padrao text not null default 'outro',
  ativa            boolean not null default true,
  criado_em        timestamptz not null default now()
);

-- Locais (salas, praças, pavilhões). Opcional no MVP: o evento guarda
-- sempre o texto do local; venue_id fica preenchido quando se conhece o local.
create table if not exists venues (
  id        bigint generated always as identity primary key,
  nome      text unique not null,
  morada    text,
  latitude  double precision,
  longitude double precision
);

-- Eventos: a tabela que a app lê
create table if not exists events (
  id            bigint generated always as identity primary key,
  chave         text unique not null,          -- titulo|data|local normalizados (evita duplicados)
  titulo        text not null check (char_length(titulo) between 2 and 200),
  inicio        timestamptz not null,
  fim           timestamptz,
  local         text not null,
  categoria     text not null default 'outro'
                check (categoria in ('musica','teatro','exposicao','desporto',
                                     'academico','familia','feira','outro')),
  preco         text,
  descricao     text check (descricao is null or char_length(descricao) <= 400),
  url           text not null,                 -- link para a fonte original
  imagem        text,
  source_id     bigint references sources(id) on delete set null,
  venue_id      bigint references venues(id) on delete set null,
  estado        text not null default 'publicado' check (estado in ('publicado','oculto')),
  criado_em     timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  check (fim is null or fim >= inicio)
);

create index if not exists events_inicio_idx on events (inicio);
create index if not exists events_categoria_idx on events (categoria);
create index if not exists events_source_idx on events (source_id);

-- Atualiza atualizado_em sempre que uma linha muda
create or replace function tocar_atualizado_em() returns trigger
language plpgsql as $$
begin
  new.atualizado_em := now();
  return new;
end;
$$;

drop trigger if exists events_atualizado on events;
create trigger events_atualizado before update on events
  for each row execute function tocar_atualizado_em();

-- Registo de cada execução do scraper, por fonte
create table if not exists scrape_runs (
  id              bigint generated always as identity primary key,
  source_id       bigint references sources(id) on delete cascade,
  inicio          timestamptz not null default now(),
  fim             timestamptz,
  estado          text not null check (estado in ('ok','erro','ignorada')),
  encontrados     int not null default 0,   -- devolvidos pelo Claude
  validos         int not null default 0,   -- passaram a validação
  novos           int not null default 0,   -- não existiam antes
  tokens_entrada  int not null default 0,
  tokens_saida    int not null default 0,
  erro            text
);

create index if not exists scrape_runs_inicio_idx on scrape_runs (inicio desc);
