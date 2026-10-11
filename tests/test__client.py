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

    monkeypatch.setattr(requests, "post", mock_post)
    jira_client.graphql(query=query)
