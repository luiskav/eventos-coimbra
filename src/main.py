"""Ponto de entrada da app (Fase 3, tarefa 3.5).

Correr em desenvolvimento:   flet run src/main.py          (janela)
                             flet run --web src/main.py    (browser)
"""

import flet as ft

from app import App


async def main(page: ft.Page):
    app = App(page)
    await app.iniciar()


ft.run(main)
