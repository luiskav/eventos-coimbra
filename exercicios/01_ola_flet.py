"""Exercício 01 (Fase 0, tarefa 0.4): o primeiro ecrã em Flet.

Correr:  flet run exercicios/01_ola_flet.py
Desafio: muda o texto para o teu nome e acrescenta um segundo Text por baixo.
"""

import flet as ft


def main(page: ft.Page):
    page.title = "Olá Flet"
    page.add(
        ft.Text("Olá, Coimbra!", size=32, weight=ft.FontWeight.BOLD),
        ft.Text("O meu primeiro ecrã em Python."),
    )


ft.run(main)
