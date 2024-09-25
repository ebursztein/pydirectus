import json
import logging
from rich.table import Table
from rich.console import Console
from .session import Session
from .field import Field
from .typing import Union, List, Optional, Any
from .query import Query, FilterBuilder, LogicalOperator, _FilterBuilderWithOperators


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
        if not meta.ok:
            raise ValueError(f"Error fetching collection {name}")

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
            logging.error(f"Error fetching fields for collection {name}")
            return

        fields = {}
        for f in fdata.data:
            fld = Field(f)
            fields[fld.name] = fld
        self.fields = fields


    def __repr__(self) -> str:
        return f"<Collection {self.name}>"

    # [Fields](https://docs.directus.io/reference/system/fields.html)
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
        table.add_column("Max Length", style="green")

        for field in self.fields.values():
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
                str(field.max_length)
            )
        console.print(table)

    def get_field(self, name: str) -> Field:
        "Get a field by name"
        if name not in self.fields:
            logging.error(f"Field {name} not found in collection {self.name}")
            return None
        return self.fields.get(name)

    def field_names(self) -> list[str]:
        "Get all fields names"
        return list(self.fields.keys())

    def field_exists(self, name: str) -> bool:
        "Check if a field exists in the collection"
        return name in self.fields


    def query(self, fields: List[str] | str = '*') -> Query:
        """run a query object to select fields and filter results.
        Args:
            fields: A list of field names to select.

        Returns:
            The Query object for chaining.

        Notes:
        The query object is independent of the collection object because you
        can have multiple queries on the same collection object that you want
        to reuse and having the collection stateless is useful for parallelization.

        """
        return Query(endpoint='items',
                     name=self.name,
                     selected_fields=fields,
                     all_fields=self.fields,
                     session=self._session)

    def get(self, id: int) -> dict:
        """Get a single record by id.

        Args:
            id: The record id to fetch.

        Returns:
            The record data as a dictionary.
        """
        resp = self._session.get(f"items/{self.name}/{id}")
        if not resp.ok:
            logging.error(f"Error fetching item {id}: {resp.error_message}")
            return None
        return resp.data

    def get_all(self) -> list[dict[str, Field]]:
        "get all the collection records"
        return self.query(['*']).fetch()


    def delete(self, ids: int | list[int]) -> None:
        """Delete record(s) in the collection.

        Args:
            ids: A single record id or a list of record ids to delete.
        Returns:
            None
        """
        if isinstance(ids, int):
            ids = [ids]
        payload = {"keys": ids}
        resp = self._session.delete(f"items/{self.name}", payload)
        if not resp.ok:
            logging.error(f"Error deleting items: {resp.error_message}")


    def insert(self,
               items: list[dict[str, Any]] | dict[str, Any]) -> list[dict] | dict:
        """Insert record(s) in the collection.

        Args:
            items: A single record or a list of records to insert as dictionaries.
        Returns:
            The inserted record(s).
        """
        # box single item in a list
        if isinstance(items, dict):
            items = [items]

        # check fields:
        for idx, item in enumerate(items):
            try:
                self._validate_item(item)
            except ValueError as e:
                logging.error(f"Error validating item {idx}: {e}")
                return None

        resp = self._session.post(f"items/{self.name}", items)
        if not resp.ok:
            logging.error(f"Error inserting items: {resp.error_message}")
            return None
        return resp.data

    def update(self, ids: int | list[int], items: dict[str, Any]) -> dict:
        if isinstance(ids, int):
            ids = [ids]
            items = [items]
        if len(ids) != len(items):
            raise ValueError("ids and data must have the same length")

        # validate items
        for idx, item in enumerate(items):

            try:
                self._validate_item(item)
            except ValueError as e:
                logging.error(f"Error validating item {ids[idx]}: {e}")
                return None

        # There seems no way to update items with different values so we loop
        # https://docs.directus.io/reference/items.html#update-an-item
        # we do after all validation to avoid partial updates
        data = []
        errors = []
        for idx, item in enumerate(items):
            resp = self._session.patch(f"items/{self.name}/{ids[idx]}", item)
            if not resp.ok:
                logging.error(f"Error updating item {ids[idx]}: {resp.error_message}")
                data.append(None)
                errors.append(f"{ids[idx]}: {resp.error_message}\n")
            data.append(resp.data)
        if len(errors) > 0:
            print(f"Update partially failed with {len(errors)} errors:\n{errors}")
        return data

    def _validate_item(self, data: dict):
        "check if the item data is valid based of the collection fields structure"
        for field, value in data.items():
            if field not in self.fields:
                raise ValueError(f"Field {field} not found in collection {self.name}")
            field_def = self.fields[field]
            if not field_def.is_nullable and value is None:
                raise ValueError(f"Field {field} can't be null")
            if field_def.max_length and len(str(value)) > field_def.max_length:
                raise ValueError(f"Field {field} max length is {field_def.max_length}")
            if field_def.pytype != type(value):
                raise ValueError(f"Field {field} type is {field_def.pytype} but got {type(value)}")