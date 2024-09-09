from rich.table import Table
from rich.console import Console
from .session import Session
from .typing import Alias, Other

class Field():
    "Directus field object"

    # from https://docs.directus.io/user-guide/overview/glossary.html#types
    TYPE_MAP = {
        'alias': Alias,   # that's when it point to another table

        'integer': int,
        'bigint': int,
        'string': str,
        'text': str,
        'character varying': str,

        'boolean': bool,

        'float': float,
        'decimal': float,
    }

    type: str
    pytype: Other
    is_indexed: bool = False
    is_unique: bool = False
    is_nullable: bool = False
    is_primary_key: bool = False
    has_auto_increment: bool = False


    def __init__(self, data: dict) -> None:
        if not data:
            raise ValueError("Field data is empty")
        self.name = data['field']
        self.type = data['type']
        # casting type to python type for hint and type checking
        self.pytype = self.TYPE_MAP.get(data['type'], Other)

        # field keys properties -- wed on't part everthing
        if data.get('schema'):
            self.is_indexed = data['schema'].get('is_indexed', False)
            self.is_unique = data['schema'].get('is_unique', False)
            self.is_nullable = data['schema'].get('is_nullable', False)
            self.is_primary_key = data['schema'].get('is_primary_key')
            self.has_auto_increment = data['schema'].get('has_auto_increment')

        if data.get('meta'):
            self.is_required = data['meta'].get('required', False)


class Collection():
    """Directus collection object
    https://docs.directus.io/reference/system/collections.html#the-collection-object

    Note:
    the api don't seems to return the `fields` key in the response so we
    fetch them separately in the constructor.
    """



    def __init__(self, name: str, session: Session) -> None:
        self.name = name
        self._session = session


        # get metadata
        meta = self._session.get(f"collections/{name}")
        self.icon = meta.data['meta']['icon']
        self.display_template = meta.data['meta']['display_template']
        self.hidden: bool = meta.data['meta']['hidden']
        self.singleton: bool = meta.data['meta']['singleton']
        self.translations = meta.data['meta']['translations']
        self.archive_field = meta.data['meta']['archive_field']
        self.archive_app_filter: bool = meta.data['meta']['archive_app_filter']
        self.archive_value = meta.data['meta']['archive_value']
        self.unarchive_value = meta.data['meta']['unarchive_value']
        self.sort_field = meta.data['meta']['sort_field']
        self.accountability: str = meta.data['meta']['accountability']
        self.color = meta.data['meta']['color']
        self.item_duplication_fields = meta.data['meta']['item_duplication_fields']
        self.sort = meta.data['meta']['sort']
        self.group = meta.data['meta']['group']
        self.collapse = meta.data['meta']['collapse']
        self.preview_url = meta.data['meta']['preview_url']
        self.versioning: bool = meta.data['meta']['versioning']

        # get fields
        fdata = self._session.get(f"fields/{name}")
        if not fdata.ok:
            return

        fields = []
        for f in fdata.data:
            fields.append(Field(f))
        self.fields = fields

    def display_fields(self) -> None:
        console = Console()
        table = Table(title=f"{self.name} Fields", row_styles=['dim', ''])

        table.add_column("Name", justify="left", style="blue", no_wrap=True)
        table.add_column("Type", style="yellow")
        table.add_column("PyType", style="magenta")
        table.add_column("Indexed", style="green")
        table.add_column("Unique", style="green")
        table.add_column("Nullable", style="green")
        table.add_column("Primary Key", style="green")
        table.add_column("Auto Increment", style="green")
        table.add_column("Required", style="green")

        for field in self.fields:
            table.add_row(
                field.name,
                field.type,
                str(field.pytype.__name__),  # Get type name for display
                "✔" if field.is_indexed else " ",
                "✔" if field.is_unique else " ",
                "✔" if field.is_nullable else " ",
                "✔" if field.is_primary_key else " ",
                "✔" if field.has_auto_increment else " ",
                "✔" if field.is_required else " ",
            )
        console.print(table)


    def __repr__(self) -> str:
        return f"<Collection {self.name}>"