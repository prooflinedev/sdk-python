from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ...client import AuthenticatedClient, Client
from ...models.problem import Problem
from ...models.review_page import ReviewPage
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: UUID,
    repository_path: str,
    pull_request_number: int,
    *,
    attention: None | str | Unset = UNSET,
    author: None | str | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    environment: None | Unset | UUID = UNSET,
    findings: None | str | Unset = UNSET,
    kind: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
    repository_query: None | Unset | UUID = UNSET,
    search: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_attention: None | str | Unset
    if isinstance(attention, Unset):
        json_attention = UNSET
    else:
        json_attention = attention
    params["attention"] = json_attention

    json_author: None | str | Unset
    if isinstance(author, Unset):
        json_author = UNSET
    else:
        json_author = author
    params["author"] = json_author

    json_cursor: None | str | Unset
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

    json_environment: None | str | Unset
    if isinstance(environment, Unset):
        json_environment = UNSET
    elif isinstance(environment, UUID):
        json_environment = str(environment)
    else:
        json_environment = environment
    params["environment"] = json_environment

    json_findings: None | str | Unset
    if isinstance(findings, Unset):
        json_findings = UNSET
    else:
        json_findings = findings
    params["findings"] = json_findings

    json_kind: None | str | Unset
    if isinstance(kind, Unset):
        json_kind = UNSET
    else:
        json_kind = kind
    params["kind"] = json_kind

    json_limit: int | None | Unset
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    json_query: None | str | Unset
    if isinstance(query, Unset):
        json_query = UNSET
    else:
        json_query = query
    params["query"] = json_query

    json_repository_query: None | str | Unset
    if isinstance(repository_query, Unset):
        json_repository_query = UNSET
    elif isinstance(repository_query, UUID):
        json_repository_query = str(repository_query)
    else:
        json_repository_query = repository_query
    params["repository"] = json_repository_query

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/organizations/{org_id}/reviews/pr/{repository_path}/{pull_request_number}".format(
            org_id=quote(str(org_id), safe=""),
            repository_path=quote(str(repository_path), safe=""),
            pull_request_number=quote(str(pull_request_number), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Problem | ReviewPage:
    if response.status_code == 200:
        response_200 = ReviewPage.from_dict(response.json())

        return response_200

    response_default = Problem.from_dict(response.json())

    return response_default


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Problem | ReviewPage]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: UUID,
    repository_path: str,
    pull_request_number: int,
    *,
    client: AuthenticatedClient,
    attention: None | str | Unset = UNSET,
    author: None | str | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    environment: None | Unset | UUID = UNSET,
    findings: None | str | Unset = UNSET,
    kind: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
    repository_query: None | Unset | UUID = UNSET,
    search: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> Response[Problem | ReviewPage]:
    """List a pull request's review runs

     Lists the review runs of one pull request, addressed by repository name and pull request number.

    Args:
        org_id (UUID):
        repository_path (str):
        pull_request_number (int):
        attention (None | str | Unset): `needed` lists terminal reviews of open pull requests with
            active
             findings, FAILED/INCOMPLETE/STOPPED execution, or an earlier reviewed commit.
        author (None | str | Unset):
        cursor (None | str | Unset):
        environment (None | Unset | UUID):
        findings (None | str | Unset):
        kind (None | str | Unset):
        limit (int | None | Unset):
        query (None | str | Unset): Qualifiers, quoted values, AND/OR, groups and minus
            exclusions.
        repository_query (None | Unset | UUID):
        search (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | ReviewPage]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repository_path=repository_path,
        pull_request_number=pull_request_number,
        attention=attention,
        author=author,
        cursor=cursor,
        environment=environment,
        findings=findings,
        kind=kind,
        limit=limit,
        query=query,
        repository_query=repository_query,
        search=search,
        status=status,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: UUID,
    repository_path: str,
    pull_request_number: int,
    *,
    client: AuthenticatedClient,
    attention: None | str | Unset = UNSET,
    author: None | str | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    environment: None | Unset | UUID = UNSET,
    findings: None | str | Unset = UNSET,
    kind: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
    repository_query: None | Unset | UUID = UNSET,
    search: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> Problem | ReviewPage | None:
    """List a pull request's review runs

     Lists the review runs of one pull request, addressed by repository name and pull request number.

    Args:
        org_id (UUID):
        repository_path (str):
        pull_request_number (int):
        attention (None | str | Unset): `needed` lists terminal reviews of open pull requests with
            active
             findings, FAILED/INCOMPLETE/STOPPED execution, or an earlier reviewed commit.
        author (None | str | Unset):
        cursor (None | str | Unset):
        environment (None | Unset | UUID):
        findings (None | str | Unset):
        kind (None | str | Unset):
        limit (int | None | Unset):
        query (None | str | Unset): Qualifiers, quoted values, AND/OR, groups and minus
            exclusions.
        repository_query (None | Unset | UUID):
        search (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | ReviewPage
    """

    return sync_detailed(
        org_id=org_id,
        repository_path=repository_path,
        pull_request_number=pull_request_number,
        client=client,
        attention=attention,
        author=author,
        cursor=cursor,
        environment=environment,
        findings=findings,
        kind=kind,
        limit=limit,
        query=query,
        repository_query=repository_query,
        search=search,
        status=status,
    ).parsed


async def asyncio_detailed(
    org_id: UUID,
    repository_path: str,
    pull_request_number: int,
    *,
    client: AuthenticatedClient,
    attention: None | str | Unset = UNSET,
    author: None | str | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    environment: None | Unset | UUID = UNSET,
    findings: None | str | Unset = UNSET,
    kind: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
    repository_query: None | Unset | UUID = UNSET,
    search: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> Response[Problem | ReviewPage]:
    """List a pull request's review runs

     Lists the review runs of one pull request, addressed by repository name and pull request number.

    Args:
        org_id (UUID):
        repository_path (str):
        pull_request_number (int):
        attention (None | str | Unset): `needed` lists terminal reviews of open pull requests with
            active
             findings, FAILED/INCOMPLETE/STOPPED execution, or an earlier reviewed commit.
        author (None | str | Unset):
        cursor (None | str | Unset):
        environment (None | Unset | UUID):
        findings (None | str | Unset):
        kind (None | str | Unset):
        limit (int | None | Unset):
        query (None | str | Unset): Qualifiers, quoted values, AND/OR, groups and minus
            exclusions.
        repository_query (None | Unset | UUID):
        search (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Problem | ReviewPage]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        repository_path=repository_path,
        pull_request_number=pull_request_number,
        attention=attention,
        author=author,
        cursor=cursor,
        environment=environment,
        findings=findings,
        kind=kind,
        limit=limit,
        query=query,
        repository_query=repository_query,
        search=search,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: UUID,
    repository_path: str,
    pull_request_number: int,
    *,
    client: AuthenticatedClient,
    attention: None | str | Unset = UNSET,
    author: None | str | Unset = UNSET,
    cursor: None | str | Unset = UNSET,
    environment: None | Unset | UUID = UNSET,
    findings: None | str | Unset = UNSET,
    kind: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
    repository_query: None | Unset | UUID = UNSET,
    search: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
) -> Problem | ReviewPage | None:
    """List a pull request's review runs

     Lists the review runs of one pull request, addressed by repository name and pull request number.

    Args:
        org_id (UUID):
        repository_path (str):
        pull_request_number (int):
        attention (None | str | Unset): `needed` lists terminal reviews of open pull requests with
            active
             findings, FAILED/INCOMPLETE/STOPPED execution, or an earlier reviewed commit.
        author (None | str | Unset):
        cursor (None | str | Unset):
        environment (None | Unset | UUID):
        findings (None | str | Unset):
        kind (None | str | Unset):
        limit (int | None | Unset):
        query (None | str | Unset): Qualifiers, quoted values, AND/OR, groups and minus
            exclusions.
        repository_query (None | Unset | UUID):
        search (None | str | Unset):
        status (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Problem | ReviewPage
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            repository_path=repository_path,
            pull_request_number=pull_request_number,
            client=client,
            attention=attention,
            author=author,
            cursor=cursor,
            environment=environment,
            findings=findings,
            kind=kind,
            limit=limit,
            query=query,
            repository_query=repository_query,
            search=search,
            status=status,
        )
    ).parsed
