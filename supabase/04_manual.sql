-- =====================================================================
-- Eventos Coimbra — introdução manual no Table Editor do Supabase
-- Correr uma vez no SQL Editor. Depois, em Table Editor -> events -> Insert row,
-- basta preencher: titulo, inicio, local, categoria, url (e, se quiseres,
-- fim, preco, descricao, imagem). A chave e a fonte preenchem-se sozinhas.
-- =====================================================================

insert into sources (codigo, nome, url, categoria_padrao, ativa)
values ('manual', 'Introdução manual', null, 'outro', false)
on conflict (codigo) do nothing;

alter table events alter column chave set default '';

create or replace function preencher_evento_manual() returns trigger
language plpgsql set search_path = public as $$
begin
  if new.chave is null or new.chave = '' then
    new.chave := 'manual|' || to_char(new.inicio at time zone 'UTC', 'YYYYMMDDHH24MI') || '|'
                 || left(md5(lower(new.titulo) || '|' || lower(new.local)), 12);
  end if;
  if new.source_id is null then
    select id into new.source_id from sources where codigo = 'manual';
  end if;
  return new;
end;
$$;

drop trigger if exists events_manual on events;
create trigger events_manual before insert on events
  for each row execute function preencher_evento_manual();
