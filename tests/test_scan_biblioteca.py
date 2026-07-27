"""
Tests para el módulo de escaneo de biblioteca musical.
"""

import os
import shutil
import tempfile

import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


# ============ TESTS EXISTENTES (ya pasan) ============

class TestEscanearCarpeta:
    """Tests básicos para escanear una carpeta."""

    def test_encuentra_archivos_mp3(self):
        from src.scan_biblioteca import escanear_carpeta
        resultados = escanear_carpeta(FIXTURES_DIR)
        nombres = [r["filename"] for r in resultados]
        assert "test_song.mp3" in nombres

    def test_encuentra_archivos_flac(self):
        from src.scan_biblioteca import escanear_carpeta
        resultados = escanear_carpeta(FIXTURES_DIR)
        nombres = [r["filename"] for r in resultados]
        assert "test_song.flac" in nombres

    def test_no_encuentra_archivos_no_audio(self):
        from src.scan_biblioteca import escanear_carpeta
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                os.path.join(FIXTURES_DIR, "test_song.mp3"),
                os.path.join(tmpdir, "cancion.mp3")
            )
            with open(os.path.join(tmpdir, "readme.txt"), "w") as f:
                f.write("Esto no es música")
            resultados = escanear_carpeta(tmpdir)
            assert len(resultados) == 1
            assert resultados[0]["filename"] == "cancion.mp3"

    def test_cada_resultado_tiene_estructura_correcta(self):
        from src.scan_biblioteca import escanear_carpeta
        resultados = escanear_carpeta(FIXTURES_DIR)
        resultado_valido = [r for r in resultados if "error" not in r][0]
        assert "filename" in resultado_valido
        assert "filepath" in resultado_valido
        assert "friendly" in resultado_valido
        assert "raw" in resultado_valido
        assert "technical" in resultado_valido

    def test_carpeta_vacia_devuelve_lista_vacia(self):
        from src.scan_biblioteca import escanear_carpeta
        with tempfile.TemporaryDirectory() as tmpdir:
            resultados = escanear_carpeta(tmpdir)
            assert resultados == []

    def test_carpeta_no_existente_lanza_error(self):
        from src.scan_biblioteca import escanear_carpeta
        with pytest.raises((FileNotFoundError, ValueError)):
            escanear_carpeta("C:\\esta\\carpeta\\no\\existe\\12345")

    def test_maneja_archivo_corrupto_sin_romperse(self):
        from src.scan_biblioteca import escanear_carpeta
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                os.path.join(FIXTURES_DIR, "test_song.mp3"),
                os.path.join(tmpdir, "valido.mp3")
            )
            with open(os.path.join(tmpdir, "corrupto.mp3"), "wb") as f:
                f.write(b"esto no es un mp3")
            resultados = escanear_carpeta(tmpdir)
            assert len(resultados) == 2
            validos = [r for r in resultados if "error" not in r]
            errores = [r for r in resultados if "error" in r]
            assert len(validos) == 1
            assert len(errores) == 1
            assert validos[0]["filename"] == "valido.mp3"
            assert errores[0]["filename"] == "corrupto.mp3"


class TestContarConTag:
    """Tests para contar archivos con tags específicos."""

    def test_cuenta_archivos_con_lyrics(self):
        from src.scan_biblioteca import contar_con_tag
        datos = [
            {"friendly": {"lyrics": "una letra"}},
            {"friendly": {"lyrics": "otra letra"}},
            {"friendly": {"title": "sin letra"}},
        ]
        assert contar_con_tag(datos, "lyrics") == 2

    def test_cuenta_cero_si_ninguno_tiene_el_tag(self):
        from src.scan_biblioteca import contar_con_tag
        datos = [
            {"friendly": {"title": "algo"}},
            {"friendly": {"artist": "otro"}},
        ]
        assert contar_con_tag(datos, "lyrics") == 0

    def test_ignora_errores(self):
        from src.scan_biblioteca import contar_con_tag
        datos = [
            {"friendly": {"lyrics": "una letra"}},
            {"error": "no se pudo leer"},
        ]
        assert contar_con_tag(datos, "lyrics") == 1


