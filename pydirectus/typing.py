from typing import TypeAlias, List, Any, Union, Dict, Optional
import uuid

# Custom type definitions
Alias: TypeAlias = str
Other: TypeAlias = str
Csv: TypeAlias = List[str]
Hash: TypeAlias = str
Uuid = str   # can't type as uuid.UUID because directus is str
Json = Union[Dict[str, Any], List[Any]]