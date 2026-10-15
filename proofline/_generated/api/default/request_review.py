from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.problem import Problem
from ...models.run_now_refused import RunNowRefused
from ...models.run_now_request import RunNowRequest
from ...models.run_now_response import RunNowResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: UUID,
    repo_id: UUID,
    number: int,
    *,
    body: RunNowRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/organizations/{org_id}/repositories/{repo_id}/pull-requests/{number}/review".format(
            org_id=quote(str(org_id), safe=""),
            repo_id=quote(str(repo_id), safe=""),
            number=quote(str(number), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    if not isinstance(body, Unset):
        headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Problem | RunNowRefused | RunNowResponse:
    if response.status_code == 200:
        response_200 = RunNowResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = RunNowRefused.from_dict(response.json())

        return response_400

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Problem | RunNowRefused | RunNowResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    repo_id: UUID,
    number: int,
    *,
    client: AuthenticatedClient,
    body: RunNowRequest | Unset = UNSET,
) -> Response[Problem | RunNowRefused | RunNowResponse]:
    """Request a pull request review

     Returns the active or result-bearing review at the pull request's live head, or creates a withheld
    one. The `FULL` mode creates a new review of the whole change unless one is pending or running.
    Requires live GitHub write access; a repeated request can create another review, so clients make one
    attempt.

    Args:
        org_id (UUID):
        repo_id (UUID):
        number (int):
        body (RunNowRequest | Unset): An empty body keeps the run-now behavior existing clients
            request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | RunNowRefused | RunNowResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        number=number,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    repo_id: UUID,
    number: int,
    *,
    client: AuthenticatedClient,
    body: RunNowRequest | Unset = UNSET,
) -> Problem | RunNowRefused | RunNowResponse | None:
    """Request a pull request review

     Returns the active or result-bearing review at the pull request's live head, or creates a withheld
    one. The `FULL` mode creates a new review of the whole change unless one is pending or running.
    Requires live GitHub write access; a repeated request can create another review, so clients make one
    attempt.

    Args:
        org_id (UUID):
        repo_id (UUID):
        number (int):
        body (RunNowRequest | Unset): An empty body keeps the run-now behavior existing clients
            request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | RunNowRefused | RunNowResponse
    """

    return sync_detailed(
        org_id=org_id,
        repo_id=repo_id,
        number=number,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repo_id: UUID,
    number: int,
    *,
    client: AuthenticatedClient,
    body: RunNowRequest | Unset = UNSET,
) -> Response[Problem | RunNowRefused | RunNowResponse]:
    """Request a pull request review

     Returns the active or result-bearing review at the pull request's live head, or creates a withheld
    one. The `FULL` mode creates a new review of the whole change unless one is pending or running.
    Requires live GitHub write access; a repeated request can create another review, so clients make one
    attempt.

    Args:
        org_id (UUID):
        repo_id (UUID):
        number (int):
        body (RunNowRequest | Unset): An empty body keeps the run-now behavior existing clients
            request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | RunNowRefused | RunNowResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repo_id=repo_id,
        number=number,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repo_id: UUID,
    number: int,
    *,
    client: AuthenticatedClient,
    body: RunNowRequest | Unset = UNSET,
) -> Problem | RunNowRefused | RunNowResponse | None:
    """Request a pull request review

     Returns the active or result-bearing review at the pull request's live head, or creates a withheld
    one. The `FULL` mode creates a new review of the whole change unless one is pending or running.
    Requires live GitHub write access; a repeated request can create another review, so clients make one
    attempt.

    Args:
        org_id (UUID):
        repo_id (UUID):
        number (int):
        body (RunNowRequest | Unset): An empty body keeps the run-now behavior existing clients
            request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | RunNowRefused | RunNowResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repo_id=repo_id,
            number=number,
            client=client,
            body=body,
        )
    ).parsed
