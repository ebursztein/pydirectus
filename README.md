# pydirectus
Python SDK for Directus


## Operations Supported

Here are the [Directus API](https://docs.directus.io/reference/)
operations currently supported. Pull requests welcomes.


| object     | list | get | search | write | update | delete |
|:-----------|------|-----|--------|-------|--------|--------|
| collection | ✔    | -   | -      | -     | -      | -      |
| item       | -    | -   | -      | -     | -      | -      |
| field      | ✔    | -   | -      | -     | -      | -      |
| file       | -    | -   | -      | -     | -      | -      |
| settings   | -    | -   | -      | -     | -      | -      |


## Usage

### Setup

The simple way to configure the package is to use
env variables:
-  **URL**: your base url - e.g `https://localhost:8055/`
-  **TOKEN**: your user token - we encourage you to NOT use
the admin users but a least privilege user with only the permission you need.

You can put the variables in the env directly (e.g Docker) or
in `.env` and the code shoudl pick-it up.  if you don't want
to use env variables then you can pass the url and token to the
`Directus()` object directly. We don't support login/pass authentication for security reasons.

Then you can test all is working as intended as:

```python
from pydirectus import Directus
dr = Directus()  # with ENV vars or .env
# dr = Directus(url="your_base__url", token="your_token")  # if you want to explictly pass them
dr.session.ping()  # check we can connect to directus
```

### Colllections
To manage a collection get an instanciated `Collection` object:

```python
from pydirectus import Directus
dr = Directus()  # with ENV vars or .env
c = dr.collection('books')s
```

#### fields
You can access the fields of the collection as follow

```python
c.display_fields()  # dislay the fields
c.get_fields_names()  # return the list of fields names
c.get_field() # return a Field() object
c.field_exist()  # retrun if exist
```

## Testing


### Adding test data

You can easily add more data to the test by using `utils/test_data_dumper.py` which interface with your directus instance to dump the raw responses. The tests should be able to pickup all the dumpped responses.

During testing we mock the `Session` object to respond with those dumps to ensure consistency and avoid network requests.



## TODO
- Settings: https://github.com/panos-stavrianos/py-directus/blob/master/py_directus/directus.py
- settings / translation / files
