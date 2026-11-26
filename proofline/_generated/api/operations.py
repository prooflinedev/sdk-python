"""Typed methods generated from the public operations without custom adapters."""

from typing import cast
from uuid import UUID

from ... import _transport
from ..client import AuthenticatedClient
from ..models.scan_request_body import ScanRequestBody
from ..models.scan_response import ScanResponse
from .default import request_scan as operation_request_scan


class Operations:
    _api: AuthenticatedClient

    def request_scan(
        self,
        org_id: UUID,
        repo_id: UUID,
        *,
        body: ScanRequestBody,
    ) -> ScanResponse:
        with _transport.operation_errors():
            response = operation_request_scan.sync_detailed(
                client=self._api,
                org_id=org_id,
                repo_id=repo_id,
                body=body,
            )
            if not (response.status_code == 200):
                raise _transport.invalid_response()
            return cast(ScanResponse, response.parsed)


class AsyncOperations:
    _api: AuthenticatedClient

    async def request_scan(
        self,
        org_id: UUID,
        repo_id: UUID,
        *,
        body: ScanRequestBody,
    ) -> ScanResponse:
        with _transport.operation_errors():
            response = await operation_request_scan.asyncio_detailed(
                client=self._api,
                org_id=org_id,
                repo_id=repo_id,
                body=body,
            )
            if not (response.status_code == 200):
                raise _transport.invalid_response()
            return cast(ScanResponse, response.parsed)
