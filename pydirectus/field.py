from .typing import Alias, Other, Csv, Hash, Uuid, Json, Union, List

class Field():
    "Directus field object"
    # from https://docs.directus.io/user-guide/overview/glossary.html#types
    TYPE_MAP = {
        'alias': Alias,   # that's when it points to another table
        'integer': int,
        'bigint': int,
        'string': str,
        'text': str,
        'character varying': str,
        'boolean': bool,
        'float': float,
        'decimal': float,
        'binary': bytes,
        'timestamp': int,
        'datetime': int,
        'date': str,
        'time': str,
        'json': Json,
        'csv': Csv,
        'uuid': Uuid,
        'hash': Hash,
    }

    name: str
    type: str
    pytype: Other
    is_indexed: bool = False
    is_unique: bool = False
    is_nullable: bool = False
    is_primary_key: bool = False
    has_auto_increment: bool = False
    max_length: int = 0

    def __init__(self, data: dict) -> None:
        if not data:
            raise ValueError("Field data is empty")
        self.name = data['field']
        self.type = data['type']
        # casting type to python type for hint and type checking
        self.pytype = self.TYPE_MAP.get(data['type'].lower(), Other)

        # field keys properties -- wed on't part everthing
        if data.get('schema'):
            self.is_indexed = data['schema'].get('is_indexed', False)
            self.is_unique = data['schema'].get('is_unique', False)
            self.is_nullable = data['schema'].get('is_nullable', False)
            self.is_primary_key = data['schema'].get('is_primary_key')
            self.has_auto_increment = data['schema'].get('has_auto_increment')
            self.max_length = data['schema'].get('max_length', 0)
        if data.get('meta'):
            self.is_required = data['meta'].get('required', False)


