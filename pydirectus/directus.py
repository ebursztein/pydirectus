import os
from dotenv import load_dotenv
from typing import Any

from .collection import Collection
from .session import Session

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

    def collection_exist(self, name: str) -> bool:
        "Check if a collection exists"
        return name in self.collection_names()

    def collection(self, collection: str) -> Collection:
        "Get a collection"
        return Collection(collection, self._session)

    def get_raw_endpoint(self, endpoint: str) -> Any:
        "Get the raw data from an endpoint for debugging purposes"
        return self._session.get(endpoint).data