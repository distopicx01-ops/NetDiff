import importlib


def load(name):
    """Carga una herramienta por el nombre de su carpeta.

    Las carpetas tienen guion (white-list), asi que no se pueden
    importar con "import". Usamos importlib.
    """
    return importlib.import_module(f"tools.{name}")