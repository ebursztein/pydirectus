import os
from dotenv import load_dotenv
from typing import Any
import logging
from .query import Query
from .collection import Collection
from .folder import Folder
from .session import Session
from rich import print

class Directus():
    "Directus API main class - mimick Directus structure"
    def __init__(self, url: str = "", token: str = ""):
        """Create a new Directus API session

        Args:
            url: Directus base url. When not supplied look for the
            env variable URL. Defaults to "".
            token: Directus API token. When not supplied look for the env
            variable TOKEN. Defaults to "".

        Note:
            The SDK purposely do not support login/password authentication as
            it is insecure. Use the API token instead and a restricted user
            when possible.
        """
        load_dotenv()

        # Check if API key is provided
        if not token:
            token = os.getenv("TOKEN")
        if not token:
            raise ValueError("API key not provided via variable or env (API_KEY)")
        self.api_key = token

        # Check if URL is provided
        if not url:
            url = os.getenv("URL")
        if not url:
            raise ValueError("URL not provided via variable or env (URL)")
        # strip trailing slash
        url = url[:-1] if url.endswith("/") else url
        self.url = url

        # Create session and check it's healthy
        self._session = Session(url, token)
        if not self._session.ping():
            raise ValueError(f"API not reachable - check URL ({url}) and API key {token[:5]}...")

    def ping(self) -> bool:
        "Check if the API is reachable"
        duration = self._session.ping()
        if duration:
            if duration < 100:
                color = "blue"
            elif duration < 300:
                color = "green"
            elif duration < 500:
                color = "yellow"
            else:
                color = "red"
            print(f"Directus reachable - [{color}] RTT {duration} ms")
            logging.info(f"Directus reachable - RTT {duration} ms")
            return True
        print("[red]Directus not reachable")
        logging.error("Directus not reachable")
        return False

    def collection_names(self, list_system_collections=False) -> list[str]:
        "Get all collections names"
        resp = self._session.get("collections")
        names = []
        for r in resp.data:
            cname = r['meta']['collection']
            if cname.startswith("directus_") and not list_system_collections:
                continue
            names.append(cname)
        return names

    def display_collections(self):
        "Display all collections names and their meta data"
        raise NotImplementedError("This method is not implemented yet")

    def collection_exist(self, name: str) -> bool:
        "Check if a collection exists"
        return name in self.collection_names()

    def collection(self, collection: str) -> Collection:
        "Get a collection"
        return Collection(collection, self._session)

    def get_raw_endpoint(self, endpoint: str) -> Any:
        "Get the raw data from an endpoint for debugging purposes"
        return self._session.get(endpoint).data


    ## Folders
    def folder_names(self) -> list[str]:
        "Get all folders names"
        resp = self._session.get("folders")
        names = []
        for r in resp.data:
            names.append(r['name'])
        return names

    def folder_exist(self, name: str = '', uuid: str = '') -> bool:
        "Check if a folder exists by name or UUID"

        if not name and not uuid:
            raise ValueError("Either name or UUID must be provided")
        if name:
            property = 'name'
            value = name
        else:
            property = 'id'
            value = uuid

        # folder don't use endpoint so passing ''
        folder = self._get_folder_info(property=property, value=value)


        if folder:
            return True
        return False

    def folder(self, name: str = '', uuid: str = '') -> Folder:
        "Get a folder"
        if not name and not uuid:
            raise ValueError("Either name or UUID must be provided")
        if name:
            property = 'name'
            value = name
        else:
            property = 'id'
            value = uuid

        # folder don't use endpoint so passing ''
        folder_info = self._get_folder_info(property=property, value=value)

        if not folder_info:
            raise ValueError(f"Folder {name} not found")
        return Folder(name=folder_info['name'],
                      parent=folder_info['parent'],
                      id=folder_info['id'],
                      session=self._session)

    def _get_folder_info(self, property:str, value: str) -> dict:
        """Get folder info using search API
        Args:
            property (str): The property to search by (name, uuid)
            value (str): The value of the property to search for
        """
        qry = Query(endpoint='folders',
                    session=self._session)

        qry.filter(property).eq(value)
        qry.limit(1)
        resp = qry.fetch()
        if len(resp) == 0:
            return {}
        else:
            return resp[0]


    def create_root_folder(self, name: str) -> Folder:
        """Create a root folder - Use Folder().create_subfolder for creating subfolders"""
        folder = {"name": name}
        resp = self._session.post("folders", data=folder)
        if resp.ok:
            return Folder(name=resp.data['name'],
                      parent=resp.data['parent'],
                      id=resp.data['id'],
                      session=self._session)
        else:
            logging.error(f"Failed to create folder {name}: {resp.error_message}")
            return None

    # translations
    def display_translations(self, limit: int = 10):
        "Display the translation"
        translations = self._session.get("translations")
        print(translations.data)