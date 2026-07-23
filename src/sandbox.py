import sys

sys.path.insert(0, "src")  # Asegurar que importe desde src/

from metadata import MetadataReader

filepath = r"G:\Music\complete\New Sentimentality [2006-12-06] (ep)\03 New Sentimentality.flac"

print("=" * 60)
print("DEBUG: MetadataReader")
print("=" * 60)

reader = MetadataReader(filepath)

print(f"\n1. Formato detectado: {reader.format}")
print(f"2. Tipo de audio: {type(reader.audio).__name__}")
print(f"3. Tiene tags: {reader.audio.tags is not None}")

# Ver qué método read existe
print(f"\n4. Método read existe: {hasattr(reader, 'read')}")
print(f"5. Tipo de read: {type(reader.read)}")

# Ejecutar read y ver qué devuelve
print("\n6. Ejecutando read()...")
try:
    data = reader.read()
    print(f"   Tipo de retorno: {type(data)}")
    print(f"   Claves: {list(data.keys()) if isinstance(data, dict) else 'NO ES DICCIONARIO'}")

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"\n   --- {key} ---")
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"      {k}: {v}")
            else:
                print(f"      {value}")
except Exception as e:
    print(f"   ERROR: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()