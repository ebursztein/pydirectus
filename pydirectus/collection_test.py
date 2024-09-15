from .test_fixtures import load_directus_raw_response, get_available_test_data, mock_session
from .collection import Collection

def test_collection_initalization(mock_session):
    collections_names = get_available_test_data('collections')

    for name in collections_names:
        collection_json = load_directus_raw_response('collections', name)
        fields_json = load_directus_raw_response('fields', name)

        instance = Collection(name, mock_session)
        assert instance.name == name
        assert instance._session == mock_session

        # check metadata
        assert instance.icon == collection_json['meta']['icon']
        assert instance.display_template == collection_json['meta']['display_template']
        assert instance.hidden == collection_json['meta']['hidden']
        assert instance.singleton == collection_json['meta']['singleton']
        assert instance.versioning == collection_json['meta']['versioning']

        # check fields
        assert len(instance.fields) == len(fields_json)
        for field in fields_json:
            name = field['field']
            fld = instance.get_field(name)
            assert fld
            assert fld.name == name
            assert fld.type == field['type']

def test_collection_get_field(mock_session):
    collections_names = get_available_test_data('collections')
    for name in collections_names:
        instance = Collection(name, mock_session)
        fields_json = load_directus_raw_response('fields', name)

        for f in fields_json:
            field = instance.get_field(f['field'])
            assert field
            assert field.name == f['field']

def test_collection_get_field_not_found(mock_session):
    collections_names = get_available_test_data('collections')
    for name in collections_names:
        instance = Collection(name, mock_session)
        field = instance.get_field('not_found')
        assert field is None

def test_collection_field_exists(mock_session):
    collections_names = get_available_test_data('collections')
    for name in collections_names:
        instance = Collection(name, mock_session)
        fields_json = load_directus_raw_response('fields', name)
        for f in fields_json:
            assert instance.field_exists(f['field'])

def test_collection_field_not_exists(mock_session):
    collections_names = get_available_test_data('collections')
    for name in collections_names:
        instance = Collection(name, mock_session)
        assert not instance.field_exists('not_found')

def test_collection_field_names(mock_session):
    collections_names = get_available_test_data('collections')
    for name in collections_names:
        instance = Collection(name, mock_session)
        fields_json = load_directus_raw_response('fields', name)
        json_field_names = {}
        for f in fields_json:
            json_field_names[f['field']] = f['type']
        field_names = instance.field_names()
        for n in field_names:
            assert n in json_field_names

def test_collection_display_fields(mock_session):
    collections_names = get_available_test_data('collections')
    for name in collections_names:
        instance = Collection(name, mock_session)
        instance.display_fields()