class TestContarSinMetadatos:
    """Tests para contar archivos sin metadatos."""

    def test_cuenta_friendly_vacio(self):
        from src.scan_biblioteca import contar_sin_metadatos
        datos = [{"friendly": {"title": "algo"}}, {"friendly": {}}]
        assert contar_sin_metadatos(datos) == 1

    def test_cuenta_errores(self):
        from src.scan_biblioteca import contar_sin_metadatos
        datos = [{"friendly": {"title": "algo"}}, {"error": "no se pudo leer"}]
        assert contar_sin_metadatos(datos) == 1

    def test_cuenta_cero_si_todos_tienen_metadatos(self):
        from src.scan_biblioteca import contar_sin_metadatos
        datos = [{"friendly": {"title": "uno"}}, {"friendly": {"title": "dos"}}]
        assert contar_sin_metadatos(datos) == 0


class TestGuardarJson:
    """Tests para exportar a JSON."""

    def test_guardar_json_crea_archivo(self):
        import json
        from src.scan_biblioteca import guardar_json
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_salida = os.path.join(tmpdir, "test.json")
            datos = [{"filename": "test.mp3", "friendly": {"title": "Test"}}]
            guardar_json(datos, ruta_salida)
            assert os.path.exists(ruta_salida)
            with open(ruta_salida, "r", encoding="utf-8") as f:
                contenido = json.load(f)
            assert contenido[0]["filename"] == "test.mp3"

    def test_guardar_json_preserva_acentos(self):
        import json
        from src.scan_biblioteca import guardar_json
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta_salida = os.path.join(tmpdir, "test.json")
            datos = [{"filename": "canción.mp3", "friendly": {"title": "Quince mil"}}]
            guardar_json(datos, ruta_salida)
            with open(ruta_salida, "r", encoding="utf-8") as f:
                contenido = json.load(f)
            assert contenido[0]["filename"] == "canción.mp3"


# ============ TESTS NUEVOS: CASOS BORDER ============

class TestCasosBorder:
    """Tests para casos edge y archivos 'raros'."""

    def test_archivo_sin_tags_devuelve_friendly_vacio(self):
        """
        Un MP3 válido pero sin tags debe tener friendly vacío.
        Usa el fixture sin_tags.mp3
        """
        from src.scan_biblioteca import escanear_carpeta

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                os.path.join(FIXTURES_DIR, "sin_tags.mp3"),
                os.path.join(tmpdir, "sin_tags.mp3")
            )

            resultados = escanear_carpeta(tmpdir)

            assert len(resultados) == 1
            assert resultados[0]["filename"] == "sin_tags.mp3"
            assert resultados[0]["friendly"] == {}

    def test_ruta_con_espacios_y_tildes(self):
        """
        Debe funcionar con rutas que tengan espacios y caracteres especiales.
        """
        from src.scan_biblioteca import escanear_carpeta

        with tempfile.TemporaryDirectory() as tmpdir:
            carpeta_especial = os.path.join(tmpdir, "Música Española")
            os.makedirs(carpeta_especial)

            shutil.copy(
                os.path.join(FIXTURES_DIR, "test_song.mp3"),
                os.path.join(carpeta_especial, "canción.mp3")
            )

            resultados = escanear_carpeta(carpeta_especial)

            assert len(resultados) == 1
            assert resultados[0]["filename"] == "canción.mp3"

    def test_archivo_mp3_que_es_flac_renombrado(self):
        """
        Un archivo .mp3 que en realidad es FLAC debe manejarse gracefully.
        mutagen debería detectar el formato real por el contenido, no la extensión.
        """
        from src.scan_biblioteca import escanear_carpeta

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                os.path.join(FIXTURES_DIR, "falso.mp3"),
                os.path.join(tmpdir, "falso.mp3")
            )

            resultados = escanear_carpeta(tmpdir)

            assert len(resultados) == 1
            # mutagen debería detectar que es FLAC a pesar de la extensión .mp3
            # o reportar error si no puede leerlo
            # Lo importante: NO rompe el escaneo
            assert resultados[0]["filename"] == "falso.mp3"

    def test_ruta_que_no_es_carpeta_lanza_error(self):
        """
        Si la ruta es un archivo (no carpeta), debe lanzar ValueError.
        """
        from src.scan_biblioteca import escanear_carpeta

        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear un archivo (no carpeta)
            archivo = os.path.join(tmpdir, "soy_un_archivo.txt")
            with open(archivo, "w") as f:
                f.write("hola")

            with pytest.raises(ValueError):
                escanear_carpeta(archivo)