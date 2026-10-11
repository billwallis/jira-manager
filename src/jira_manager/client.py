import base64
import json

import requests

BASE_URL = "https://{domain}.atlassian.net/"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_PAGE_SIZE = 20
MAX_RETRIES = 5


class JiraClient:
    """
    Bridge class for the Jira API.
    """

    base_url: str

    def __init__(self, domain: str, key: str, secret: str) -> None:
        self.base_url = BASE_URL.format(domain=domain)

        # https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/#supply-basic-auth-headers
        self._auth = (
            "Basic " + base64.b64encode(f"{key}:{secret}".encode()).decode()
        )

    @property
    def request_headers(self) -> dict:
        """
        Default request headers.
        """

        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self._auth,
        }

    def graphql(
        self,
        query: str,
        variables: dict | None = None,
    ) -> requests.Response:
        """
        https://developer.atlassian.com/platform/atlassian-graphql-api/graphql/#overview
        """

        endpoint = "gateway/api/graphql"
        return requests.post(
            url=self.base_url + endpoint,
            headers=self.request_headers,
            data=json.dumps(
                {
                    "query": query,
                    "variables": {} if variables is None else variables,
                },
            ),
        )
