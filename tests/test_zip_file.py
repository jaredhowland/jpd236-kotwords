import unittest
import zipfile
from io import BytesIO

from kotwords_py.formats.zip_file import InvalidZipError, Zip


class ZipTests(unittest.IsolatedAsyncioTestCase):
    async def test_zip_unzip_roundtrip(self) -> None:
        original = b"test payload"

        zipped = await Zip.zip("test.txt", original)
        unzipped = await Zip.unzip(zipped)

        self.assertEqual(original, unzipped)

    async def test_unzip_invalid_data_raises_invalid_zip_error(self) -> None:
        with self.assertRaisesRegex(InvalidZipError, "Error unzipping data"):
            await Zip.unzip(b"not-a-zip")

    async def test_unzip_raises_when_no_file_entries(self) -> None:
        zip_bytes = BytesIO()
        with zipfile.ZipFile(zip_bytes, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("folder/", "")

        with self.assertRaisesRegex(InvalidZipError, "No file entry in ZIP file"):
            await Zip.unzip(zip_bytes.getvalue())


if __name__ == "__main__":
    unittest.main()
