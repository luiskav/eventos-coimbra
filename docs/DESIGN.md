# Design — My Own City (bloco G)

Preto de Coimbra, amarelo do ponto do logótipo, letras grandes. Inspiração: Apple e Revolut.
Todas as cores e letras vêm de `src/conf/config.json`: para outra cidade, muda-se o tema, não o código.

## Cores

| Papel | Chave no config.json | Coimbra |
|---|---|---|
| Fundo | `cor_fundo` | `#0A0A0A` |
| Cartões | `cor_superficie` | `#161618` |
| Cartões por cima de cartões, bordas | `cor_superficie_2` | `#1F1F22` |
| Texto principal | `cor_texto` | `#F5F5F7` |
| Texto secundário | `cor_texto_2` | `#8E8E93` |
| Destaque (botões, seleção, anel, ponto do logótipo) | `cor_destaque` | `#F9C441` |

Cores das categorias (só em etiquetas pequenas, com fundo a 14 %):
música `#B48CF2`, teatro `#F2786D`, exposição `#5FC8C8`, desporto `#7BC67B`,
académico `#8FA8F5`, família `#F2B35E`, feira `#C9A27E`, cinema `#F28FB8`, outro `#9AA4AE`.

## Letras

| Uso | Família | Ficheiro |
|---|---|---|
| Texto | `Inter` | `src/assets/fonts/Inter-Regular.ttf` |
| Realces (botões, etiquetas) | `InterSemi` | `Inter-SemiBold.ttf` |
| Títulos | `InterDisplay` | `InterDisplay-Bold.ttf` |

Os ficheiros estão reduzidos ao alfabeto português (cerca de 56 KB cada). Licença: `LICENSE-Inter.txt` (SIL OFL).

## Medidas

- Cantos: cartões 20, pílulas totalmente redondas (`theme.RAIO_CARTAO`, `theme.RAIO_PILULA`).
- Margens laterais: 20. Espaço entre cartões: 12.
- Título do ecrã: 32–34, `InterDisplay`. Título de cartão: 17, `InterSemi`.

## Peças (`src/theme.py` e `src/views/componentes.py`)

- `titulo`, `destaque`, `secundario`: textos já com letra e cor certas.
- `pilula`: filtro redondo; dourado quando escolhido.
- `etiqueta_categoria`: etiqueta colorida da categoria.
- `botao`: botão em pílula; `principal=True` fica dourado.
- `cartao_evento`: imagem (se houver), bloco de data, etiqueta, título, local e coração.
- `cartao_esqueleto`: cartão cinzento mostrado enquanto os eventos chegam.

## Carregamento sem parecer parado

1. **Site:** `scripts/splash.py` acrescenta ao `index.html` um ecrã preto com o anel amarelo a rodar e o logótipo "m." com o ponto a saltitar. Fica até o Python enviar a primeira mensagem (no máximo 90 s).
2. **App (site e Android):** `views/ecra_arranque.py` mostra o mesmo anel enquanto arranca.
3. **Agenda:** se ainda não há eventos, aparecem 4 cartões cinzentos; no Android, aparecem logo os eventos guardados da última vez (`CacheEventos`, em `data.py`).

## Logótipo

- `src/assets/icon.png` (1024 px): ícone da app Android e do site, "m." sobre preto.
- `src/assets/logo.png` (512 px, cantos arredondados): página Sobre e temas.
- `src/assets/marca.png`: só o "m." sobre transparente (ecrã de arranque).
- `src/assets/favicon.png` (64 px): separador do browser.
