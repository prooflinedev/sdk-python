from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx2

from ...client import AuthenticatedClient, Client
from ...models.commit_deploy_verifications import CommitDeployVerifications
from ...models.problem import Problem
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    repo_id: UUID,
    commit_sha: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/repositories/{repo_id}/commits/{commit_sha}/deploy-verifications".format(
            org_id=quote(str(org_id), safe=""),
            repo_id=quote(str(repo_id), safe=""),
            commit_sha=quote(str(commit_sha), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> CommitDeployVerifications | Problem:
    if response.status_code == 200:
        response_200 = CommitDeployVerifications.from_dict(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Response[CommitDeployVerifications | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    repo_id: UUID,
    commit_sha: str,
    *,
    client: AuthenticatedClient,
) -> Response[CommitDeployVerifications | Problem]:
    """Get a commit's deploy verifications

     Returns each deploy of one exact commit in the repository that Proofline recorded, across the
    organization's environments: its environment ID, GitHub Environment, task, workflow run and attempt,
    where its verification stands, whether a check regressed, each check's result and due time, the gaps
    that leave it unproven and its console page. `commit_sha` must be a full 40-character lowercase
    commit SHA; a branch, tag or abbreviated SHA gets 400. A commit with no recorded deploy returns
    `recorded: false` and no deploys, which is never a result about a deploy. A repository outside the
    token's repository restriction or organization returns 404.

    Args:
        org_id (UUID):
        repo_id (UUID):
        commit_sha (str): The full 40-character lowercase commit SHA the job deployed. A branch,
             tag or abbreviated SHA is refused.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommitDeployVerifications | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        commit_sha=commit_sha,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    repo_id: UUID,
    commit_sha: str,
    *,
    client: AuthenticatedClient,
) -> CommitDeployVerifications | Problem | None:
    """Get a commit's deploy verifications

     Returns each deploy of one exact commit in the repository that Proofline recorded, across the
    organization's environments: its environment ID, GitHub Environment, task, workflow run and attempt,
    where its verification stands, whether a check regressed, each check's result and due time, the gaps
    that leave it unproven and its console page. `commit_sha` must be a full 40-character lowercase
    commit SHA; a branch, tag or abbreviated SHA gets 400. A commit with no recorded deploy returns
    `recorded: false` and no deploys, which is never a result about a deploy. A repository outside the
    token's repository restriction or organization returns 404.

    Args:
        org_id (UUID):
        repo_id (UUID):
        commit_sha (str): The full 40-character lowercase commit SHA the job deployed. A branch,
             tag or abbreviated SHA is refused.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommitDeployVerifications | Problem
    """

    return sync_detailed(
        org_id=org_id,
        repo_id=repo_id,
        commit_sha=commit_sha,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repo_id: UUID,
    commit_sha: str,
    *,
    client: AuthenticatedClient,
) -> Response[CommitDeployVerifications | Problem]:
    """Get a commit's deploy verifications

     Returns each deploy of one exact commit in the repository that Proofline recorded, across the
    organization's environments: its environment ID, GitHub Environment, task, workflow run and attempt,
    where its verification stands, whether a check regressed, each check's result and due time, the gaps
    that leave it unproven and its console page. `commit_sha` must be a full 40-character lowercase
    commit SHA; a branch, tag or abbreviated SHA gets 400. A commit with no recorded deploy returns
    `recorded: false` and no deploys, which is never a result about a deploy. A repository outside the
    token's repository restriction or organization returns 404.

    Args:
        org_id (UUID):
        repo_id (UUID):
        commit_sha (str): The full 40-character lowercase commit SHA the job deployed. A branch,
             tag or abbreviated SHA is refused.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CommitDeployVerifications | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        commit_sha=commit_sha,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repo_id: UUID,
    commit_sha: str,
    *,
    client: AuthenticatedClient,
) -> CommitDeployVerifications | Problem | None:
    """Get a commit's deploy verifications

     Returns each deploy of one exact commit in the repository that Proofline recorded, across the
    organization's environments: its environment ID, GitHub Environment, task, workflow run and attempt,
    where its verification stands, whether a check regressed, each check's result and due time, the gaps
    that leave it unproven and its console page. `commit_sha` must be a full 40-character lowercase
    commit SHA; a branch, tag or abbreviated SHA gets 400. A commit with no recorded deploy returns
    `recorded: false` and no deploys, which is never a result about a deploy. A repository outside the
    token's repository restriction or organization returns 404.

    Args:
        org_id (UUID):
        repo_id (UUID):
        commit_sha (str): The full 40-character lowercase commit SHA the job deployed. A branch,
             tag or abbreviated SHA is refused.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CommitDeployVerifications | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repo_id=repo_id,
            commit_sha=commit_sha,
            client=client,
        )
    ).parsed
