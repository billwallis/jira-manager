import http
import types

import pytest
import requests

from jira_manager import client


@pytest.fixture
def jira_client() -> client.JiraClient:
    return client.JiraClient(
        domain="foo-bar",
        key="foo",
        secret="B4r!",
    )


def test__client__can_be_instantiated(jira_client: client.JiraClient):
    assert jira_client.domain == "foo-bar"
    assert jira_client.base_url == "https://foo-bar.atlassian.net/"
    assert jira_client.request_headers == {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def test__client__can_post_graphql_query(
    jira_client: client.JiraClient,
    monkeypatch: pytest.MonkeyPatch,
):
    query = "query getMe {me {user {... on AtlassianAccountUser {accountId}}}}"

    def mock_post(**kwargs):
        assert kwargs["url"] == "https://foo-bar.atlassian.net/gateway/api/graphql"
        assert kwargs["data"] == f'{{"query": "{query}", "variables": {{}}}}'

    monkeypatch.setattr(requests, "post", mock_post)  # type: ignore
    jira_client.graphql(query=query)


def test__client__can_search_jql(
    jira_client: client.JiraClient,
    monkeypatch: pytest.MonkeyPatch,
):
    jql = "project = X order by updated -30d"
    fields = ["key", "foo", "bar"]

    def mock_get(**kwargs):
        assert kwargs["url"] == "https://foo-bar.atlassian.net/rest/api/3/search/jql"
        assert kwargs["params"] == {
            "jql": jql,
            "maxResults": 100,
            "fields": "key,foo,bar",
            "expand": "renderedFields,names",
            "nextPageToken": None,
        }

        return types.SimpleNamespace(
            status_code=http.HTTPStatus.OK,
            json=lambda: {"issues": [], "isLast": True},
        )

    monkeypatch.setattr(requests, "get", mock_get)  # type: ignore
    jira_client.search_jql(jql=jql, fields=fields)


def test__client__can_search_jql_with_multiple_results(
    jira_client: client.JiraClient,
    monkeypatch: pytest.MonkeyPatch,
):
    search_results = {
        None: types.SimpleNamespace(
            status_code=http.HTTPStatus.OK,
            json=lambda: {
                "issues": ["X-1", "X-2", "X-3"],
                "isLast": False,
                "nextPageToken": "Cx-page1",
            },
        ),
        "Cx-page1": types.SimpleNamespace(
            status_code=http.HTTPStatus.OK,
            json=lambda: {
                "issues": ["X-4", "X-5", "X-6"],
                "isLast": False,
                "nextPageToken": "Cx-page2",
            },
        ),
        "Cx-page2": types.SimpleNamespace(
            status_code=http.HTTPStatus.OK,
            json=lambda: {
                "issues": ["X-7", "X-8"],
                "isLast": True,
            },
        ),
    }

    def mock_get(**kwargs):
        return search_results[kwargs["params"].get("nextPageToken")]

    monkeypatch.setattr(requests, "get", mock_get)  # type: ignore
    results = jira_client.search_jql(jql="project = X", fields=[])
    assert results == ["X-1", "X-2", "X-3", "X-4", "X-5", "X-6", "X-7", "X-8"]


def test__client__search_jql_raises_runtime_error_without_200(
    jira_client: client.JiraClient,
    monkeypatch: pytest.MonkeyPatch,
):
    def mock_get(**kwargs):
        return types.SimpleNamespace(
            status_code=http.HTTPStatus.BAD_REQUEST,
            text="oh no!",
        )

    monkeypatch.setattr(requests, "get", mock_get)  # type: ignore
    with pytest.raises(RuntimeError):
        jira_client.search_jql(jql="project = X", fields=[])


def test__client__search_jql_json_error_exits_early(
    jira_client: client.JiraClient,
    monkeypatch: pytest.MonkeyPatch,
):
    def raise_json_decode_error():
        raise requests.JSONDecodeError("", "", 0)

    def mock_get(**kwargs):
        return types.SimpleNamespace(
            status_code=http.HTTPStatus.OK,
            json=lambda: raise_json_decode_error(),
        )

    monkeypatch.setattr(requests, "get", mock_get)  # type: ignore
    results = jira_client.search_jql(jql="project = X", fields=[])
    assert results == []


def test__client__search_jql_missing_keys_raises_value_error(
    jira_client: client.JiraClient,
    monkeypatch: pytest.MonkeyPatch,
):
    def mock_get(**kwargs):
        return types.SimpleNamespace(
            status_code=http.HTTPStatus.OK,
            # no `isLast` flag
            json=lambda: {"issues": ["X-1", "X-2", "X-3"]},
        )

    monkeypatch.setattr(requests, "get", mock_get)  # type: ignore
    with pytest.raises(ValueError):
        jira_client.search_jql(jql="project = X", fields=[])
