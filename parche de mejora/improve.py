from typing import List

def evolvable(func):
    func.__evolvable__ = True
    return func

@evolvable
def summarize(text: str, max_words: int = 30) -> str:
    """
    Resumen extractivo muy simple:
    1) Normaliza espacios.
    2) Divide por frases.
    3) Selecciona frases con términos clave si caben.
    4) Si excede, recorta por palabras sin pasar max_words.
    No inventa datos: sólo reutiliza fragmentos del texto.
    """
    import re
    text = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", text) if text else []
    key_terms = {"objetivo", "requisito", "seguridad", "transparencia", "ArkAIOS", "2024"}

    chosen: List[str] = []
    for s in sentences:
        if any(k.lower() in s.lower() for k in key_terms):
            if len((" ".join(chosen + [s])).split()) <= max_words:
                chosen.append(s)

    if not chosen:
        # fallback: primeras palabras
        return " ".join(text.split()[:max_words])

    out = " ".join(chosen)
    words = out.split()
    if len(words) > max_words:
        out = " ".join(words[:max_words])
    return out
EOF
