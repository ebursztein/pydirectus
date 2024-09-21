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

    def post(self, endpoint: str, data: dict) -> APIResponse:
        "POST request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        response = httpx.post(url, headers=headers, json=data)
        duration = max(int(time() - start), 1)

        return self._make_response(url, duration, response)

    def patch(self, endpoint: str, data: dict) -> APIResponse:
        "PATCH request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        response = httpx.patch(url, headers=headers, json=data)
        duration = max(int(time() - start), 1)

        return self._make_response(url, duration, response)

    def delete(self, endpoint: str, data: dict) -> APIResponse:
        "DELETE request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        # have to do custom to pass payload to the DELETE request...
        with httpx.Client() as client:
            response = client.request(method="DELETE", url=url,
                                      headers=headers, json=data)
        duration = max(int(time() - start), 1)

        return self._make_response(url, duration, response)

    def search(self, endpoint: str, data: dict) -> APIResponse:
        "Search request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()
        # Make request
        start = time()
        with httpx.Client() as client:
            response = client.request(method="SEARCH", url=url,
                                      headers=headers, json=data)
        duration = max(int(time() - start), 1)

        return self._make_response(url, duration, response)

    # files management
    def download(self, endpoint: str) -> bytes:
        "Download a file"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        response = httpx.get(url, headers=headers)

        if response.status_code != 200:
            logging.error(f"{url}: error {response.status_code}: {response.text}")
            return b''
        return response.content

    def upload(self, endpoint: str, data: dict, files: dict) -> APIResponse:
        "Upload a file"
        url = self._make_url(endpoint)
        headers = self._make_headers()
        start = time()
        response = httpx.post(url, headers=headers, data=data, files=files)
        duration = max(int(time() - start), 1)
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
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"{self.url}/{endpoint}"

    def _make_headers(self, headers: dict = {}) -> dict:
        "Add Authorization header"
        headers['Authorization'] = f"Bearer {self.token}"
        return headers

    def _make_response(self, url: str, duration: int, response: httpx.Response) -> APIResponse:
        "Build and return response"

        # https://www.restack.io/docs/directus-knowledge-directus-status-code-reference
        if response.status_code not in [200, 201, 204]:
            logging.error(f"{url}: error {response.status_code}: {response.text}")
            return APIResponse(ok=False,
                            error_message=response.text,
                            duration=duration,
                            data={})

        # this happen when 204 (e.g. delete)
        if not response.content:
            data = {}
        else:
            data = response.json()
        data = data['data'] if 'data' in data else data
        logging.debug(f"{url}: success {len(data)} objects returned in {duration}ms")
        return APIResponse(ok=True, error_message="", duration=duration,
                           data=data)
