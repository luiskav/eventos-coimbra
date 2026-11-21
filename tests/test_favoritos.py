"""Testes dos favoritos com um armazenamento falso (Fase 4, tarefa 4.1)."""

import asyncio

from favoritos import Favoritos


class ArmazenamentoFalso:
    def __init__(self, inicial=None, falhar=False):
        self.dados = dict(inicial or {})
        self.falhar = falhar

    async def get(self, key):
        if self.falhar:
            raise RuntimeError("indisponível")
        return self.dados.get(key)

    async def set(self, key, value):
        self.dados[key] = value
        return True


def test_alternar_e_persistir():
    armazem = ArmazenamentoFalso()

    async def cenario():
        fav = Favoritos(armazem)
        await fav.carregar()
        assert await fav.alternar(5) is True
        assert await fav.alternar(3) is True
        assert await fav.alternar(5) is False
        novo = Favoritos(armazem)  # simula reabrir a app
        await novo.carregar()
        return novo

    novo = asyncio.run(cenario())
    assert novo.contem(3) and not novo.contem(5)
    assert armazem.dados["eventos.favoritos"] == ["3"]


def test_valores_estragados_e_ids_negativos():
    armazem = ArmazenamentoFalso({"eventos.favoritos": ["1", "abc", "-2"]})
    fav = Favoritos(armazem)
    asyncio.run(fav.carregar())
    assert fav.ids == {1, -2}


def test_armazenamento_indisponivel_comeca_vazio():
    fav = Favoritos(ArmazenamentoFalso(falhar=True))
    asyncio.run(fav.carregar())
    assert fav.ids == set()
