# improve.py  — ArkAIOS Safe Evolver (sin depender de pytest)
import sys, os, shutil, importlib, inspect, traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
BRAIN = ROOT / "brain.py"
SNAP = ROOT / "snapshots"
SNAP.mkdir(exist_ok=True)

def snapshot():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = SNAP / f"brain_{ts}.py"
    shutil.copy(BRAIN, dst)
    print(f"Snapshot guardado: {dst.name}")

def run_internal_tests():
    """
    Busca tests en test_spec.py o spec.py y los ejecuta
    directamente (sin pytest). Si no encuentra, pasa en modo dev.
    """
    for mod_name in ("test_spec", "spec"):
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            continue
        tests = []
        for name in dir(mod):
            if name.startswith("test_"):
                obj = getattr(mod, name)
                if callable(obj):
                    tests.append(obj)
        if not tests:
            return True, "No hay tests definidos (dev mode: PASS)."
        try:
            for t in tests:
                t()
            return True, f"{len(tests)} tests OK (runner interno)."
        except AssertionError as e:
            return False, f"Fallo en {t.__name__}: {e}"
        except Exception as e:
            return False, f"Error ejecutando tests: {e}\n{traceback.format_exc()}"
    # Si no hay ningún archivo de spec
    return True, "No se encontró spec; dev mode: PASS."

def evolve_brain():
    """
    Micro-evolución segura: añade una marca de evolución al final de brain.py.
    (No cambia lógica; sirve para verificar el ciclo snapshot->tests->apply)
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src = BRAIN.read_text(encoding="utf-8")
    if "\n# evolutions:" not in src:
        src += "\n# evolutions:\n"
    src += f"# + {ts} - micro-tweak (noop)\n"
    BRAIN.write_text(src, encoding="utf-8")
    print("Evolución aplicada al núcleo (marcado en brain.py).")

def main():
    print("-- ArkAIOS Safe Evolver --")
    snapshot()
    ok, msg = run_internal_tests()
    if ok:
        print(f"Tests base: OK  | {msg}")
        evolve_brain()
        print("Listo. Puedes volver a ejecutar para iterar.")
    else:
        print(f"Tests base: FALLAN | {msg}")
        print("Arregla los tests antes de evolucionar.")

if __name__ == "__main__":
    main()
