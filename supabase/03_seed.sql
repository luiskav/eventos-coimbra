-- =====================================================================
-- Eventos Coimbra — dados de exemplo (Fase 1, tarefa 1.4)
-- 10 eventos FICTÍCIOS, sempre no futuro (datas relativas a hoje).
-- Servem só para a app ter dados antes de o scraper funcionar.
-- Apagar antes do lançamento: delete from events where chave like 'exemplo|%';
-- =====================================================================

insert into sources (codigo, nome, url, categoria_padrao, ativa)
values ('manual', 'Introdução manual', null, 'outro', false)
on conflict (codigo) do nothing;

insert into venues (nome, morada) values
  ('Sala Exemplo', 'Rua de Exemplo, Coimbra'),
  ('Praça Exemplo', 'Baixa de Coimbra'),
  ('Pavilhão Exemplo', 'Coimbra')
on conflict (nome) do nothing;

with base as (select date_trunc('day', now()) as hoje,
                     (select id from sources where codigo = 'manual') as fonte)
insert into events (chave, titulo, inicio, fim, local, categoria, preco, descricao, url, source_id)
select 'exemplo|' || e.n, e.titulo,
       base.hoje + e.dias * interval '1 day' + e.hora,
       case when e.duracao is null then null
            else base.hoje + e.dias * interval '1 day' + e.hora + e.duracao end,
       e.local, e.categoria, e.preco, e.descricao, 'https://example.org/evento/' || e.n, base.fonte
from base, (values
  (1,  'Concerto de Exemplo',          0, interval '21 hours 30 minutes', interval '2 hours', 'Sala Exemplo',     'musica',    '10 €',    'Evento fictício para testes.'),
  (2,  'Peça de Teatro de Exemplo',    1, interval '21 hours',            interval '90 minutes', 'Sala Exemplo', 'teatro',    '8 €',     'Evento fictício para testes.'),
  (3,  'Exposição de Exemplo',         2, interval '10 hours',            interval '8 hours', 'Praça Exemplo',   'exposicao', 'Gratuito','Evento fictício para testes.'),
  (4,  'Jogo de Exemplo',              3, interval '16 hours',            null,               'Pavilhão Exemplo','desporto',  '5 €',     'Evento fictício para testes.'),
  (5,  'Sessão Académica de Exemplo',  4, interval '18 hours',            null,               'Sala Exemplo',    'academico', 'Gratuito','Evento fictício para testes.'),
  (6,  'Oficina para Famílias',        5, interval '11 hours',            interval '2 hours', 'Praça Exemplo',   'familia',   '3 €',     'Evento fictício para testes.'),
  (7,  'Feira de Exemplo',             6, interval '9 hours',             interval '9 hours', 'Praça Exemplo',   'feira',     'Gratuito','Evento fictício para testes.'),
  (8,  'Concerto Acústico de Exemplo', 9, interval '22 hours',            null,               'Sala Exemplo',    'musica',    '12 €',    'Evento fictício para testes.'),
  (9,  'Conversa de Exemplo',         12, interval '18 hours 30 minutes', null,               'Sala Exemplo',    'outro',     'Gratuito','Evento fictício para testes.'),
  (10, 'Festival de Exemplo',         20, interval '15 hours',            interval '8 hours', 'Praça Exemplo',   'musica',    '15 €',    'Evento fictício para testes.')
) as e(n, titulo, dias, hora, duracao, local, categoria, preco, descricao)
on conflict (chave) do nothing;
