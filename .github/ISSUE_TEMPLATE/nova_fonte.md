---
name: Nova fonte de eventos
about: Propor um site novo para o scraper
labels: fonte-nova, scraper
---
**Nome:**
**URL da página de agenda:**
**Categoria mais comum:**

## Verificações (ver docs/NOVA_FONTE.md)
- [ ] `python -m scripts.verificar_fonte <url>` diz que o robots.txt permite
- [ ] Li os termos de utilização do site e não proíbem a recolha
- [ ] O texto limpo tem menos de 100 000 tokens (se não, encontrei um `seletor`)
- [ ] Os eventos aparecem no HTML (não são carregados só por JavaScript)
- [ ] Guardei uma cópia da página em `tests/fixtures/<id>.html` e corri `--ensaio`
- [ ] Os eventos do ensaio batem certo com o site (datas, horas, local)
