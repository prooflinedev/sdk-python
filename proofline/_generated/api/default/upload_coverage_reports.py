from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.coverage_refused import CoverageRefused
from ...models.coverage_upload_request import CoverageUploadRequest
from ...models.coverage_upload_response import CoverageUploadResponse
from ...models.problem import Problem
from ...types import Response


def _get_kwargs(
    org_id: UUID,
    repo_id: UUID,
    *,
    body: CoverageUploadRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/organizations/{org_id}/repositories/{repo_id}/coverage-reports".format(
            org_id=quote(str(org_id), safe=""),
            repo_id=quote(str(repo_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CoverageRefused | CoverageUploadResponse | Problem:
    if response.status_code == 200:
        response_200 = CoverageUploadResponse.from_dict(response.json())

        return response_200

    if response.status_code == 201:
        response_201 = CoverageUploadResponse.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = CoverageRefused.from_dict(response.json())

        return response_422

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CoverageRefused | CoverageUploadResponse | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CoverageUploadRequest,
) -> Response[CoverageRefused | CoverageUploadResponse | Problem]:
    """Upload coverage reports

     Records the LCOV, Cobertura, JaCoCo or Go coverage reports a CI run produced for one exact commit
    GitHub has in the repository, for COVERAGE checks that accept uploads. A branch, tag or abbreviated
    SHA, or a report that cannot be read, gets 422 and stores nothing. Requires a repository-restricted
    token and live GitHub write access; the same reports for the same commit return the report already
    recorded.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CoverageUploadRequest): The coverage reports a CI run produced for one commit.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CoverageRefused | CoverageUploadResponse | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CoverageUploadRequest,
) -> CoverageRefused | CoverageUploadResponse | Problem | None:
    """Upload coverage reports

     Records the LCOV, Cobertura, JaCoCo or Go coverage reports a CI run produced for one exact commit
    GitHub has in the repository, for COVERAGE checks that accept uploads. A branch, tag or abbreviated
    SHA, or a report that cannot be read, gets 422 and stores nothing. Requires a repository-restricted
    token and live GitHub write access; the same reports for the same commit return the report already
    recorded.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CoverageUploadRequest): The coverage reports a CI run produced for one commit.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CoverageRefused | CoverageUploadResponse | Problem
    """

    return sync_detailed(
        org_id=org_id,
        repo_id=repo_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CoverageUploadRequest,
) -> Response[CoverageRefused | CoverageUploadResponse | Problem]:
    """Upload coverage reports

     Records the LCOV, Cobertura, JaCoCo or Go coverage reports a CI run produced for one exact commit
    GitHub has in the repository, for COVERAGE checks that accept uploads. A branch, tag or abbreviated
    SHA, or a report that cannot be read, gets 422 and stores nothing. Requires a repository-restricted
    token and live GitHub write access; the same reports for the same commit return the report already
    recorded.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CoverageUploadRequest): The coverage reports a CI run produced for one commit.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CoverageRefused | CoverageUploadResponse | Problem]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repo_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CoverageUploadRequest,
) -> CoverageRefused | CoverageUploadResponse | Problem | None:
    """Upload coverage reports

     Records the LCOV, Cobertura, JaCoCo or Go coverage reports a CI run produced for one exact commit
    GitHub has in the repository, for COVERAGE checks that accept uploads. A branch, tag or abbreviated
    SHA, or a report that cannot be read, gets 422 and stores nothing. Requires a repository-restricted
    token and live GitHub write access; the same reports for the same commit return the report already
    recorded.

    Args:
        org_id (UUID):
        repo_id (UUID):
        body (CoverageUploadRequest): The coverage reports a CI run produced for one commit.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CoverageRefused | CoverageUploadResponse | Problem
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repo_id=repo_id,
            client=client,
            body=body,
        )
    ).parsed
