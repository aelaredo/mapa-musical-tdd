import sys
from mutagen import File


def inspeccionar_archivo(ruta: str):
    """Muestra todos los metadatos técnicos y descriptivos de un archivo."""

    audio = File(ruta)

    if audio is None:
        print(f"❌ No se pudo leer: {ruta}")
        return

    print("=" * 60)
    print(f"📁 Archivo: {ruta}")
    print("=" * 60)

    # 1. INFORMACIÓN TÉCNICA (común a todos los formatos)
    print("\n🔧 INFORMACIÓN TÉCNICA:")
    print(f"   Formato detectado: {type(audio).__name__}")
    print(f"   Duración: {getattr(audio.info, 'length', 'N/A')} segundos")
    print(f"   Bitrate: {getattr(audio.info, 'bitrate', 'N/A')} bps")
    print(f"   Sample rate: {getattr(audio.info, 'sample_rate', 'N/A')} Hz")
    print(f"   Canales: {getattr(audio.info, 'channels', 'N/A')}")

    # 2. TODOS LOS TAGS (sin filtrar)
    print("\n🏷️  TODOS LOS TAGS/DESCRIPTORES:")

    if audio.tags is None:
        print("   (No hay tags)")
        return

    # MP3 usa ID3 (objeto especial)
    if hasattr(audio.tags, 'items'):
        # ID3: iterar sobre los frames
        for key, value in audio.tags.items():
            print(f"   {key}: {value}")
    else:
        # FLAC/Vorbis Comments: diccionario simple
        for key, value in audio.tags.items():
            print(f"   {key}: {value}")

    # 3. TAGS ESPECÍFICOS DE ALGUNOS FORMATOS
    print("\n📋 TAGS ESPECÍFICOS:")

    # Para MP3 (ID3), mostrar también los frames "human readable"
    if hasattr(audio.tags, 'getall'):
        print("   Frames ID3 disponibles:")
        for frame in audio.tags.values():
            print(f"      {frame.FrameID}: {frame}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/inspeccionar.py <ruta_del_archivo>")
        sys.exit(1)

    inspeccionar_archivo(sys.argv[1])