"""Exercício 03 (Fase 0, tarefa 0.5): uma lista de eventos escritos no código.

Treina Card, ListTile, ListView e o clique num elemento.
Desafio 1: ao clicar num evento, mostra a descrição por baixo da lista.
Desafio 2: acrescenta um botão "Só música" que filtra a lista.
"""

import flet as ft

EVENTOS = [
    {"titulo": "Concerto de Exemplo", "dia": "Sábado", "hora": "21:30", "local": "Sala Exemplo",
     "categoria": "musica", "descricao": "Um concerto fictício."},
    {"titulo": "Peça de Teatro", "dia": "Domingo", "hora": "17:00", "local": "Teatro Exemplo",
     "categoria": "teatro", "descricao": "Uma peça fictícia."},
    {"titulo": "Feira do Livro", "dia": "Segunda", "hora": "10:00", "local": "Praça Exemplo",
     "categoria": "feira", "descricao": "Uma feira fictícia."},
]

ICONES = {"musica": ft.Icons.MUSIC_NOTE, "teatro": ft.Icons.THEATER_COMEDY,
          "feira": ft.Icons.STOREFRONT}


def main(page: ft.Page):
    page.title = "Mini agenda"
    detalhe = ft.Text("Toca num evento.", italic=True)

    def ao_clicar(evento):
        detalhe.value = f"{evento['titulo']}: {evento['descricao']}"
        page.update()

    def cartao(evento):
        return ft.Card(
            ft.ListTile(
                leading=ft.Icon(ICONES[evento["categoria"]]),
                title=ft.Text(evento["titulo"]),
                subtitle=ft.Text(f"{evento['dia']}, {evento['hora']} · {evento['local']}"),
                on_click=lambda e: ao_clicar(evento),
            )
        )

    page.add(ft.ListView([cartao(ev) for ev in EVENTOS], height=300), detalhe)


ft.run(main)
