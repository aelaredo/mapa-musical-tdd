import os

import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


class TestMetadataReader:
    """Tests para leer metadatos de archivos de audio."""

    def test_puede_leer_titulo_de_mp3(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert data["friendly"]["title"] == "Canción de Prueba"

    def test_puede_leer_artista_de_mp3(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert data["friendly"]["artist"] == "Artista de Prueba"

    def test_puede_leer_album_de_mp3(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert data["friendly"]["album"] == "Álbum de Prueba"

    def test_puede_leer_titulo_de_flac(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.flac")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert data["friendly"]["title"] == "Canción FLAC de Prueba"

    def test_puede_detectar_formato_mp3(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)

        assert reader.format == "mp3"

    def test_puede_detectar_formato_flac(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.flac")
        reader = MetadataReader(filepath)

        assert reader.format == "flac"

    def test_expone_raw_tags_mp3(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert "TIT2" in data["raw"]
        assert "TPE1" in data["raw"]
        assert "TALB" in data["raw"]

    def test_expone_raw_tags_flac(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.flac")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert "title" in data["raw"]  # ← minúscula
        assert "artist" in data["raw"]  # ← minúscula
        assert "album" in data["raw"]  # ← minúscula

    def test_archivo_no_existente_lanza_error(self):
        from mutagen._util import MutagenError
        from src.metadata import MetadataReader

        with pytest.raises((MutagenError, ValueError)):
            MetadataReader("no_existe.mp3")


    def test_expone_info_tecnica(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert data["technical"]["format"] == "mp3"
        assert data["technical"]["duration_seconds"] is not None
        assert data["technical"]["sample_rate_hz"] is not None

    def test_acceso_directo_get(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)

        assert reader.get("title") == "Canción de Prueba"
        assert reader.get("no_existe") is None
        assert reader.get("no_existe", "default") == "default"

    def test_acceso_con_corchetes(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "test_song.mp3")
        reader = MetadataReader(filepath)

        assert reader["title"] == "Canción de Prueba"


class TestCasosBorder:
    """Tests para casos edge."""

    def test_archivo_no_existente_lanza_error(self):
        from src.metadata import MetadataReader

        with pytest.raises(ValueError):
            MetadataReader("no_existe.mp3")

    def test_mp3_sin_tags_tiene_friendly_vacio(self):
        from src.metadata import MetadataReader

        filepath = os.path.join(FIXTURES_DIR, "sin_tags.mp3")
        reader = MetadataReader(filepath)
        data = reader.read()

        assert data["friendly"] == {}
        assert data["raw"] == {}