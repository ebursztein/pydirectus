import pytest
from io import StringIO
import sys

from .query import Query
from .collection import Collection  # Import your actual classes
from .test_fixtures import load_directus_raw_response, get_available_test_data, mock_session

@pytest.fixture
def collection(mock_session):

    return Collection("books", mock_session)

# FIXME: add tests for the json rendering which is the most important part
# as it is what goes into directus

def test_single_filter(collection):
    query = collection.query(["title"])
    query.filter("title").contains("Robots")
    assert query.to_dict() == {
        "title": {
            "_contains": "Robots"
        }
    }

    sql = query.to_sql().replace("\n", " ").lower().strip()
    assert sql == "SELECT title FROM books WHERE title LIKE '%Robots%'".lower().strip()

    # check if explain works
    query.explain()

# def test_multiple_filters_different_fields(collection):
#     query = collection.select(["title", "rating"]).filter("title").contains("Robots").and_(
#         collection.filter("rating").gte(3)
#     )
#     assert query.to_dict() == {
#         "_and": [
#             {"title": {"_contains": "Robots"}},
#             {"rating": {"_gte": 3}}
#         ]
#     }
#     assert query.explain() == (
#         "SELECT title, rating\n"
#         "FROM books\n"
#         "WHERE title LIKE '%Robots%' AND rating >= 3"
#     )

# def test_multiple_filters_same_field(collection):
#     query = collection.select(["title"]).filter("title").contains("Robots").and_(
#         collection.filter("title").starts_with("The")
#     )
#     assert query.to_dict() == {
#         "_and": [
#             {"title": {"_contains": "Robots"}},
#             {"title": {"_starts_with": "The"}}
#         ]
#     }
#     assert query.explain() == (
#         "SELECT title\n"
#         "FROM books\n"
#         "WHERE title LIKE '%Robots%' AND title LIKE 'The%'"
#     )

# def test_combining_and_or(collection):
#     query = collection.select(["title", "rating", "genres"]).filter("title").contains("Robots").and_(
#         collection.filter("rating").gte(3)
#     ).or_(
#         collection.filter("genres").in_(["Scifi", "Fantasy"])
#     )
#     assert query.to_dict() == {
#         "_or": [
#             {
#                 "_and": [
#                     {"title": {"_contains": "Robots"}},
#                     {"rating": {"_gte": 3}}
#                 ]
#             },
#             {"genres": {"_in": ["Scifi", "Fantasy"]}}
#         ]
#     }
#     assert query.explain() == (
#         "SELECT title, rating, genres\n"
#         "FROM books\n"
#         "WHERE (title LIKE '%Robots%' AND rating >= 3) OR genres IN ('Scifi', 'Fantasy')"
#     )

# def test_multiple_and_conditions(collection):
#     query = collection.select(["title", "genres"]).filter("title").contains("Robots").and_(
#         collection.filter("rating").gte(3),
#         collection.filter("genres").in_(["Scifi", "Fantasy"])
#     )
#     assert query.to_dict() == {
#         "_and": [
#             {"title": {"_contains": "Robots"}},
#             {"rating": {"_gte": 3}},
#             {"genres": {"_in": ["Scifi", "Fantasy"]}}
#         ]
#     }
#     assert query.explain() == (
#         "SELECT title, genres\n"
#         "FROM books\n"
#         "WHERE title LIKE '%Robots%' AND rating >= 3 AND genres IN ('Scifi', 'Fantasy')"
#     )

# def test_empty_filter(collection):
#     query = collection.select(["title"]).filter("title")
#     assert query.to_dict() == {}
#     assert query.explain() == (
#         "SELECT title\n"
#         "FROM books\n"
#         "WHERE "
#     )

# def test_multiple_filters_on_same_field_with_different_operators(collection):
#     query = collection.select(["price"]).filter("price").gte(10).and_(
#         collection.filter("price").lt(20)
#     )
#     assert query.to_dict() == {
#         "_and": [
#             {"price": {"_gte": 10}},
#             {"price": {"_lt": 20}}
#         ]
#     }
#     assert query.explain() == (
#         "SELECT price\n"
#         "FROM books\n"
#         "WHERE price >= 10 AND price < 20"
#     )

# def test_complex_nested_conditions(collection):
#     query = collection.select(["title", "author", "year"]).filter("year").gte(2000).and_(
#         collection.filter("author").eq("John Doe").or_(
#             collection.filter("author").eq("Jane Smith")
#         )
#     ).or_(
#         collection.filter("title").contains("Python").and_(
#             collection.filter("year").lt(2020)
#         )
#     )
#     assert query.to_dict() == {
#         "_or": [
#             {
#                 "_and": [
#                     {"year": {"_gte": 2000}},
#                     {
#                         "_or": [
#                             {"author": {"_eq": "John Doe"}},
#                             {"author": {"_eq": "Jane Smith"}}
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "_and": [
#                     {"title": {"_contains": "Python"}},
#                     {"year": {"_lt": 2020}}
#                 ]
#             }
#         ]
#     }
#     assert query.explain() == (
#         "SELECT title, author, year\n"
#         "FROM books\n"
#         "WHERE (year >= 2000 AND (author = 'John Doe' OR author = 'Jane Smith')) OR (title LIKE '%Python%' AND year < 2020)"
#     )
