import http
import json

import requests
import requests.auth

BASE_URL = "https://{domain}.atlassian.net/"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_PAGE_SIZE = 100
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

    def search_jql(self, jql: str, fields: list[str]) -> list[dict]:
        """
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-jql-get
        """
        endpoint = "rest/api/3/search/jql"
        query = {
            "jql": jql,
            "maxResults": DEFAULT_PAGE_SIZE,
            "fields": ",".join(fields),
            "expand": "renderedFields,names",
            "nextPageToken": None,
        }
        search_results, is_last = [], False
        while not is_last:
            response = requests.get(
                url=self.base_url + endpoint,
                headers=self.request_headers,
                auth=self.auth,
                params=query,
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )
            if response.status_code != http.HTTPStatus.OK:
                raise RuntimeError(response.text)

            try:
                response_json = response.json()
            except requests.JSONDecodeError:
                # TODO: Do more stuff here
                return search_results

            required_keys = ["issues", "isLast"]
            for key in required_keys:
                if key not in response_json:
                    raise ValueError(f"response missing required key '{key}'")

            search_results.extend(response_json["issues"])
            is_last = response_json["isLast"]
            query["nextPageToken"] = response_json.get("nextPageToken")

        return search_results
