import logging
from time import time
import httpx
from dataclasses import dataclass

@dataclass
class APIResponse:
    "response object"
    ok: bool
    error_message: str
    duration: int
    data: dict

class Session():
    "handle lowlevel requests to the Directus API"
    def __init__(self, url: str, token: str) -> None:

        if not url:
            raise ValueError("URL not provided")
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("URL must start with http(s)://")
        if not token:
            raise ValueError("API key not provided")

        self.url = url
        self.token = token

    def get(self, endpoint: str) -> APIResponse:
        "GET request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        response = httpx.get(url, headers=headers)
        duration = max(int(time() - start), 1) # avoid 0ms response

        # parse response and returns it
        return self._make_response(url, duration, response)

    def ping(self) -> int:
        "Check if the API is reachable"
        path = "server/health"
        url = self._make_url(path)
        headers = self._make_headers()

        start = time()
        try:
            response = httpx.get(url, headers=headers)
        except httpx.RequestError as e:
            logging.error(f"Server error:{url}:{e}")
            return 0

        duration = max(int(time() - start), 1) # avoid 0ms response

        if response.status_code != 200:
            logging.error(f"Server error:{url}:{response.status_code}: {response.text}")
            return 0

        logging.info(f"Server up {duration}ms")
        return duration

    def _make_url(self, endpoint: str) -> str:
        "Build URL"
        return f"{self.url}/{endpoint}"

    def _make_headers(self, headers: dict = {}) -> dict:
        "Add Authorization header"
        headers['Authorization'] = f"Bearer {self.token}"
        return headers

    def _make_response(self, url: str, duration: int, response: httpx.Response) -> APIResponse:
        "Build and return response"

        if response.status_code != 200:
            logging.error(f"{url}: error {response.status_code}: {response.text}")
            return APIResponse(ok=False,
                            error_message=response.text,
                            duration=duration,
                        data={})

        data = response.json()
        data = data['data'] if 'data' in data else data
        logging.debug(f"{url}: success {len(data)} objects returned in {duration}ms")
        return APIResponse(ok=True, error_message="", duration=duration,
                           data=data)
