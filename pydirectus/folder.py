from io import BytesIO
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from datetime import datetime
import logging

from .file import File
from .session import Session
from .query import Query

console = Console()

class Folder():
    """Files class to handle files in Directus

    https://docs.directus.io/reference/system/folders.html#folders
    """
    def __init__(self,
                 id: str,
                 name: str,
                 parent: str | None,
                 session: Session) -> None:
        # folder only have 3 fields so we do it the simple way
        self._session = session
        self.id: str = id
        self.name: str = name
        self.parent: str = parent

    def __repr__(self) -> str:
        return f"<Folder {self.name}>"

    def create_folder(self, name: str) -> 'Folder':
        """Create a subfolder in the current folder."""
        folder = {"name": name, "parent": self.id}
        resp = self._session.post("folders", data=folder)
        if resp.ok:
            return Folder(name=resp.data['name'],
                      parent=self.id,
                      id=resp.data['id'],
                      session=self._session)
        else:
            logging.error(f"Failed to create folder {name}: {resp.error_message}")
            return None


    def display_files(self, limit: int = 10) -> None:
        "Display files in the folder"
        table = Table(title=f"{self.name} files", box=box.ROUNDED)

        # we respect the user order if exists otherwise we use the order from the API
        columns = ['name', 'type', 'filesize', 'width', 'height', 'uploaded_on']
        # Add columns and rows
        for col in columns:
            table.add_column(col)
        files = self.files(limit=limit)
        for file in files:
            row = [
                file.filename_download,
                file.type.split('/')[1],
                file.pretty_filesize,
                str(file.width) if file.width else '',
                str(file.height) if file.height else '',
                file.uploaded_on.strftime('%Y-%m-%d')
            ]
            table.add_row(*row)

        # Display the table
        console.print(table)

    def filenames(self) -> list[str]:
        "Return the list of filename_download"
        files = self.files()
        return [f.filename_download for f in files]

    def files(self, limit: int = 0) -> list[File]:
        "Get files using search API"
        qry = Query(endpoint='files',
                    name='',  # files don't use collection
                    selected_fields=['*'],
                    all_fields=[],
                    session=self._session)

        qry.filter("folder").eq(self.id)
        if limit:
            qry.limit(limit)
        resp = qry.fetch()
        if len(resp) == 0:
            return []
        else:
            files = [File(f, session=self._session) for f in resp]
            return files


    # file handling
    def fileinfo(self, name: str) -> File:
        "Get a file by name"
        qry = Query(endpoint='files',
                    name='',  # files don't use collection
                    selected_fields=['*'],
                    all_fields=[],
                    session=self._session)
        qry.filter("filename_download").eq(name)
        qry = qry.limit(1)
        resp = qry.fetch()
        if resp:
            return File(resp[0], session=self._session)
        else:
            logging.warning(f"File {name} not found")
            return None

    def exists(self, name: str) -> bool:
        "Check if a file exists"
        return bool(self.fileinfo(name))

    def download(self, name: str, dirpath: str, ondisk_filename: str = "",
                 width: int = 0, height: int = 0, format: str = "",
                 quality: int = 0) -> bool:
        """Download the file on disk

        Args:
            name: the name of the file (filename_download) to download

            dirpath: the directory path where to save the file

            ondisk_name: Optionally Specify a different filename.
            Defaults to "" which will use the filename_download from the API as
            the filename.

            width: Optionally specify a resized image width. Defaults to 0 which will
            use the original width.

            height: Optionally specify a resized image height. Defaults to 0 which will
            use the original height.

            format: Optionally specify a different image format. Defaults to "" which
            will use the original format.

            quality: Optionally specify the image quality. Defaults to 0 which will
            use directus default quality.

        Returns:
            bool: True if the file was downloaded successfully
        """

        if (width or height or format) and not ondisk_filename:
                raise ValueError("Resize and format transcoding requires to specify the ondisk_name")

        file_bytes = self.download_bytes(name=name, width=width, height=height,
                                         format=format, quality=quality)

        if not file_bytes:
            logging.error(f"Error downloading file {name}")
            return False

        if not ondisk_filename:
            ondisk_filename = self.filename_download

        dirpath = Path(dirpath)
        if not dirpath.exists():
            dirpath.mkdir(parents=True)
        full_path = dirpath / ondisk_filename
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        return True

    def download_bytes(self, name: str, width: int = 0, height: int = 0,
                       format: str = "", quality: int = 0) -> bytes:
        """Get the file bytes

            width: Optionally specify a resized image width. Defaults to 0 which will
            use the original width.

            height: Optionally specify a resized image height. Defaults to 0 which will
            use the original height.

            format: Optionally specify a different image format. Defaults to "" which
            will use the original format.

            quality: Optionally specify the image quality. Defaults to 0 which will
            use directus default quality.

        Returns:
            bytes: The file bytes
        """
        # get file metadata
        file = self.fileinfo(name)
        if not file:
            raise ValueError(f"File {name} not found")

        if not file.type.startswith("image") and (width or height or format):
            raise ValueError("Resize and format transcoding is only available for images")

        # format check
        format = 'jpg' if format == 'jpeg' else format
        if format not in ['jpg', 'png', 'webp', 'avif']:
            raise ValueError("Invalid format. Supported formats are jpg, png, webp, avif")

        # build the query
        query = []
        if format:
            query.append(f"format={format}")
        if width:
            query.append(f"width={width}")
        if height:
            query.append(f"height={height}")
        if quality:
            query.append(f"quality={quality}")
        query = "&".join(query) if query else ""

        endpoint = f"/assets/{file.id}"
        if query:
            endpoint += f"?{query}"
        logging.debug(f"Download:{file.filename_download} from {endpoint}")
        return self._session.download(endpoint)

    def upload(self, filepath: str, filename: str = "",
               title: str = "") -> File:
        """Upload a file to the folder"""
        filepath = Path(filepath)
        if not filepath.exists():
            raise ValueError(f"File {filepath} not found")
        with open(filepath, "rb") as f:
            data = f.read()

        # pickup the filename from the path if not provided
        filename = filename if filename else filepath.name

        # pickup the title from the path if not provided
        title = title if title else filepath.stem

        # reuse the upload_bytes method
        return self.upload_bytes(data, filename, title)

    def upload_bytes(self, data: bytes, filename: str, title: str = "") -> File:
        """Upload bytes as files to the folder"""

        if not title:
            title = filename

        metadata  = {
            'folder': self.id,
            'title': title,
        }

        files = {'file': (filename, data)}
        resp = self._session.upload('files', data=metadata, files=files)
        if resp.ok:
            return File(resp.data, session=self._session)
        else:
            logging.error(f"Error uploading file {filename}: {resp.error_message}")
            return None

    def delete(self, names: str | list[str]) -> bool:
        """Delete file(s) from the folder

        Args:
            names: A single filename or a list of filenames to delete.

        """
        if isinstance(names, str):
            names = [names]

        # collect files ids
        ids = []
        for name in names:
            f = self.fileinfo(name)
            if not f:
                logging.error(f"File {name} not found aborting")
                return False
            ids.append(f.id)

        data = {"keys": ids}
        resp = self._session.delete(f"files/", data=data)
        if resp.ok:
            logging.info(f"Deleted {len(ids)} files")
            return True
        else:
            logging.error(f"Error deleting files {names}: {resp.error_message}")
            return False