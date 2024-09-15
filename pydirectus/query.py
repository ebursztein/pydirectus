from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import json
from rich import print  # Import rich's print function
from rich.panel import Panel
from rich.syntax import Syntax
from rich.console import Console
from rich.table import Table

console = Console()  # Create a Rich console object


class OperatorType(Enum):
    """Enum representing the types of filter operators."""
    COMPARISON = "comparison"
    EQUALITY = "equality"
    RANGE = "range"
    STRING = "string"
    ARRAY = "array"
    LOGICAL = "logical"
    GEOMETRIC = "geometric"
    SPECIAL = "special"


@dataclass
class Operator:
    """Represents a filter operator."""
    name: str
    symbol: str
    op_type: OperatorType


class Operators:
    """A collection of predefined filter operators."""

    # Equality
    EQ = Operator("eq", "_eq", OperatorType.EQUALITY)
    NEQ = Operator("neq", "_neq", OperatorType.EQUALITY)

    # Comparison
    LT = Operator("lt", "_lt", OperatorType.COMPARISON)
    LTE = Operator("lte", "_lte", OperatorType.COMPARISON)
    GT = Operator("gt", "_gt", OperatorType.COMPARISON)
    GTE = Operator("gte", "_gte", OperatorType.COMPARISON)

    # Array
    IN = Operator("in", "_in", OperatorType.ARRAY)
    NIN = Operator("nin", "_nin", OperatorType.ARRAY)

    # Special
    NULL = Operator("null", "_null", OperatorType.SPECIAL)
    NNULL = Operator("nnull", "_nnull", OperatorType.SPECIAL)

    # String
    CONTAINS = Operator("contains", "_contains", OperatorType.STRING)
    ICONTAINS = Operator("icontains", "_icontains", OperatorType.STRING)
    NCONTAINS = Operator("ncontains", "_ncontains", OperatorType.STRING)
    STARTS_WITH = Operator("starts_with", "_starts_with", OperatorType.STRING)
    ISTARTS_WITH = Operator("istarts_with", "_istarts_with", OperatorType.STRING)
    NSTARTS_WITH = Operator("nstarts_with", "_nstarts_with", OperatorType.STRING)
    NISTARTS_WITH = Operator("nistarts_with", "_nistarts_with", OperatorType.STRING)
    ENDS_WITH = Operator("ends_with", "_ends_with", OperatorType.STRING)
    IENDS_WITH = Operator("iends_with", "_iends_with", OperatorType.STRING)
    NENDS_WITH = Operator("nends_with", "_nends_with", OperatorType.STRING)
    NIENDS_WITH = Operator("niends_with", "_niends_with", OperatorType.STRING)

    # Range
    BETWEEN = Operator("between", "_between", OperatorType.RANGE)
    NBETWEEN = Operator("nbetween", "_nbetween", OperatorType.RANGE)

    # Special
    EMPTY = Operator("empty", "_empty", OperatorType.SPECIAL)
    NEMPTY = Operator("nempty", "_nempty", OperatorType.SPECIAL)

    # Geometric
    INTERSECTS = Operator("intersects", "_intersects", OperatorType.GEOMETRIC)
    NINTERSECTS = Operator("nintersects", "_nintersects", OperatorType.GEOMETRIC)
    INTERSECTS_BBOX = Operator("intersects_bbox", "_intersects_bbox", OperatorType.GEOMETRIC)
    NINTERSECTS_BBOX = Operator("nintersects_bbox", "_nintersects_bbox", OperatorType.GEOMETRIC)

    # Special
    REGEX = Operator("regex", "_regex", OperatorType.SPECIAL)

    # Logical
    AND = Operator("and", "_and", OperatorType.LOGICAL)
    OR = Operator("or", "_or", OperatorType.LOGICAL)

    @classmethod
    def get_all(cls) -> List[Operator]:
        """Returns a list of all defined operators."""
        return [value for value in cls.__dict__.values() if isinstance(value, Operator)]


