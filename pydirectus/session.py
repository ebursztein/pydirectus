import logging
from time import time
import httpx
from httpx import HTTPError
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class APIResponse:
    "response object"
    ok: bool
    error_message: str
    duration: int
    data: dict

class Session():
    "handle lowlevel requests to the Directus API"
    def __init__(self, url: str, token: str, timeout: float = 20.0) -> None:

        if not url:
            raise ValueError("URL not provided")
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("URL must start with http(s)://")
        if not token:
            raise ValueError("API key not provided")

        self.url = url
        self.token = token
        self.client = httpx.Client(timeout=timeout)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get(self, endpoint: str) -> APIResponse:
        "GET request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        response = self.client.get(url, headers=headers)
        duration = self._duration(start)

        # retry logic
        if not response.is_success:
            logging.warning(f'request to {url} timed out - retrying 3 times')
            raise HTTPError(f"{response.status_code} {response.text}")

        # parse response and returns it
        return self._make_response(url, duration, response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def post(self, endpoint: str, data: dict) -> APIResponse:
        "POST request"
        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        response = self.client.post(url, headers=headers, json=data)
        duration = self._duration(start)

        # retry logic
        if not response.is_success:
            logging.warning(f'request to {url} timed out - retrying 3 times')
            raise HTTPError(f"{response.status_code} {response.text}")

        return self._make_response(url, duration, response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def patch(self, endpoint: str, data: dict) -> APIResponse:
        "PATCH request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        response = self.client.patch(url, headers=headers, json=data)
        duration = self._duration(start)

        # retry logic
        if not response.is_success:
            logging.warning(f'request to {url} timed out - retrying 3 times')
            raise HTTPError(f"{response.status_code} {response.text}")

        return self._make_response(url, duration, response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def delete(self, endpoint: str, data: dict) -> APIResponse:
        "DELETE request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        start = time()
        # have to do custom to pass payload to the DELETE request...
        response = self.client.request(method="DELETE", url=url,
                                       headers=headers, json=data)
        duration = self._duration(start)

        # retry logic
        if not response.is_success:
            logging.warning(f'request to {url} timed out - retrying 3 times')
            raise HTTPError(f"{response.status_code} {response.text}")

        return self._make_response(url, duration, response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def search(self, endpoint: str, data: dict) -> APIResponse:
        "Search request"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()
        # Make request
        start = time()
        response = self.client.request(method="SEARCH", url=url,
                                       headers=headers, json=data)
        duration = self._duration(start)

        # retry logic
        if not response.is_success:
            logging.warning(f'request to {url} timed out - retrying 3 times')
            raise HTTPError(f"{response.status_code} {response.text}")

        return self._make_response(url, duration, response)

    # files management
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def download(self, endpoint: str) -> bytes:
        "Download a file"

        # build URL and headers
        url = self._make_url(endpoint)
        headers = self._make_headers()

        # Make request
        response = self.client.get(url, headers=headers)

        # retry logic
        if not response.is_success:
            logging.warning(f'request to {url} timed out - retrying 3 times')
            raise HTTPError(f"{response.status_code} {response.text}")

        if response.status_code != 200:
            logging.error(f"{url}: error {response.status_code}: {response.text}")
            return b''
        return response.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def upload(self, endpoint: str, data: dict, files: dict) -> APIResponse:
        "Upload a file"
        url = self._make_url(endpoint)
        headers = self._make_headers()
        start = time()
        response = httpx.post(url, headers=headers, data=data, files=files)
        duration = self._duration(start)

        # retry logic
        if not response.is_success:
            logging.warning(f'request to {url} timed out - retrying 3 times')
            raise HTTPError(f"{response.status_code} {response.text}")

        return self._make_response(url, duration, response)



    def ping(self) -> int:
        "Check if the API is reachable"
        path = "server/ping"
        url = self._make_url(path)
        headers = self._make_headers()

        start = time()
        try:
            response = httpx.get(url, headers=headers)
        except httpx.RequestError as e:
            logging.error(f"Server error:{url}:{e}")
            return 0
        duration = self._duration(start)

        if response.status_code != 200:
            logging.error(f"Server error:{url}:{response.status_code}: {response.text}")
            return 0

        logging.info(f"Server up {duration}ms")
        return duration

    def _duration(self, start: float) -> int:
        "Calculate duration in ms"
        return max(int((time() - start) * 1000), 1)


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
