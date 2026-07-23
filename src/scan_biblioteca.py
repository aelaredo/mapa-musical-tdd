"""
Módulo para escanear carpetas de música y extraer metadatos.
TDD-friendly: devuelve datos, no imprime.
"""

import json
import os
from pathlib import Path

try:
    from src.metadata import MetadataReader
except ModuleNotFoundError:
    from metadata import MetadataReader


EXTENSIONES_AUDIO = {".mp3", ".flac", ".wav"}


def es_archivo_audio(nombre_archivo: str) -> bool:
    """Devuelve True si el archivo es un formato de audio soportado."""
    return Path(nombre_archivo).suffix.lower() in EXTENSIONES_AUDIO


def escanear_carpeta(ruta_carpeta: str) -> list[dict]:
    """
    Escanear una carpeta y devolver metadatos de todos los archivos de audio.

    Args:
        ruta_carpeta: Ruta a la carpeta a escanear.

    Returns:
        Lista de diccionarios con metadatos de cada archivo.
        Cada dict tiene: filename, filepath, friendly, raw, technical.
        Si hay error en un archivo, incluye "error" en el dict.

    Raises:
        FileNotFoundError: Si la carpeta no existe.
        ValueError: Si la ruta no es una carpeta.
    """
    ruta = Path(ruta_carpeta)

    if not ruta.exists():
        raise FileNotFoundError(f"La carpeta no existe: {ruta_carpeta}")

    if not ruta.is_dir():
        raise ValueError(f"No es una carpeta: {ruta_carpeta}")

    resultados = []

    for archivo in sorted(ruta.rglob("*")):
        if not archivo.is_file():
            continue

        if not es_archivo_audio(archivo.name):
            continue

        try:
            reader = MetadataReader(str(archivo))
            data = reader.read()

            resultados.append({
                "filepath": str(archivo),
                "filename": archivo.name,
                **data,
            })

        except Exception as e:
            resultados.append({
                "filepath": str(archivo),
                "filename": archivo.name,
                "error": str(e),
            })

    return resultados


def contar_con_tag(datos: list[dict], tag_name: str) -> int:
    """
    Cuenta cuántos archivos tienen un tag específico en friendly.

    Args:
        datos: Lista de resultados de escanear_carpeta().
        tag_name: Nombre del tag a buscar (ej: "lyrics", "title").

    Returns:
        Cantidad de archivos que tienen ese tag con valor no vacío.
    """
    return sum(
        1 for d in datos
        if "friendly" in d
        and tag_name in d["friendly"]
        and d["friendly"][tag_name]
    )


def contar_sin_metadatos(datos: list[dict]) -> int:
    """
    Cuenta archivos sin metadatos friendly o con error.

    Args:
        datos: Lista de resultados de escanear_carpeta().

    Returns:
        Cantidad de archivos sin metadatos útiles.
    """
    return sum(
        1 for d in datos
        if "error" in d
        or ("friendly" in d and not d["friendly"])
    )


def guardar_json(datos: list[dict], ruta_salida: str):
    """
    Guarda los datos en un archivo JSON.

    Args:
        datos: Lista de resultados de escanear_carpeta().
        ruta_salida: Ruta donde guardar el archivo JSON.
    """
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ============ SCRIPT CLI (opcional, para uso manual) ============

def _imprimir_resultados(resultados: list[dict], ruta_base: Path):
    """Imprime resultados en formato legible (para CLI)."""
    for r in resultados:
        if "error" in r:
            print(f"⚠️  Error en {r['filename']}: {r['error']}")
            continue

        print(f"📁 {r['filename']}")
        print(f"   Formato: {r['technical']['format']}")
        friendly = r.get('friendly', {})
        print(f"   Título:  {friendly.get('title') or '(sin título)'}")
        print(f"   Artista: {friendly.get('artist') or '(sin artista)'}")
        print(f"   Álbum:   {friendly.get('album') or '(sin álbum)'}")
        print()

    print("=" * 50)
    print(f"📊 Total: {len(resultados)}")
    print(f"❌ Con error: {sum(1 for r in resultados if 'error' in r)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python src/scan_biblioteca.py <ruta_de_la_carpeta>")
        print()
        print("Ejemplo:")
        print('  python src/scan_biblioteca.py "C:\\Users\\Agustín\\Music"')
        sys.exit(1)

    ruta = sys.argv[1]
    resultados = escanear_carpeta(ruta)
    _imprimir_resultados(resultados, Path(ruta))