class FilterBuilder:
    """Builds filter rules for a specific field."""

    def __init__(self, field: str, query: 'Query'):
        self.field = field
        self.filter_dict: Dict[str, Any] = {field: {}}  # Initialize with an empty dict for the field
        self.query = query  # Reference to the Query object

    def apply_operator(self, operator: Operator, value: Any) -> 'FilterBuilder':
        """Applies the given operator and value to the filter."""
        self.filter_dict[self.field][operator.symbol] = value
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Returns the filter as a dictionary."""
        return self.filter_dict if self.filter_dict[self.field] else {}

    def and_(self, *conditions: Union['FilterBuilder', 'LogicalOperator']) -> 'LogicalOperator':
        """Starts building a logical AND condition."""
        return self.query.logical_operator(Operators.AND, self, *conditions)

    def or_(self, *conditions: Union['FilterBuilder', 'LogicalOperator']) -> 'LogicalOperator':
        """Starts building a logical OR condition."""
        return self.query.logical_operator(Operators.OR, self, *conditions)

class LogicalOperator:
    """Represents a logical AND or OR operator that combines multiple filter rules."""

    def __init__(self, operator: Operator, *conditions: Union['FilterBuilder', 'LogicalOperator']):
        self.operator = operator
        self.conditions: List[Union[FilterBuilder, 'LogicalOperator']] = list(conditions)

    def add(self, condition: Union[FilterBuilder, 'LogicalOperator']) -> 'LogicalOperator':
        if isinstance(condition, LogicalOperator) and condition.operator == self.operator:
            for sub_condition in condition.conditions:
                self._add_single_condition(sub_condition)
        else:
            self._add_single_condition(condition)
        return self

    def _add_single_condition(self, condition: Union[FilterBuilder, 'LogicalOperator']):
        if isinstance(condition, FilterBuilder):
            if condition.filter_dict[condition.field]:  # Only add non-empty filters
                existing = next((c for c in self.conditions if isinstance(c, FilterBuilder) and c.field == condition.field), None)
                if existing:
                    for op, value in condition.filter_dict[condition.field].items():
                        if op in existing.filter_dict[existing.field]:
                            # If the operator already exists, replace the value instead of appending
                            existing.filter_dict[existing.field][op] = value
                        else:
                            existing.filter_dict[existing.field][op] = value
                else:
                    self.conditions.append(condition)
        else:
            self.conditions.append(condition)

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        return {self.operator.symbol: [condition.to_dict() for condition in self.conditions if condition.to_dict()]}

    def and_(self, *conditions: Union['FilterBuilder', 'LogicalOperator']) -> 'LogicalOperator':
        """Starts building a logical AND condition."""
        return self.add(LogicalOperator(Operators.AND, *conditions))

    def or_(self, *conditions: Union['FilterBuilder', 'LogicalOperator']) -> 'LogicalOperator':
        """Starts building a logical OR condition."""
        return self.add(LogicalOperator(Operators.OR, *conditions))

class _FilterBuilderWithOperators(FilterBuilder):  # Dummy class for autocompletion
    """Dummy class to help with type hinting and autocompletion."""
    # Add operator methods here with dummy implementations to aid autocompletion
    def eq(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def neq(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def lt(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def lte(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def gt(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def gte(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def in_(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nin(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def null(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nnull(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def contains(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def icontains(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def ncontains(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def starts_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def istarts_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nstarts_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nistarts_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def ends_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def iends_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nends_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def niends_with(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def between(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nbetween(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def empty(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nempty(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def intersects(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nintersects(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def intersects_bbox(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def nintersects_bbox(self, value: Any) -> '_FilterBuilderWithOperators':
        return self

    def regex(self, value: Any) -> '_FilterBuilderWithOperators':
        return self


class Query:
    """Represents a query with filters and selected fields."""

    def __init__(self, collection_name: str, selected_fields: list[str]):
        """Initializes a new Query object."""
        self.root: Optional[Union[FilterBuilder, LogicalOperator]] = None
        self.selected_fields: list[str] = selected_fields
        self.collection_name = collection_name

    def filter(self, field: str) -> '_FilterBuilderWithOperators':
        filter_builder = _FilterBuilderWithOperators(field, self)
        if self.root is None:
            self.root = filter_builder
        elif isinstance(self.root, FilterBuilder):
            if self.root.field == field:
                return self.root  # Return existing FilterBuilder for the same field
            self.root = LogicalOperator(Operators.AND, self.root, filter_builder)
        elif isinstance(self.root, LogicalOperator):
            existing = next((c for c in self.root.conditions if isinstance(c, FilterBuilder) and c.field == field), None)
            if existing:
                return existing  # Return existing FilterBuilder for the same field
            self.root.add(filter_builder)
        return filter_builder

    def logical_operator(
        self, operator: Operator, *conditions: Union[FilterBuilder, "LogicalOperator"]
    ) -> LogicalOperator:
        if self.root is None:
            self.root = LogicalOperator(operator, *conditions)
        elif isinstance(self.root, FilterBuilder):
            self.root = LogicalOperator(operator, self.root, *conditions)
        elif isinstance(self.root, LogicalOperator):
            if self.root.operator == operator:
                for condition in conditions:
                    self.root.add(condition)
            else:
                self.root = LogicalOperator(operator, self.root, *conditions)
        return self.root

    def and_(self, *conditions: Union[FilterBuilder, "LogicalOperator"]) -> LogicalOperator:
        """Starts building a logical AND condition."""
        return self.logical_operator(Operators.AND, *conditions)

    def or_(self, *conditions: Union[FilterBuilder, "LogicalOperator"]) -> LogicalOperator:
        """Starts building a logical OR condition."""
        return self.logical_operator(Operators.OR, *conditions)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the query as a dictionary."""
        return self.root.to_dict() if self.root else {}

    def to_json(self) -> str:
        """Returns the query as a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def explain(self) -> None:
        """Prints a colorized and formatted SQL-like explanation of the query using Rich."""
        if self.root is None:
            console.print("[bold blue]No filter applied[/]")
            return

        select_clause = f"SELECT {', '.join(self.selected_fields or ['*'])}"
        where_clause = self._explain_filter(self.root)

        sql_query = f"{select_clause}\nFROM {self.collection_name}\nWHERE {where_clause}"

        syntax = Syntax(sql_query, "sql", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="SQL Query Explanation", expand=False))

    def _explain_filter(self, filter_node: Union[FilterBuilder, LogicalOperator]) -> str:
        """Recursively builds the SQL-like explanation for filters."""
        if isinstance(filter_node, FilterBuilder):
            return self._explain_filter_builder(filter_node)
        elif isinstance(filter_node, LogicalOperator):
            return self._explain_logical_operator(filter_node)
        else:
            raise ValueError(f"Invalid filter node type: {type(filter_node)}")

    def _explain_filter_builder(self, filter_builder: FilterBuilder) -> str:
        """Returns a SQL-like explanation for a FilterBuilder."""
        field = filter_builder.field
        operators = {
            "_eq": "=",
            "_neq": "<>",
            "_lt": "<",
            "_lte": "<=",
            "_gt": ">",
            "_gte": ">=",
            "_contains": "LIKE",
            "_icontains": "LIKE",
            "_starts_with": "LIKE",
            "_istarts_with": "LIKE",
            "_ends_with": "LIKE",
            "_iends_with": "LIKE",
            "_between": "BETWEEN",
            "_in": "IN",
            "_nin": "NOT IN",
            "_null": "IS NULL",
            "_nnull": "IS NOT NULL",
            "_empty": "IS NULL",
            "_nempty": "IS NOT NULL",
            "_intersects": "INTERSECTS",
            "_nintersects": "NOT INTERSECTS",
            "_intersects_bbox": "INTERSECTS_BBOX",
            "_nintersects_bbox": "NOT INTERSECTS_BBOX",
            "_regex": "REGEX",
        }

        if not filter_builder.filter_dict[field]:  # Check if filter_dict[field] is empty
            return ""  # Return an empty string if no filter is applied

        explanations = []
        for op_symbol, op_value in filter_builder.filter_dict[field].items():
            try:
                sql_op = operators[op_symbol]
                if sql_op == "LIKE":
                    if op_symbol in ("_starts_with", "_istarts_with"):
                        sql_op = f"{field} LIKE '{op_value}%'"  # Add wildcard at the end
                    elif op_symbol in ("_ends_with", "_iends_with"):
                        sql_op = f"{field} LIKE '%{op_value}'"  # Add wildcard at the beginning
                    else:
                        sql_op = f"{field} LIKE '%{op_value}%'"
                elif sql_op == "BETWEEN":
                    if isinstance(op_value, list) and len(op_value) == 2:
                        sql_op = f"{field} BETWEEN {op_value[0]} AND {op_value[1]}"
                    else:
                        raise ValueError("BETWEEN operator requires a list of two values.")
                elif sql_op in ("IN", "NOT IN"):
                    if isinstance(op_value, list):
                        sql_op = f"{field} {sql_op} ({', '.join(map(repr, op_value))})"
                    else:
                        raise ValueError(f"{sql_op} operator requires a list of values.")
                else:
                    sql_op = f"{field} {sql_op} {repr(op_value)}"

                explanations.append(sql_op)  # Append to the list of explanations
            except (KeyError, IndexError, ValueError) as e:
                explanations.append(f"Error building SQL explanation for field '{field}': {e}")

        return " AND ".join(explanations)  # Join with AND for multiple filters on same field


    def _explain_logical_operator(self, logical_operator: LogicalOperator) -> str:
        explanation = []
        for condition in logical_operator.conditions:
            if isinstance(condition, FilterBuilder):
                exp = self._explain_filter_builder(condition)
                if exp:
                    explanation.append(exp)
            elif isinstance(condition, LogicalOperator):
                exp = self._explain_logical_operator(condition)
                if exp:
                    explanation.append(exp)
            else:
                raise ValueError(f"Invalid condition type: {condition}")

        if not explanation:
            return ""

        if logical_operator.operator.symbol == "_and":
            return " AND ".join(explanation)
        elif logical_operator.operator.symbol == "_or":
            return "(" + " OR ".join(explanation) + ")"
        else:
            return "Error building SQL explanation"

# Add methods to FilterBuilder for each operator
for op in Operators.get_all():
    if op.op_type != OperatorType.LOGICAL:
        setattr(_FilterBuilderWithOperators, op.name,
                lambda self, value, op=op: self.apply_operator(op, value))  # type: ignore


