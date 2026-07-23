"""
Módulo para leer metadatos de archivos de audio.
Expone TODOS los metadatos disponibles.
"""
import os
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC


# Mapeo de frames ID3 a nombres amigables
ID3_TO_FRIENDLY = {
    "TIT2": "title",
    "TPE1": "artist",
    "TPE2": "album_artist",
    "TALB": "album",
    "TDRC": "year",
    "TYER": "year",
    "TRCK": "track",
    "TPOS": "disc",
    "TCON": "genre",
    "TCOM": "composer",
    "TPUB": "publisher",
    "TEXT": "lyricist",
    "USLT": "lyrics",
    "COMM": "comment",
    "APIC": "cover_art",
    "TBPM": "bpm",
    "TKEY": "key",
    "TLAN": "language",
    "TMED": "media",
    "TMOO": "mood",
    "TSRC": "isrc",
}

# Mapeo de Vorbis Comments a nombres amigables
VORBIS_TO_FRIENDLY = {
    "TITLE": "title",
    "ARTIST": "artist",
    "ALBUMARTIST": "album_artist",
    "ALBUM": "album",
    "DATE": "year",
    "YEAR": "year",
    "TRACKNUMBER": "track",
    "DISCNUMBER": "disc",
    "GENRE": "genre",
    "COMPOSER": "composer",
    "PUBLISHER": "publisher",
    "LYRICIST": "lyricist",
    "LYRICS": "lyrics",
    "COMMENT": "comment",
    "DESCRIPTION": "description",
    "BPM": "bpm",
    "KEY": "key",
    "LANGUAGE": "language",
    "MEDIA": "media",
    "MOOD": "mood",
    "ISRC": "isrc",
    "ENCODING": "encoding_settings",
    "LABEL": "label",
    "CATALOGNUMBER": "catalog_number",
    "BARCODE": "barcode",
    "ASIN": "asin",
    "RELEASECOUNTRY": "release_country",
    "RELEASETYPE": "release_type",
    "RELEASESTATUS": "release_status",
    "ORIGINALYEAR": "original_year",
    "ORIGINALDATE": "original_date",
    "SCRIPT": "script",
    "TRACKTOTAL": "total_tracks",
    "TOTALTRACKS": "total_tracks",
    "DISCTOTAL": "total_discs",
    "TOTALDISCS": "total_discs",
    "ALBUMARTISTSORT": "album_artist_sort",
    "ARTISTSORT": "artist_sort",
    "MUSICBRAINZ_ALBUMID": "mb_album_id",
    "MUSICBRAINZ_ARTISTID": "mb_artist_id",
    "MUSICBRAINZ_TRACKID": "mb_track_id",
    "MUSICBRAINZ_ALBUMARTISTID": "mb_album_artist_id",
    "MUSICBRAINZ_RELEASEGROUPID": "mb_release_group_id",
    "MUSICBRAINZ_RELEASETRACKID": "mb_release_track_id",
    "ACOUSTID_ID": "acoustid_id",
}


class MetadataReader:
    def __init__(self, filepath: str):
        self.filepath = filepath

        # Verificar que el archivo existe ANTES de pasar a mutagen
        if not os.path.exists(filepath):
            raise ValueError(f"El archivo no existe: {filepath}")

        self.audio = File(filepath)

        if self.audio is None:
            raise ValueError(f"No se pudo leer el archivo: {filepath}")

        self.format = self._detectar_formato()
        self._raw_tags = {}
        self._friendly_tags = {}

    def _detectar_formato(self) -> str:
        if isinstance(self.audio, MP3):
            return "mp3"
        elif isinstance(self.audio, FLAC):
            return "flac"
        return "unknown"

    def read(self) -> dict:
        """
        Lee todos los metadatos.

        Returns:
            {
                "friendly": {...},   # tags con nombres normalizados
                "raw": {...},        # tags originales del formato
                "technical": {...}   # info técnica (duración, bitrate, etc.)
            }
        """
        self._raw_tags = {}
        self._friendly_tags = {}

        if self.format == "mp3":
            self._read_mp3_tags()
        elif self.format == "flac":
            self._read_flac_tags()

        technical = {
            "format": self.format,
            "duration_seconds": getattr(self.audio.info, 'length', None),
            "bitrate_bps": getattr(self.audio.info, 'bitrate', None),
            "sample_rate_hz": getattr(self.audio.info, 'sample_rate', None),
            "channels": getattr(self.audio.info, 'channels', None),
        }

        return {
            "friendly": self._friendly_tags,
            "raw": self._raw_tags,
            "technical": technical,
        }

    def _read_mp3_tags(self):
        """Lee todos los frames ID3."""
        if self.audio.tags is None:
            return

        for frame_id, frame in self.audio.tags.items():
            self._raw_tags[frame_id] = self._extraer_valor_id3(frame)
            friendly_name = ID3_TO_FRIENDLY.get(frame_id)
            if friendly_name:
                self._friendly_tags[friendly_name] = self._raw_tags[frame_id]

    def _read_flac_tags(self):
        """Lee todos los Vorbis Comments."""
        if self.audio.tags is None:
            return

        for tag_name, value in self.audio.tags.items():
            tag_name_upper = tag_name.upper()
            self._raw_tags[tag_name] = self._extraer_valor_vorbis(value)
            friendly_name = VORBIS_TO_FRIENDLY.get(tag_name_upper)
            if friendly_name:
                self._friendly_tags[friendly_name] = self._raw_tags[tag_name]

    def _extraer_valor_id3(self, frame):
        """Extrae valor legible de un frame ID3."""
        if hasattr(frame, 'text'):
            if isinstance(frame.text, list):
                return str(frame.text[0]) if frame.text else None
            return str(frame.text)
        return str(frame)

    def _extraer_valor_vorbis(self, value):
        """Extrae valor de un tag Vorbis (viene como lista)."""
        if isinstance(value, list):
            return str(value[0]) if value else None
        return str(value)

    def get(self, key: str, default=None):
        """Acceso directo: reader.get('title')."""
        if not self._friendly_tags:
            self.read()
        return self._friendly_tags.get(key, default)

    def __getitem__(self, key: str):
        """Acceso directo: reader['title']."""
        return self.get(key)