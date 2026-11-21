# Como acrescentar uma fonte de eventos

1. **Encontrar a página de agenda** do site (a que lista vários eventos, não a de um evento).
2. **Verificar:**
   ```bash
   python -m scripts.verificar_fonte https://site.pt/agenda/
   ```
   - Se o robots.txt não permitir, a fonte fica de fora.
   - Lê os termos de utilização do site. Na dúvida, pergunta ao Luis (ou pede autorização à sala).
   - Se o texto passar de 100 000 tokens, encontra um seletor CSS da zona da agenda
     (no browser: botão direito → Inspecionar) e volta a correr com ele:
     `python -m scripts.verificar_fonte https://site.pt/agenda/ "#agenda"`
   - Se o texto não tiver os eventos, a página carrega-os com JavaScript. Procura um feed
     (RSS, iCal) ou deixa a fonte para depois.
3. **Guardar uma cópia da página** em `tests/fixtures/<id>.html` (no browser: Guardar como).
4. **Acrescentar ao `scraper/fontes.yaml`** com `ativa: false`.
5. **Ensaio** (gasta uma fração de cêntimo da chave de desenvolvimento):
   ```bash
   python -m scraper.run --fonte <id> --ensaio
   ```
   Compara 5 eventos com o site: título, data, hora, local, preço.
6. Se estiver tudo certo, muda para `ativa: true` e abre o Pull Request (modelo "Nova fonte").
7. Depois do merge, corre o workflow **Scraper** à mão (Actions → Scraper → Run workflow,
   com o id da fonte) e confirma os eventos no Supabase.
