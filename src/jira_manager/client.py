import json

import requests
import requests.auth

BASE_URL = "https://{domain}.atlassian.net/"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_PAGE_SIZE = 20
MAX_RETRIES = 5


class JiraClient:
    """
    Bridge class for the Jira API.
    """

    domain: str
    base_url: str

    def __init__(self, domain: str, key: str, secret: str) -> None:
        self.domain = domain
        self.base_url = BASE_URL.format(domain=domain)
        self.auth = requests.auth.HTTPBasicAuth(username=key, password=secret)

    @property
    def request_headers(self) -> dict:
        """
        Default request headers.
        """

        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
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
            auth=self.auth,
            data=json.dumps(
                {
                    "query": query,
                    "variables": {} if variables is None else variables,
                },
            ),
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
