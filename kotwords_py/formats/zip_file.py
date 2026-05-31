"""ZIP helpers used by format converters."""

from __future__ import annotations

import zipfile
from io import BytesIO


class InvalidZipError(Exception):
    """Exception raised when ZIP data is invalid."""


class Zip:
    """ZIP encoder/decoder helpers."""

    @staticmethod
    async def zip(filename: str, data: bytes) -> bytes:
        zip_bytes = BytesIO()
        with zipfile.ZipFile(zip_bytes, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(filename, data)
        return zip_bytes.getvalue()

    @staticmethod
    async def unzip(data: bytes) -> bytes:
        try:
            with zipfile.ZipFile(BytesIO(data), mode="r") as archive:
                for entry in archive.infolist():
                    if not entry.is_dir():
                        with archive.open(entry, mode="r") as zipped_file:
                            return zipped_file.read()
        except Exception as ex:
            raise InvalidZipError("Error unzipping data") from ex

        raise InvalidZipError("No file entry in ZIP file")
