# Como reutilizar a app noutra cidade

1. Copia `temas/coimbra/` para `temas/<cidade>/`.
2. Edita `temas/<cidade>/config.json`: nome, cidade, slogan, cores, categorias, contacto.
   - Uma categoria que retires do config deixa de aparecer nos filtros. O scraper continua
     a aceitar as 8 categorias da base de dados.
3. Edita `temas/<cidade>/fontes.yaml` com os sites dessa cidade (ver `NOVA_FONTE.md`).
4. Troca `temas/<cidade>/logo.png` (512×512, fundo transparente).
5. Aplica o tema: `python scripts/usar_tema.py <cidade>`
6. Cria um projeto Supabase novo, corre os três ficheiros de `supabase/` e muda os Secrets.
7. No `pyproject.toml`, muda `product` (nome da app Android). O identificador do Android
   tem de ser diferente para cada cidade.
8. Para voltar a Coimbra: `python scripts/usar_tema.py coimbra`
