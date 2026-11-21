"""Favoritos guardados no próprio dispositivo, sem login (Fase 4, tarefa 4.1).

O armazenamento é injetado: na app é ft.SharedPreferences(); nos testes é um
dicionário falso. Os métodos são assíncronos porque o SharedPreferences do Flet é.
"""

from typing import Protocol


class Armazenamento(Protocol):
    async def get(self, key: str): ...
    async def set(self, key: str, value) -> bool: ...


class Favoritos:
    def __init__(self, armazenamento: Armazenamento, prefixo: str = "eventos"):
        self.armazenamento = armazenamento
        self.chave = f"{prefixo}.favoritos"
        self.ids: set[int] = set()

    async def carregar(self) -> None:
        try:
            guardados = await self.armazenamento.get(self.chave) or []
        except Exception:  # armazenamento indisponível: começa vazio
            guardados = []
        self.ids = {int(x) for x in guardados if str(x).lstrip("-").isdigit()}

    def contem(self, evento_id: int) -> bool:
        return evento_id in self.ids

    async def alternar(self, evento_id: int) -> bool:
        """Junta ou retira o evento. Devolve True se ficou nos favoritos."""
        if evento_id in self.ids:
            self.ids.remove(evento_id)
        else:
            self.ids.add(evento_id)
        await self.armazenamento.set(self.chave, [str(i) for i in sorted(self.ids)])
        return evento_id in self.ids
