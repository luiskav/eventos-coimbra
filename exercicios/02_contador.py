"""Exercício 02 (Fase 0, tarefa 0.4): botões e eventos.

Cada clique chama uma função Python que muda o ecrã.
Desafio: acrescenta um botão "Repor" que põe o contador a zero.
"""

import flet as ft


def main(page: ft.Page):
    contador = ft.Text("0", size=48)

    def somar(e):
        contador.value = str(int(contador.value) + 1)
        page.update()

    def subtrair(e):
        contador.value = str(int(contador.value) - 1)
        page.update()

    page.add(
        ft.Row(
            [
                ft.IconButton(ft.Icons.REMOVE, on_click=subtrair),
                contador,
                ft.IconButton(ft.Icons.ADD, on_click=somar),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


ft.run(main)
