from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from datetime import datetime

from .session import Session
from .query import Query

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


    def display_files(self, limit: int = 10) -> None:
        "Display files in the folder"
        table = Table(title=f"{self.name} files", box=box.ROUNDED)

        # we respect the user order if exists otherwise we use the order from the API
        columns = ['title', 'type', 'filesize', 'width', 'height', 'uploaded_on']
        # Add columns and rows
        for col in columns:
            table.add_column(col)

        files = self._get_files(limit=limit)
        for file in files:
            row = []
            for col in columns:
                d = file.get(col, '')

                if col == 'type':
                    d = d.split('/')[1]

                if col == 'filesize':
                    size = int(d)
                    if size >= 1048576:  # 1 MB
                        d = f"{size/1048576:.2f} MB"
                    else:
                        d = f"{size/1024:.2f} KB"
                if col == 'uploaded_on':
                    date = datetime.fromisoformat(d.replace('Z', '+00:00'))
                    d = date.strftime('%Y-%m-%d')

                d = str(d) if str(d) != 'None' else ''

                row.append(str(d))
            table.add_row(*row)

        # Display the table
        Console().print(table)

    def file_names(self) -> list[str]:
        "Get all files names"
        files = self._get_files()
        return [f['filename_download'] for f in files]

    def _get_files(self, limit: int = 0) -> dict:
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
            return {}
        else:
            return resp