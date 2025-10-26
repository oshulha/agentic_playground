import re

import requests


class PlaneBase:
    def __init__(
        self,
        api_key,
        workspace="tac",
        server_url="http://the-agent-company.com:8091",
        email="agent@company.com",
        password="theagentcompany",
        ssl_verify=True,
        proxies=None,
        timeout=30,
        session=None,
        client_certs=None,
    ):
        """Creates a Plane object"""
        self.headers = {}
        self.server_url = server_url
        self.proxies = proxies
        self.ssl_verify = ssl_verify
        self.cert = client_certs
        self.timeout = timeout
        self.req = session or requests.Session()
        self.workspace = workspace
        self.email = email
        self.password = password
        self.api_path = "/api/v1/" + "workspaces/" + workspace + "/"
        if api_key:
            self.headers["X-API-Key"] = api_key
        self.login()

    def _make_url(self, endpoint: str) -> str:
        if not re.match(r"^https?://", endpoint):
            endpoint = f"{self.server_url}{self.api_path}{endpoint}"
        return endpoint

    def _request(
        self, method: str, endpoint: str, body: dict = None
    ) -> requests.Response:
        url = self._make_url(endpoint)
        return self.req.request(
            method=method,
            url=url,
            headers=self.headers,
            verify=self.ssl_verify,
            cert=self.cert,
            proxies=self.proxies,
            timeout=self.timeout,
            json=body,
        )

    def call_api_get(self, endpoint: str) -> requests.Response:
        return self._request("GET", endpoint)

    def call_api_post(self, endpoint: str, body: dict = None) -> requests.Response:
        return self._request("POST", endpoint, body)

    def call_api_put(self, endpoint: str, body: dict = None) -> requests.Response:
        return self._request("PUT", endpoint, body)

    def call_api_patch(self, endpoint: str, body: dict = None) -> requests.Response:
        return self._request("PATCH", endpoint, body)

    def call_api_delete(self, endpoint: str, body: dict = None) -> requests.Response:
        return self._request("DELETE", endpoint, body)

    def login(self):
        csrf_url = f"{self.server_url}/auth/get-csrf-token/"
        login_url = f"{self.server_url}/auth/sign-in/"
        response = self.req.get(csrf_url)
        response.raise_for_status()
        data = response.json()
        csrf_token = data.get("csrf_token")
        if not csrf_token:
            raise ValueError("CSRF token not found in Plane response!")
        payload = {
            "csrfmiddlewaretoken": csrf_token,
            "email": self.email,
            "password": self.password,
            "next_path": f"/{self.workspace}/",
        }
        headers = {"Referer": csrf_url}
        login_response = self.req.post(login_url, data=payload, headers=headers)
        login_response.raise_for_status()
