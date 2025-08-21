# brain.py
"""
Módulo "cerebro" editable por el agente.
Sólo se permite modificar funciones marcadas con @evolvable.
"""

from typing import List

def evolvable(func):
    func.__evolvable__ = True
    return func

@evolvable
def summarize(text: str, max_words: int = 30) -> str:
    """
    Objetivo: resumir texto respetando max_words palabras,
    manteniendo puntos clave y sin inventar datos.
    Implementación inicial muy simple.
    """
    words = text.strip().split()
    return " ".join(words[:max_words])

# evolutions:
# + 2025-08-14 00:38:41 - micro-tweak (noop)
