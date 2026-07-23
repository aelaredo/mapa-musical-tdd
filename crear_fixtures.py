"""
Script de una sola ejecución: crea TODOS los archivos de audio de prueba.
"""

import os
import shutil
import subprocess

FIXTURES_DIR = "fixtures"


def run_ffmpeg(args):
    """Ejecuta ffmpeg y maneja errores."""
    result = subprocess.run(
        ["ffmpeg"] + args,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Error ffmpeg: {result.stderr}")
        return False
    return True


def create_test_mp3():
    """Crea un MP3 con metadatos de prueba."""
    os.makedirs(FIXTURES_DIR, exist_ok=True)
    filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")

    if not run_ffmpeg([
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "1", "-acodec", "libmp3lame", "-q:a", "4",
        "-id3v2_version", "0", "-y", filepath
    ]):
        return

    from mutagen.mp3 import MP3
    from mutagen.id3 import TIT2, TPE1, TALB

    audio = MP3(filepath)
    if audio.tags is None:
        audio.add_tags()
    audio.tags["TIT2"] = TIT2(encoding=3, text="Canción de Prueba")
    audio.tags["TPE1"] = TPE1(encoding=3, text="Artista de Prueba")
    audio.tags["TALB"] = TALB(encoding=3, text="Álbum de Prueba")
    audio.save()

    print(f"✅ MP3 con tags: {filepath}")


def create_test_flac():
    """Crea un FLAC con metadatos de prueba."""
    filepath = os.path.join(FIXTURES_DIR, "test_song.flac")

    if not run_ffmpeg([
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "1", "-acodec", "flac", "-y", filepath
    ]):
        return

    from mutagen.flac import FLAC

    audio = FLAC(filepath)
    audio["TITLE"] = "Canción FLAC de Prueba"
    audio["ARTIST"] = "Artista FLAC de Prueba"
    audio["ALBUM"] = "Álbum FLAC de Prueba"
    audio.save()

    print(f"✅ FLAC con tags: {filepath}")


def create_sin_tags_mp3():
    """Crea un MP3 válido pero SIN metadatos."""
    filepath = os.path.join(FIXTURES_DIR, "sin_tags.mp3")

    if not run_ffmpeg([
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "1", "-acodec", "libmp3lame", "-q:a", "4",
        "-id3v2_version", "0", "-y", filepath
    ]):
        return

    print(f"✅ MP3 sin tags: {filepath}")


def create_falso_mp3():
    """Crea un FLAC renombrado como .mp3 (para test de detección de formato)."""
    origen = os.path.join(FIXTURES_DIR, "test_song.flac")
    destino = os.path.join(FIXTURES_DIR, "falso.mp3")

    if not os.path.exists(origen):
        print("❌ Primero creá test_song.flac")
        return

    shutil.copy(origen, destino)
    print(f"✅ FLAC renombrado como MP3: {destino}")


if __name__ == "__main__":
    create_test_mp3()
    create_test_flac()
    create_sin_tags_mp3()
    create_falso_mp3()
    print("\n🎵 Todos los fixtures listos.")