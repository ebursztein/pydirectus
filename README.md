# pydirectus: Python SDK for Directus


## Higlights

### Full ORM support for database query

`Pydirectus` allows you to quickly build search query in a pythonic ORM way.
The ORM supporting editors autocompletion and advanced typing.

```python
qry = clt.query(['title', 'url'])
qry.filter("title").contains("obot")
qry.sort("title", "asc").limit(2)
res = qry.fetch()
```

### Query explainer and debuger

The `Query.explain()` methods allows you to visualize the query sent to directus in Directus language, SQL and English for quickly debugging and understanding your query.

```pythons
qry.explain()
```
![pydirectus explainer in action](https://raw.githubusercontent.com/ebursztein/pydirectus/refs/heads/main/medias/pydirectus_explainer.jpg)


### Typechecking

Prior to inserting or updating an item pydirectus check the fields exist and
if the type of the data passed is correct to help you insert data.

## Operations Supported

Here are the [Directus API](https://docs.directus.io/reference/)
operations currently supported. Pull requests welcomes.

| object     | list | exist | get | search | insert | update | delete |
|:-----------|------|-------|-----|--------|--------|--------|--------|
| collection | ✔    | ✔     | ✔   | -      | -      | -      | -      |
| items      | ✔    | ✔     | ✔   | ✔      | ✔      | ✔      | ✔      |
| folder     | ✔    | ✔     | ✔   | -      | ✔      | -      | -      |
| file       | ✔    | ✔     | ✔   | -      | ✔      | ✔      | ✔      |
| settings   | -    | -     | -   | -      | -      | -      | -      |


**notes**: `create`, `update`, `delete` support both single and bulk items transparently whereever possible based of if you are passing a `dict` (single items) or a `list[dict]` multiples items.

## Installation

pydirectus is installed like any other packages as

```python
pip install pydirectus-sdk
```

For dev setup see the bottom of the README.md


## Usage

### Connection

The simple way to configure the connection is to use
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
clt = dr.collection('books')
```

#### fields
You can access the fields of the collection as follow

```python
clt.display_fields()  # dislay the fields
clt.get_fields_names()  # return the list of fields names
clt.get_field() # return a Field() object
clt.field_exist()  # retrun if exist
```

### Items
#### Search

pydirectus have a WIP mini ORM that allows you to construct your search query
interactively with autocompletion.
**note**: There are some case that are still buggy but basic usage works

```python
clt = dr.collection('books')
qry = clt.query(['id', 'title', 'count'])
qry.filter("title").contains("obot")
qry.sort("id", "asc").limit(10)
# qry.explain()
items = qry.fetch()
```

#### Insert

##### Single item
```python
item = {'title': 'my book'}
clt.insert(item)
```

##### Multiples items
```python
items = [{'title': 'my book'}, {'title': 'my book2', 'rating': 3}]
clt.insert(items)
```

#### Update

##### Single item
```python
item = {'title': 'my book'}
clt.update(2, item)
```

##### Multiples items
```python
ids = [3, 4]
items = [{'title': 'my book'}, {'title': 'my book2', 'rating': 3}]
clt.update(ids, items)
```

#### Delete

##### Single items

```python
idx = 1
clt.delete(idx)
```

##### Multiples items

```python
idxs = [3, 5]
clt.delete(idxs)
```


### Folders and Files

#### Get a folder

```python
fld = dr.folder(name='folder-name')
# or by id/uuid (The one in the url)
fld = dr.folder(id='folder-uuid')
```

#### List files

```python
fld = dr.folder(name)
files = fld.files()  # return the list[Files] that the folder hold
filenames = fld.filenames()  # return the list[str] of the file.filename_download
fld.display_files(limit=10)  # terminal pretty print of the existing files
```

#### Create folder

##### Root folder

Create a folder at the root of the directus instance:
```python
fld = dr.create_folder('name')
```

#### Subfolder
Create a subfolder in the specified folder:
```python
parent = dr.folder(name='parent-folder')
subfolder = parent.create_folder('sub-folder')
```


### Files

#### get fileinfo

```python
fld.fileinfo('test.webp')
```

#### exist

```python
fld.exist('test.webp')
```

#### Download a file

```python
fld.download('test.webp', 'tmp/',
              ondisk_filename='test.jpeg',
              width=200, format='jpeg')
```

Download support images operations and the ability to rename the file on disk via
`ondisk_filename`.

Note: `ondisk_filename` is required when doing image transformation as the
downloaded image is not the original one.

#### Upload
Upload is basically the same as download

```python
fld.upload('tmp/test.jpeg', title='uploaded test')
```

#### Delete

```python
fld.delete('filemane')
```




## Dev

### Setup

```bash
uv venv
source .venv/bin/activate  # and/or in vscode select the venv
uv pip install -e .
```

### Refresh
when bumping version don't forget to refresh uv

```bash
uv pip install -e .
```


### Adding test data

You can easily add more data to the test by using `utils/test_data_dumper.py` which interface with your directus instance to dump the raw responses. The tests should be able to pickup all the dumpped responses.

During testing we mock the `Session` object to respond with those dumps to ensure consistency and avoid network requests.
