"""Small sync and async facades over the generated review operations."""

from __future__ import annotations

import datetime
import math
import weakref
from asyncio import (
    Future as AsyncFuture,
)
from asyncio import (
    Task as AsyncTask,
)
from asyncio import (
    create_task as async_create_task,
)
from asyncio import (
    current_task as async_current_task,
)
from asyncio import (
    get_running_loop as async_get_running_loop,
)
from asyncio import (
    sleep as async_sleep,
)
from asyncio import (
    wait as async_wait,
)
from collections import defaultdict, deque
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from inspect import (
    CORO_CREATED,
    GEN_CREATED,
    getcoroutinestate,
    getgeneratorstate,
    isawaitable,
    iscoroutine,
    isgenerator,
)
from inspect import (
    signature as inspect_signature,
)
from string import hexdigits
from time import monotonic, sleep
from types import (
    BuiltinFunctionType,
    FunctionType,
    MemberDescriptorType,
    MethodType,
    TracebackType,
)
from typing import Any, Self, TypedDict, TypeVar, Unpack, cast
from urllib.parse import quote
from uuid import UUID

import httpx2
from pydantic import SecretStr

from . import _transport
from ._generated.api.default import (
    get_agent_session,
    get_agent_session_prompt,
    get_assessment,
    get_deployment_review,
    get_finding,
    get_finding_fix_prompt,
    get_pull_request_review,
    get_review,
    get_review_guidance,
    get_review_routing,
    list_pull_request_reviews,
    list_repositories,
    list_reviews,
    request_commit_review,
    request_file_review,
    request_patch_review,
    request_review,
    rerun_review,
    start_agent_session,
    stop_review,
    upload_coverage_reports,
)
from ._generated.api.operations import AsyncOperations, Operations
from ._generated.client import AuthenticatedClient
from ._generated.models.agent_session import AgentSession
from ._generated.models.agent_session_prompt_type_0 import AgentSessionPromptType0
from ._generated.models.agent_session_prompt_type_1 import AgentSessionPromptType1
from ._generated.models.commit_review_request import CommitReviewRequest
from ._generated.models.commit_review_response import CommitReviewResponse
from ._generated.models.coverage_upload_request import CoverageUploadRequest
from ._generated.models.coverage_upload_response import CoverageUploadResponse
from ._generated.models.customer_assessment_detail import CustomerAssessmentDetail
from ._generated.models.customer_finding import CustomerFinding
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.models.file_review_request import FileReviewRequest
from ._generated.models.file_review_response import FileReviewResponse
from ._generated.models.finding_fix_prompt_type_0 import FindingFixPromptType0
from ._generated.models.finding_fix_prompt_type_1 import FindingFixPromptType1
from ._generated.models.patch_review_request import PatchReviewRequest
from ._generated.models.patch_review_response import PatchReviewResponse
from ._generated.models.repository_guidance import RepositoryGuidance
from ._generated.models.repository_names import RepositoryNames
from ._generated.models.rerun_response import RerunResponse
from ._generated.models.review_page import ReviewPage
from ._generated.models.review_routing_view_type_0 import ReviewRoutingViewType0
from ._generated.models.review_routing_view_type_1 import ReviewRoutingViewType1
from ._generated.models.review_routing_view_type_2 import ReviewRoutingViewType2
from ._generated.models.review_summary import ReviewSummary
from ._generated.models.run_now_request import RunNowRequest
from ._generated.models.run_now_response import RunNowResponse
from ._generated.models.start_session import StartSession
from ._generated.models.stop_response import StopResponse
from ._generated.types import UNSET, Response, Unset
from ._mcp import AsyncMcpClient, McpClient
from ._transport import ProoflineError
from .exports import ExportDataset, ExportFormat, ExportPage, decode_export
from .fixes import AsyncFixesClient, FixesClient
from .knowledge import AsyncKnowledgeClient, KnowledgeClient
from .outcomes import ReviewOutcome, outcome

T = TypeVar("T")


async def _await_res(res: Awaitable[Any]) -> None:
    await res


AgentSessionPrompt = AgentSessionPromptType0 | AgentSessionPromptType1
_AgentSessionPromptModels = tuple[type[AgentSessionPromptType0], type[AgentSessionPromptType1]]
_AGENT_SESSION_PROMPT_MODELS: _AgentSessionPromptModels = (
    AgentSessionPromptType0,
    AgentSessionPromptType1,
)
FindingFixPrompt = FindingFixPromptType0 | FindingFixPromptType1
_FindingFixPromptModels = tuple[type[FindingFixPromptType0], type[FindingFixPromptType1]]
_FINDING_FIX_PROMPT_MODELS: _FindingFixPromptModels = (
    FindingFixPromptType0,
    FindingFixPromptType1,
)
ReviewRoutingView = ReviewRoutingViewType0 | ReviewRoutingViewType1 | ReviewRoutingViewType2
_ReviewRoutingModels = tuple[
    type[ReviewRoutingViewType0],
    type[ReviewRoutingViewType1],
    type[ReviewRoutingViewType2],
]
_REVIEW_ROUTING_MODELS: _ReviewRoutingModels = (
    ReviewRoutingViewType0,
    ReviewRoutingViewType1,
    ReviewRoutingViewType2,
)


class ReviewFilters(TypedDict, total=False):
    attention: str | None
    author: str | None
    cursor: str | None
    environment: UUID | None
    findings: str | None
    kind: str | None
    limit: int | None
    query: str | None
    repository: UUID | None
    search: str | None
    status: str | None


def _decoded(
    response: Response[Any],
    expected: type[T] | _ReviewRoutingModels | _FindingFixPromptModels | _AgentSessionPromptModels,
) -> T:
    if not isinstance(response.parsed, expected):
        raise _transport.invalid_response()
    return cast(T, response.parsed)


def _configuration(
    token: str | SecretStr | None, base_url: str, timeout: float
) -> AuthenticatedClient:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("The HTTP timeout must be a finite positive number of seconds.")
    return AuthenticatedClient(
        base_url=_transport.base_url(base_url),
        token=_transport.token_value(token),
        timeout=httpx2.Timeout(timeout),
    )


def _review_url(base_url: str, organization_id: UUID, review_id: UUID) -> str:
    return (
        f"{base_url}/orgs/by-id/{quote(str(organization_id), safe='')}"
        f"/reviews/{quote(str(review_id), safe='')}"
    )


def _page_limits(page_size: int, max_pages: int, max_items: int) -> None:
    if not 1 <= page_size <= 100 or not 1 <= max_pages <= 1_000 or not 1 <= max_items <= 100_000:
        raise ValueError(
            "Pagination requires page_size 1..100, max_pages 1..1000, max_items 1..100000."
        )


def _head_commit(value: str | None) -> None:
    # Only a full SHA names one exact commit; a branch or an abbreviation does not.
    if value is not None and (
        not isinstance(value, str)
        or len(value) not in (40, 64)
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError("The head commit must be a full 40 or 64 character hexadecimal SHA.")


def _next_cursor(page: ReviewPage, seen: set[str]) -> str | None:
    if not isinstance(page.truncated, bool):
        raise _transport.invalid_response()
    if not page.truncated:
        if isinstance(page.next_cursor, str) and page.next_cursor:
            raise _transport.invalid_response()
        return None
    cursor = page.next_cursor
    if not isinstance(cursor, str) or not cursor or cursor in seen:
        raise ProoflineError(
            0,
            "urn:proofline:sdk:invalid-pagination",
            "The review page has no new continuation cursor.",
        )
    seen.add(cursor)
    return cursor


def _pagination_limit(resource: str = "Review") -> ProoflineError:
    return ProoflineError(
        0,
        "urn:proofline:sdk:pagination-limit",
        f"{resource} pagination reached the configured bound.",
    )


def _export_page_limit(max_pages: int) -> None:
    if isinstance(max_pages, bool) or not isinstance(max_pages, int) or not 1 <= max_pages <= 1_000:
        raise ValueError("Export pagination requires max_pages 1..1000.")


_IMMUTABLE_TYPES: set[type] = {
    int,
    float,
    str,
    bool,
    bytes,
    UUID,
    datetime.date,
}


def _has_mutable_captures(val: Any, seen: set[int] | None = None) -> bool:
    closure = getattr(val, "__closure__", None)
    if not closure:
        return False
    if seen is None:
        seen = set()
    if id(val) in seen:
        return False
    seen.add(id(val))
    for cell in closure:
        try:
            contents = cell.cell_contents
        except ValueError:
            continue
        if not _is_immutable(contents, seen):
            return True
    return False


def _is_immutable(val: Any, seen: set[int] | None = None) -> bool:
    if val is None or val is UNSET or isinstance(val, type):
        return True
    if hasattr(val, "__self__") and not _is_immutable(val.__self__, seen):
        return False
    t = type(val)
    if t in _IMMUTABLE_TYPES:
        return True
    if isinstance(val, (FunctionType, BuiltinFunctionType, MethodType)):
        if getattr(val, "__dict__", None):
            return False
        return not _has_mutable_captures(val, seen)
    if t is datetime.datetime:
        tz = val.tzinfo
        return tz is None or type(tz) is datetime.timezone
    return False


def _assign_target(target: Any, key: Any, is_attr: bool, val: Any) -> None:
    if target is None:
        return
    if is_attr:
        slot_or_name, is_desc = key
        if is_desc:
            slot_or_name.__set__(target, val)
        else:
            setattr(target, slot_or_name, val)
    else:
        if isinstance(target, deque):
            deque.__setitem__(target, key, val)
        elif isinstance(target, list):
            list.__setitem__(target, key, val)
        else:
            target[key] = val


def _get_obj_attrs(obj: Any) -> list[tuple[Any, bool, Any]]:
    items: list[tuple[Any, bool, Any]] = []
    seen_slots: set[int] = set()

    for cls in type(obj).__mro__:
        for name, desc in cls.__dict__.items():
            if isinstance(desc, MemberDescriptorType) or (
                type(desc).__name__ == "member_descriptor"
                and hasattr(desc, "__get__")
                and hasattr(desc, "__set__")
            ):
                if name in ("__dict__", "__weakref__"):
                    continue
                if id(desc) in seen_slots:
                    continue
                seen_slots.add(id(desc))
                try:
                    val = desc.__get__(obj, cls)
                    items.append((desc, True, val))
                except AttributeError:
                    pass

    if hasattr(obj, "__dict__") and isinstance(obj.__dict__, dict):
        for k, v in obj.__dict__.items():
            items.append((k, False, v))

    return items


_ITEM_TASK = 1
_DICT_EXPAND = 2
_LIST_EXPAND = 3
_OBJ_EXPAND = 4
_TUPLE_EXPAND = 5
_TUPLE_FINALIZE = 6
_SET_FINALIZE = 7
_SET_EXPAND = 8
_EXPAND_BATCH_SIZE = 64
_MAX_SAFE_TUPLE_SIZE = 1000
_MAX_SAFE_BUFFER_SIZE = 65_536


def _deadline_expired() -> bool:
    budget = _transport.remaining()
    return budget is not None and budget <= 0


def _snapshot_review(detail: CustomerReviewDetail) -> CustomerReviewDetail | None:
    if _deadline_expired():
        return None

    memo: dict[int, Any] = {id(UNSET): UNSET}
    root = object.__new__(type(detail))
    memo[id(detail)] = root

    deferred_dict_insertions: list[tuple[Any, Any, Any]] = []
    deferred_frozenset_insertions: list[tuple[Any, Any, bool, int, Any, list[Any]]] = []
    deferred_tuple_finalizations: list[tuple[Any, Any, bool, int, Any, list[Any]]] = []
    deferred_set_insertions: list[tuple[Any, Any, list[Any]]] = []

    stack: list[Any] = [(_OBJ_EXPAND, root, iter(_get_obj_attrs(detail)))]

    while stack:
        if _deadline_expired():
            return None

        task_type, target, it_or_key, *extra = stack.pop()

        if task_type == _ITEM_TASK:
            key, is_attr, val = it_or_key, extra[0], extra[1]
            if isinstance(val, (weakref.ref, weakref.ProxyType, weakref.CallableProxyType)):
                raise TypeError(
                    f"Unsupported mutable value in review extension data: {type(val).__name__}"
                )
            if _is_immutable(val):
                _assign_target(target, key, is_attr, val)
                continue
            val_id = id(val)
            if val_id in memo:
                _assign_target(target, key, is_attr, memo[val_id])
                continue
            if type(val) is dict:
                new_dict: dict[Any, Any] = {}
                memo[val_id] = new_dict
                _assign_target(target, key, is_attr, new_dict)
                stack.append((_DICT_EXPAND, new_dict, iter(val.items())))
            elif type(val) is list:
                new_list: list[Any] = []
                memo[val_id] = new_list
                _assign_target(target, key, is_attr, new_list)
                stack.append((_LIST_EXPAND, new_list, iter(val)))
            elif isinstance(val, tuple):
                if tuple.__len__(val) > _MAX_SAFE_TUPLE_SIZE:
                    return None
                if tuple.__len__(val) == 0:
                    if type(val) is tuple:
                        res_empty: Any = ()
                    else:
                        try:
                            val_cls: Any = type(val)
                            res_empty = tuple.__new__(val_cls, ())
                        except Exception:
                            return None
                    memo[val_id] = res_empty
                    if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                        stack.append((_OBJ_EXPAND, res_empty, iter(_get_obj_attrs(val))))
                    _assign_target(target, key, is_attr, res_empty)
                else:
                    temp_list: list[Any] = []
                    stack.append(
                        (
                            _TUPLE_FINALIZE,
                            target,
                            key,
                            is_attr,
                            val_id,
                            val,
                            temp_list,
                        )
                    )
                    stack.append((_TUPLE_EXPAND, temp_list, tuple.__iter__(val)))
            elif isinstance(val, dict):
                if "__copy__" in type(val).__dict__:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
                try:
                    if isinstance(val, defaultdict):
                        new_dict = type(val)(None)
                    else:
                        new_dict = dict.__new__(type(val))
                    dict.clear(new_dict)
                except Exception as exc:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    ) from exc
                memo[val_id] = new_dict
                _assign_target(target, key, is_attr, new_dict)
                if isinstance(val, defaultdict) and val.default_factory is not None:
                    stack.append(
                        (
                            _ITEM_TASK,
                            new_dict,
                            ("default_factory", False),
                            True,
                            val.default_factory,
                        )
                    )
                if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                    stack.append((_OBJ_EXPAND, new_dict, iter(_get_obj_attrs(val))))
                stack.append((_DICT_EXPAND, new_dict, iter(val.items())))
            elif isinstance(val, list):
                if "__copy__" in type(val).__dict__:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
                try:
                    new_list = list.__new__(type(val))
                    list.clear(new_list)
                except Exception as exc:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    ) from exc
                memo[val_id] = new_list
                _assign_target(target, key, is_attr, new_list)
                stack.append((_LIST_EXPAND, new_list, iter(val)))
                if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                    stack.append((_OBJ_EXPAND, new_list, iter(_get_obj_attrs(val))))
            elif isinstance(val, set):
                if "__copy__" in type(val).__dict__:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
                set_len = set.__len__(val)
                if type(val) is not set:
                    try:
                        if set_len == 0:
                            inspect_signature(type(val).__init__).bind(type(val))
                        else:
                            inspect_signature(type(val).__init__).bind(type(val), ())
                    except TypeError:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
                if type(val) is set:
                    new_set: set[Any] = set()
                else:
                    try:
                        new_set = set.__new__(type(val))
                        set.clear(new_set)
                    except Exception as exc:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        ) from exc
                    if set(new_set):
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
                memo[val_id] = new_set
                _assign_target(target, key, is_attr, new_set)
                if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                    stack.append((_OBJ_EXPAND, new_set, iter(_get_obj_attrs(val))))
                if set_len > 0:
                    deferred_set_insertions.append((new_set, val, list(val)))
                    stack.append((_SET_EXPAND, None, iter(val)))
            elif isinstance(val, frozenset):
                fs_len = frozenset.__len__(val)
                if type(val) is not frozenset:
                    try:
                        if fs_len == 0:
                            inspect_signature(type(val).__init__).bind(type(val))
                        else:
                            inspect_signature(type(val).__init__).bind(type(val), ())
                    except TypeError:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
                if fs_len == 0:
                    if type(val) is frozenset:
                        res_empty_fs: Any = frozenset()
                    else:
                        try:
                            res_empty_fs = frozenset.__new__(type(val), ())
                        except Exception as exc:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(val).__name__}"
                            ) from exc
                        if frozenset(res_empty_fs):
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(val).__name__}"
                            )
                    memo[val_id] = res_empty_fs
                    if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                        stack.append((_OBJ_EXPAND, res_empty_fs, iter(_get_obj_attrs(val))))
                    _assign_target(target, key, is_attr, res_empty_fs)
                else:
                    deferred_frozenset_insertions.append(
                        (target, key, is_attr, val_id, val, list(val))
                    )
                    stack.append((_SET_EXPAND, None, iter(val)))
            elif isinstance(val, deque):
                if deque.__len__(val) > _MAX_SAFE_BUFFER_SIZE:
                    return None
                if type(val) is deque:
                    new_deque: deque[Any] = deque(maxlen=val.maxlen)
                else:
                    try:
                        new_deque = deque.__new__(type(val))
                        deque.__init__(new_deque, maxlen=val.maxlen)
                    except Exception as exc:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        ) from exc
                memo[val_id] = new_deque
                _assign_target(target, key, is_attr, new_deque)
                stack.append((_LIST_EXPAND, new_deque, deque.__iter__(val)))
                if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                    stack.append((_OBJ_EXPAND, new_deque, iter(_get_obj_attrs(val))))
            elif isinstance(val, bytearray):
                if bytearray.__len__(val) > _MAX_SAFE_BUFFER_SIZE:
                    return None
                try:
                    resolved = bytearray.__new__(type(val))
                    bytearray.__init__(resolved, val)
                except Exception as exc:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    ) from exc
                memo[val_id] = resolved
                _assign_target(target, key, is_attr, resolved)
                if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                    stack.append((_OBJ_EXPAND, resolved, iter(_get_obj_attrs(val))))
            elif isinstance(val, memoryview):
                if val.nbytes > _MAX_SAFE_BUFFER_SIZE:
                    return None
                resolved_mv: Any
                if val.readonly:
                    resolved_mv = memoryview(bytes(val))
                    if val.format != "B" or val.ndim > 1:
                        try:
                            resolved_mv = resolved_mv.cast(val.format, shape=val.shape)
                        except Exception as exc:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(val).__name__}"
                            ) from exc
                else:
                    resolved_mv = memoryview(bytearray(val))
                    if val.format != "B" or val.ndim > 1:
                        try:
                            resolved_mv = resolved_mv.cast(val.format, shape=val.shape)
                        except Exception as exc:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(val).__name__}"
                            ) from exc
                memo[val_id] = resolved_mv
                _assign_target(target, key, is_attr, resolved_mv)
            elif isinstance(val, datetime.datetime):
                tz = val.tzinfo
                copied_tz = tz
                if tz is not None and type(tz) is not datetime.timezone:
                    if id(tz) in memo:
                        copied_tz = memo[id(tz)]
                    else:
                        if "__copy__" in type(tz).__dict__:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(tz).__name__}"
                            )
                        try:
                            copied_tz = datetime.tzinfo.__new__(type(tz))
                        except Exception as exc:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(tz).__name__}"
                            ) from exc
                        memo[id(tz)] = copied_tz
                        if hasattr(tz, "__dict__") or hasattr(tz, "__slots__"):
                            stack.append((_OBJ_EXPAND, copied_tz, iter(_get_obj_attrs(tz))))

                if type(val) is datetime.datetime:
                    if copied_tz is tz and (tz is None or type(tz) is datetime.timezone):
                        _assign_target(target, key, is_attr, val)
                    else:
                        new_dt = val.replace(tzinfo=copied_tz)
                        memo[val_id] = new_dt
                        _assign_target(target, key, is_attr, new_dt)
                else:
                    try:
                        new_dt = val.replace(tzinfo=copied_tz)
                    except Exception:
                        try:
                            new_dt = type(val).__new__(
                                type(val),
                                val.year,
                                val.month,
                                val.day,
                                val.hour,
                                val.minute,
                                val.second,
                                val.microsecond,
                                tzinfo=copied_tz,
                                fold=val.fold,
                            )
                        except Exception as exc:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(val).__name__}"
                            ) from exc
                    if new_dt is val or new_dt.tzinfo is not copied_tz:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
                    memo[val_id] = new_dt
                    _assign_target(target, key, is_attr, new_dt)
                    if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                        stack.append((_OBJ_EXPAND, new_dt, iter(_get_obj_attrs(val))))
            elif hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                new_obj: Any
                try:
                    if isinstance(val, str):
                        new_obj = str.__new__(type(val), val)
                    elif isinstance(val, bytes):
                        new_obj = bytes.__new__(type(val), val)
                    elif isinstance(val, int):
                        new_obj = int.__new__(type(val), val)
                    elif isinstance(val, float):
                        new_obj = float.__new__(type(val), val)
                    else:
                        new_obj = object.__new__(type(val))
                except Exception as exc:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    ) from exc
                memo[val_id] = new_obj
                _assign_target(target, key, is_attr, new_obj)
                stack.append((_OBJ_EXPAND, new_obj, iter(_get_obj_attrs(val))))
            else:
                raise TypeError(
                    f"Unsupported mutable value in review extension data: {type(val).__name__}"
                )

        elif task_type == _DICT_EXPAND:
            target_dict, it = target, it_or_key
            for _ in range(_EXPAND_BATCH_SIZE):
                try:
                    k, v = next(it)
                except StopIteration:
                    break
                deferred_dict_insertions.append((target_dict, k, v))
                k_needed = not _is_immutable(k) and id(k) not in memo
                v_needed = not _is_immutable(v) and id(v) not in memo
                if k_needed or v_needed:
                    stack.append((_DICT_EXPAND, target_dict, it))
                    if v_needed:
                        stack.append((_ITEM_TASK, None, 0, False, v))
                    if k_needed:
                        stack.append((_ITEM_TASK, None, 0, False, k))
                    break
            else:
                stack.append((_DICT_EXPAND, target_dict, it))

        elif task_type == _SET_EXPAND:
            it = it_or_key
            for _ in range(_EXPAND_BATCH_SIZE):
                try:
                    m = next(it)
                except StopIteration:
                    break
                if not _is_immutable(m) and id(m) not in memo:
                    stack.append((_SET_EXPAND, None, it))
                    stack.append((_ITEM_TASK, None, 0, False, m))
                    break
            else:
                stack.append((_SET_EXPAND, None, it))

        elif task_type == _LIST_EXPAND:
            target_list, it = target, it_or_key
            is_dq = isinstance(target_list, deque)
            app_fn = deque.append if is_dq else list.append
            len_fn = deque.__len__ if is_dq else list.__len__
            for _ in range(_EXPAND_BATCH_SIZE):
                try:
                    v = next(it)
                except StopIteration:
                    break
                if _is_immutable(v):
                    app_fn(target_list, v)
                elif id(v) in memo:
                    app_fn(target_list, memo[id(v)])
                else:
                    idx = len_fn(target_list)
                    app_fn(target_list, None)
                    stack.append((_LIST_EXPAND, target_list, it))
                    stack.append((_ITEM_TASK, target_list, idx, False, v))
                    break
            else:
                stack.append((_LIST_EXPAND, target_list, it))

        elif task_type == _OBJ_EXPAND:
            new_obj, it = target, it_or_key
            for _ in range(_EXPAND_BATCH_SIZE):
                try:
                    slot_or_name, is_desc, attr_val = next(it)
                except StopIteration:
                    break
                if _is_immutable(attr_val):
                    _assign_target(new_obj, (slot_or_name, is_desc), True, attr_val)
                elif id(attr_val) in memo:
                    _assign_target(new_obj, (slot_or_name, is_desc), True, memo[id(attr_val)])
                else:
                    stack.append((_OBJ_EXPAND, new_obj, it))
                    stack.append((_ITEM_TASK, new_obj, (slot_or_name, is_desc), True, attr_val))
                    break
            else:
                stack.append((_OBJ_EXPAND, new_obj, it))

        elif task_type == _TUPLE_EXPAND:
            temp_list, it = target, it_or_key
            for _ in range(_EXPAND_BATCH_SIZE):
                try:
                    v = next(it)
                except StopIteration:
                    break
                if _is_immutable(v):
                    temp_list.append(v)
                elif id(v) in memo:
                    temp_list.append(memo[id(v)])
                else:
                    idx = len(temp_list)
                    temp_list.append(None)
                    stack.append((_TUPLE_EXPAND, temp_list, it))
                    stack.append((_ITEM_TASK, temp_list, idx, False, v))
                    break
            else:
                stack.append((_TUPLE_EXPAND, temp_list, it))

        elif task_type == _TUPLE_FINALIZE:
            key, is_attr, val_id, orig_val, temp_list = (
                it_or_key,
                extra[0],
                extra[1],
                extra[2],
                extra[3],
            )
            if any(x is None for x in temp_list):
                deferred_tuple_finalizations.append(
                    (target, key, is_attr, val_id, orig_val, temp_list)
                )
                continue
            if val_id in memo:
                res_tuple = memo[val_id]
            elif type(orig_val) is tuple and all(a is b for a, b in zip(orig_val, temp_list)):
                res_tuple = orig_val
                memo[val_id] = res_tuple
            else:
                if type(orig_val) is tuple:
                    res_tuple = tuple(temp_list)
                else:
                    try:
                        orig_cls: Any = type(orig_val)
                        res_tuple = tuple.__new__(orig_cls, temp_list)
                    except Exception:
                        return None
                memo[val_id] = res_tuple
            if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                stack.append((_OBJ_EXPAND, res_tuple, iter(_get_obj_attrs(orig_val))))
            _assign_target(target, key, is_attr, res_tuple)

    if _deadline_expired():
        return None

    deferred_custom_dict_insertions: list[tuple[Any, Any, Any]] = []
    deferred_later_dict_insertions: list[tuple[Any, Any, Any]] = []
    for target_dict, orig_k, orig_v in deferred_dict_insertions:
        if _deadline_expired():
            return None
        if _is_immutable(orig_k):
            if _is_immutable(orig_v):
                target_dict[orig_k] = orig_v
            elif id(orig_v) in memo:
                target_dict[orig_k] = memo[id(orig_v)]
            else:
                deferred_later_dict_insertions.append((target_dict, orig_k, orig_v))
        else:
            deferred_custom_dict_insertions.append((target_dict, orig_k, orig_v))

    for target, key, is_attr, val_id, orig_val, orig_members in deferred_frozenset_insertions:
        if _deadline_expired():
            return None
        if val_id in memo:
            res_set = memo[val_id]
        else:
            resolved_members = [m if _is_immutable(m) else memo[id(m)] for m in orig_members]
            if type(orig_val) is frozenset:
                res_set = frozenset(resolved_members)
            else:
                try:
                    res_set = frozenset.__new__(type(orig_val), resolved_members)
                except Exception as exc:
                    raise TypeError(
                        "Unsupported mutable value in review extension data: "
                        f"{type(orig_val).__name__}"
                    ) from exc
                if frozenset(res_set) != frozenset(resolved_members):
                    raise TypeError(
                        "Unsupported mutable value in review extension data: "
                        f"{type(orig_val).__name__}"
                    )
            memo[val_id] = res_set
            if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                for slot_or_name, is_desc, attr_val in _get_obj_attrs(orig_val):
                    val_to_set = attr_val if _is_immutable(attr_val) else memo[id(attr_val)]
                    _assign_target(res_set, (slot_or_name, is_desc), True, val_to_set)
        _assign_target(target, key, is_attr, res_set)

    for target_dict, orig_k, orig_v in deferred_later_dict_insertions:
        if _deadline_expired():
            return None
        target_dict[orig_k] = memo[id(orig_v)]

    for target, key, is_attr, val_id, orig_val, temp_list in deferred_tuple_finalizations:
        if _deadline_expired():
            return None
        if val_id in memo:
            res_tuple = memo[val_id]
        else:
            if type(orig_val) is tuple:
                res_tuple = tuple(temp_list)
            else:
                try:
                    orig_tuple_cls: Any = type(orig_val)
                    res_tuple = tuple.__new__(orig_tuple_cls, temp_list)
                except Exception:
                    return None
            memo[val_id] = res_tuple
        if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
            for slot_or_name, is_desc, attr_val in _get_obj_attrs(orig_val):
                val_to_set = attr_val if _is_immutable(attr_val) else memo[id(attr_val)]
                _assign_target(res_tuple, (slot_or_name, is_desc), True, val_to_set)
        _assign_target(target, key, is_attr, res_tuple)

    for s, orig_val, orig_members in deferred_set_insertions:
        if _deadline_expired():
            return None
        resolved_members = [m if _is_immutable(m) else memo[id(m)] for m in orig_members]
        set.update(s, resolved_members)
        if set(s) != set(resolved_members):
            raise TypeError(
                f"Unsupported mutable value in review extension data: {type(orig_val).__name__}"
            )

    for target_dict, orig_k, orig_v in deferred_custom_dict_insertions:
        if _deadline_expired():
            return None
        k = memo[id(orig_k)]
        v = orig_v if _is_immutable(orig_v) else memo[id(orig_v)]
        target_dict[k] = v

    return root


_DETACHED_TASKS: dict[int, Any] = {}
_DETACHED_FUTURES: dict[int, Any] = {}


def _safe_cancel_target(target: Any) -> None:
    try:
        target.cancel()
    except BaseException:
        pass


def _detach_overdue_future(fut: Any) -> None:
    try:
        is_done = fut.done() if hasattr(fut, "done") else AsyncFuture.done(fut)
        if is_done:
            is_canc = fut.cancelled() if hasattr(fut, "cancelled") else AsyncFuture.cancelled(fut)
            if not is_canc:
                try:
                    if hasattr(fut, "exception"):
                        fut.exception()
                    else:
                        AsyncFuture.exception(fut)
                except Exception:
                    pass
            return
        try:
            loop = fut.get_loop() if hasattr(fut, "get_loop") else AsyncFuture.get_loop(fut)
        except Exception:
            return
        try:
            running_loop = async_get_running_loop()
        except Exception:
            return
        if loop is not running_loop or loop.is_closed():
            return
        fut_id = id(fut)
        _DETACHED_FUTURES[fut_id] = fut

        def _on_detached_fut_done(t: Any) -> None:
            _DETACHED_FUTURES.pop(fut_id, None)
            try:
                is_canc = t.cancelled() if hasattr(t, "cancelled") else False
                if not is_canc:
                    if hasattr(t, "exception"):
                        t.exception()
            except BaseException:
                pass

        try:
            if hasattr(fut, "add_done_callback"):
                fut.add_done_callback(_on_detached_fut_done)
            else:
                AsyncFuture.add_done_callback(fut, _on_detached_fut_done)
        except BaseException:
            _DETACHED_FUTURES.pop(fut_id, None)
    except BaseException:
        pass


def _detach_overdue_task(
    task: Any,
    res: Any,
    wrapper_started: bool,
) -> None:
    task_id = id(task)
    _DETACHED_TASKS[task_id] = task

    def _on_detached_task_done(t: Any) -> None:
        _DETACHED_TASKS.pop(task_id, None)
        try:
            is_canc = t.cancelled() if hasattr(t, "cancelled") else False
            if not is_canc:
                if hasattr(t, "exception"):
                    t.exception()
        except BaseException:
            pass

    try:
        if hasattr(task, "add_done_callback"):
            task.add_done_callback(_on_detached_task_done)
        else:
            AsyncFuture.add_done_callback(task, _on_detached_task_done)
    except BaseException:
        _DETACHED_TASKS.pop(task_id, None)
    if not wrapper_started:
        if iscoroutine(res) and getcoroutinestate(res) == CORO_CREATED:
            try:
                res.close()
            except BaseException:
                pass
        elif isgenerator(res) and getgeneratorstate(res) == GEN_CREATED:
            try:
                res.close()
            except BaseException:
                pass


def _export_next_cursor(page: ExportPage, seen: set[str]) -> str | None:
    cursor = page.next_cursor
    if cursor is None:
        return None
    if not cursor or cursor in seen:
        raise ProoflineError(
            0,
            "urn:proofline:sdk:invalid-pagination",
            "The export page has no new continuation cursor.",
        )
    seen.add(cursor)
    return cursor


class ProoflineClient(Operations):
    """Synchronous typed HTTP operations.

    Name resolution, connection, TLS and socket operations stop at the configured
    HTTP timeout and at a wait deadline.
    """

    def __init__(
        self,
        token: str | SecretStr | None = None,
        *,
        base_url: str = "https://proofline.sh",
        timeout: float = 30,
    ) -> None:
        self._api = _configuration(token, base_url, timeout)
        self._base_url = _transport.base_url(base_url)
        self._http = httpx2.Client(
            base_url=self._base_url,
            auth=_transport.BearerAuth(self._api.token),
            headers={
                "User-Agent": f"proofline-python/{_transport.VERSION}",
                "Accept-Encoding": "identity",
            },
            timeout=httpx2.Timeout(timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.RetryTransport(self._api.token, timeout),
        )
        self._api.set_httpx_client(self._http)
        self.mcp = McpClient(self._http)
        self.knowledge = KnowledgeClient(self._http)
        self.fixes = FixesClient(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _call(
        self,
        operation: Callable[..., Response[Any]],
        expected: type[T]
        | _ReviewRoutingModels
        | _FindingFixPromptModels
        | _AgentSessionPromptModels,
        *args: object,
        **kwargs: object,
    ) -> T:
        with _transport.operation_errors():
            return _decoded(operation(*args, client=self._api, **kwargs), expected)

    def export_reviews(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
    ) -> ExportPage:
        """Read one export page. Repeat with next_cursor and the same filters."""
        if dataset not in (
            "reviews",
            "finding_outcomes",
            "finding_validations",
            "spend",
            "findings",
        ):
            raise ValueError("Unknown export dataset.")
        if format not in ("csv", "ndjson"):
            raise ValueError("Export format must be csv or ndjson.")
        params = {"from": from_time, "to": to_time, "format": format}
        if cursor is not None:
            params["cursor"] = cursor
        if group_by is not None:
            params["group_by"] = group_by
        try:
            response = self._http.get(
                f"/api/v1/organizations/{organization_id}/exports/{dataset}",
                params=params,
                headers={"Accept": "text/csv" if format == "csv" else "application/x-ndjson"},
            )
            return decode_export(response, format, dataset)
        except httpx2.HTTPError as error:
            raise _transport.network_error(error) from None

    def iter_export_pages(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
        max_pages: int = 100,
    ) -> Iterator[ExportPage]:
        """Stream export pages, refusing cursor cycles and incomplete bounded traversals."""
        _export_page_limit(max_pages)
        seen = {cursor} if cursor is not None else set()
        for _ in range(max_pages):
            page = self.export_reviews(
                organization_id,
                dataset,
                from_time=from_time,
                to_time=to_time,
                format=format,
                cursor=cursor,
                group_by=group_by,
            )
            cursor = _export_next_cursor(page, seen)
            yield page
            if cursor is None:
                return
        raise _pagination_limit("Export")

    def list_reviews(self, organization_id: UUID, **filters: Unpack[ReviewFilters]) -> ReviewPage:
        return self._call(list_reviews.sync_detailed, ReviewPage, organization_id, **filters)

    def list_pull_request_reviews(
        self,
        organization_id: UUID,
        repository: str,
        pull_request_number: int,
        *,
        filters: ReviewFilters | None = None,
    ) -> ReviewPage:
        params = dict(filters or {})
        params["repository_query"] = params.pop("repository", None)
        return self._call(
            list_pull_request_reviews.sync_detailed,
            ReviewPage,
            organization_id,
            repository,
            pull_request_number,
            **params,
        )

    def get_pull_request_review(
        self, organization_id: UUID, repository: str, pull_request_number: int, run_number: int
    ) -> CustomerReviewDetail:
        return self._call(
            get_pull_request_review.sync_detailed,
            CustomerReviewDetail,
            organization_id,
            repository,
            pull_request_number,
            run_number,
        )

    def get_deployment_review(self, organization_id: UUID, public_key: str) -> CustomerReviewDetail:
        return self._call(
            get_deployment_review.sync_detailed, CustomerReviewDetail, organization_id, public_key
        )

    def get_review(self, organization_id: UUID, review_id: UUID) -> CustomerReviewDetail:
        return self._call(
            get_review.sync_detailed, CustomerReviewDetail, organization_id, review_id
        )

    def get_review_routing(self, organization_id: UUID, review_id: UUID) -> ReviewRoutingView:
        return self._call(
            get_review_routing.sync_detailed,
            _REVIEW_ROUTING_MODELS,
            organization_id,
            review_id,
        )

    def get_assessment(
        self, organization_id: UUID, review_id: UUID, assessment_id: UUID
    ) -> CustomerAssessmentDetail:
        return self._call(
            get_assessment.sync_detailed,
            CustomerAssessmentDetail,
            organization_id,
            review_id,
            assessment_id,
        )

    def get_finding(self, organization_id: UUID, finding_id: UUID) -> CustomerFinding:
        return self._call(get_finding.sync_detailed, CustomerFinding, organization_id, finding_id)

    def get_agent_session(self, organization_id: UUID, session_id: UUID) -> AgentSession:
        return self._call(
            get_agent_session.sync_detailed, AgentSession, organization_id, session_id
        )

    def get_agent_session_prompt(
        self, organization_id: UUID, finding_id: UUID
    ) -> AgentSessionPrompt:
        return self._call(
            get_agent_session_prompt.sync_detailed,
            _AGENT_SESSION_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    def start_agent_session(
        self, organization_id: UUID, finding_id: UUID, *, body: StartSession
    ) -> AgentSession:
        return self._call(
            start_agent_session.sync_detailed, AgentSession, organization_id, finding_id, body=body
        )

    def get_finding_fix_prompt(self, organization_id: UUID, finding_id: UUID) -> FindingFixPrompt:
        return self._call(
            get_finding_fix_prompt.sync_detailed,
            _FINDING_FIX_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    def get_review_guidance(self, organization_id: UUID, repository_id: UUID) -> RepositoryGuidance:
        return self._call(
            get_review_guidance.sync_detailed, RepositoryGuidance, organization_id, repository_id
        )

    def list_repositories(self, organization_id: UUID) -> RepositoryNames:
        return self._call(list_repositories.sync_detailed, RepositoryNames, organization_id)

    def request_review(
        self,
        organization_id: UUID,
        repository_id: UUID,
        pull_request_number: int,
        *,
        body: RunNowRequest | Unset = UNSET,
    ) -> RunNowResponse:
        return self._call(
            request_review.sync_detailed,
            RunNowResponse,
            organization_id,
            repository_id,
            pull_request_number,
            body=body,
        )

    def request_patch_review(
        self, organization_id: UUID, repository_id: UUID, *, body: PatchReviewRequest
    ) -> PatchReviewResponse:
        return self._call(
            request_patch_review.sync_detailed,
            PatchReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def upload_coverage_reports(
        self, organization_id: UUID, repository_id: UUID, *, body: CoverageUploadRequest
    ) -> CoverageUploadResponse:
        return self._call(
            upload_coverage_reports.sync_detailed,
            CoverageUploadResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def request_file_review(
        self, organization_id: UUID, repository_id: UUID, *, body: FileReviewRequest
    ) -> FileReviewResponse:
        return self._call(
            request_file_review.sync_detailed,
            FileReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def stop_review(self, organization_id: UUID, review_id: UUID) -> StopResponse:
        return self._call(stop_review.sync_detailed, StopResponse, organization_id, review_id)

    def request_commit_review(
        self, organization_id: UUID, repository_id: UUID, *, body: CommitReviewRequest
    ) -> CommitReviewResponse:
        return self._call(
            request_commit_review.sync_detailed,
            CommitReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    def rerun_review(self, organization_id: UUID, review_id: UUID) -> RerunResponse:
        return self._call(rerun_review.sync_detailed, RerunResponse, organization_id, review_id)

    def iter_reviews(
        self,
        organization_id: UUID,
        *,
        page_size: int = 100,
        max_pages: int = 100,
        max_items: int = 10_000,
        filters: ReviewFilters | None = None,
    ) -> Iterator[ReviewSummary]:
        _page_limits(page_size, max_pages, max_items)
        params: ReviewFilters = {}
        if filters:
            params.update(filters)
        params["limit"] = page_size
        seen: set[str] = set()
        cursor = params.get("cursor")
        if cursor:
            seen.add(cursor)
        count = 0
        for _ in range(max_pages):
            page = self.list_reviews(organization_id, **params)
            for item in page.items:
                if count == max_items:
                    raise _pagination_limit()
                yield item
                count += 1
            cursor = _next_cursor(page, seen)
            if cursor is None:
                return
            params["cursor"] = cursor
        raise _pagination_limit()

    def wait_for_review(
        self,
        organization_id: UUID,
        review_id: UUID,
        *,
        timeout: float = 300,
        head_commit_sha: str | None = None,
        on_poll: Callable[[CustomerReviewDetail], None] | None = None,
    ) -> ReviewOutcome:
        """Wait for recorded review completion or return TIMED_OUT.

        A name lookup still running at the deadline returns TIMED_OUT; it never
        reports completion.

        head_commit_sha holds the outcome to that commit. A review pinned to
        another head ends the wait on that read and is never COMPLETED.

        When on_poll is provided, it is called on each review poll with the
        latest CustomerReviewDetail. Only reviews fetched and validated before
        the callback is reached are delivered; deadline expiry can suppress
        delivery. Oversized tuples or buffers in review extension data skip
        on_poll snapshot delivery even with time remaining, and snapshot copy
        errors on unsupported mutable values propagate before on_poll runs.
        on_poll exceptions and return-validation errors propagate even when a
        terminal outcome has already been determined and can prevent the waiter
        from returning a classified outcome. Synchronous callbacks must return
        None (returning an awaitable or any return value other than None raises
        TypeError) and must return before a terminal result can be delivered;
        the polling deadline cannot interrupt them.
        """

        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("The review timeout must be a finite nonnegative number of seconds.")
        _head_commit(head_commit_sha)
        url = _review_url(self._base_url, organization_id, review_id)
        last: CustomerReviewDetail | None = None
        result: ReviewOutcome | None = None
        deadline = _transport.DEADLINE.set(monotonic() + timeout)
        interval = 5.0
        try:
            while (_transport.remaining() or 0) > 0:
                try:
                    last = self.get_review(organization_id, review_id)
                except ProoflineError as error:
                    if error.status == 0 and (_transport.remaining() or 0) <= 0:
                        break
                    raise
                if (_transport.remaining() or 0) <= 0:
                    break
                result = outcome(last, url, review_id=review_id, head_commit_sha=head_commit_sha)
                if on_poll is not None and (_transport.remaining() or 0) > 0:
                    snapshot = _snapshot_review(last)
                    if snapshot is not None and (_transport.remaining() or 0) > 0:
                        res = on_poll(snapshot)
                        try:
                            res_awaitable = isawaitable(res)
                        except Exception:
                            raise TypeError("Callbacks must return None.") from None
                        if res_awaitable:
                            if iscoroutine(res):
                                try:
                                    if getcoroutinestate(res) == CORO_CREATED:
                                        res.close()
                                except Exception:
                                    pass
                            elif isgenerator(res):
                                try:
                                    if getgeneratorstate(res) == GEN_CREATED:
                                        res.close()
                                except Exception:
                                    pass
                            raise TypeError(
                                "on_poll returned an awaitable; use AsyncProoflineClient "
                                "for async callbacks."
                            )
                        if res is not None:
                            raise TypeError("Callbacks must return None.")
                if result is not None:
                    return result
                if (_transport.remaining() or 0) <= 0:
                    break
                sleep(min(interval, _transport.remaining() or 0))
                interval = min(60, interval * 2)
            if result is not None:
                return result
            timed_out = outcome(last, url, "TIMED_OUT", head_commit_sha=head_commit_sha)
            return timed_out or ReviewOutcome("TIMED_OUT", url)
        finally:
            _transport.DEADLINE.reset(deadline)


class AsyncProoflineClient(AsyncOperations):
    def __init__(
        self,
        token: str | SecretStr | None = None,
        *,
        base_url: str = "https://proofline.sh",
        timeout: float = 30,
    ) -> None:
        self._api = _configuration(token, base_url, timeout)
        self._base_url = _transport.base_url(base_url)
        self._http = httpx2.AsyncClient(
            base_url=self._base_url,
            auth=_transport.BearerAuth(self._api.token),
            headers={
                "User-Agent": f"proofline-python/{_transport.VERSION}",
                "Accept-Encoding": "identity",
            },
            timeout=httpx2.Timeout(timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.AsyncRetryTransport(self._api.token, timeout),
        )
        self._api.set_async_httpx_client(self._http)
        self.mcp = AsyncMcpClient(self._http)
        self.knowledge = AsyncKnowledgeClient(self._http)
        self.fixes = AsyncFixesClient(self._http)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def _call(
        self,
        operation: Callable[..., Awaitable[Response[Any]]],
        expected: type[T]
        | _ReviewRoutingModels
        | _FindingFixPromptModels
        | _AgentSessionPromptModels,
        *args: object,
        **kwargs: object,
    ) -> T:
        with _transport.operation_errors():
            return _decoded(await operation(*args, client=self._api, **kwargs), expected)

    async def export_reviews(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
    ) -> ExportPage:
        """Read one export page. Repeat with next_cursor and the same filters."""
        if dataset not in (
            "reviews",
            "finding_outcomes",
            "finding_validations",
            "spend",
            "findings",
        ):
            raise ValueError("Unknown export dataset.")
        if format not in ("csv", "ndjson"):
            raise ValueError("Export format must be csv or ndjson.")
        params = {"from": from_time, "to": to_time, "format": format}
        if cursor is not None:
            params["cursor"] = cursor
        if group_by is not None:
            params["group_by"] = group_by
        try:
            response = await self._http.get(
                f"/api/v1/organizations/{organization_id}/exports/{dataset}",
                params=params,
                headers={"Accept": "text/csv" if format == "csv" else "application/x-ndjson"},
            )
            return decode_export(response, format, dataset)
        except httpx2.HTTPError as error:
            raise _transport.network_error(error) from None

    async def iter_export_pages(
        self,
        organization_id: UUID,
        dataset: ExportDataset,
        *,
        from_time: str,
        to_time: str,
        format: ExportFormat = "ndjson",
        cursor: str | None = None,
        group_by: str | None = None,
        max_pages: int = 100,
    ) -> AsyncIterator[ExportPage]:
        """Stream export pages, refusing cursor cycles and incomplete bounded traversals."""
        _export_page_limit(max_pages)
        seen = {cursor} if cursor is not None else set()
        for _ in range(max_pages):
            page = await self.export_reviews(
                organization_id,
                dataset,
                from_time=from_time,
                to_time=to_time,
                format=format,
                cursor=cursor,
                group_by=group_by,
            )
            cursor = _export_next_cursor(page, seen)
            yield page
            if cursor is None:
                return
        raise _pagination_limit("Export")

    async def list_reviews(
        self, organization_id: UUID, **filters: Unpack[ReviewFilters]
    ) -> ReviewPage:
        return await self._call(
            list_reviews.asyncio_detailed, ReviewPage, organization_id, **filters
        )

    async def list_pull_request_reviews(
        self,
        organization_id: UUID,
        repository: str,
        pull_request_number: int,
        *,
        filters: ReviewFilters | None = None,
    ) -> ReviewPage:
        params = dict(filters or {})
        params["repository_query"] = params.pop("repository", None)
        return await self._call(
            list_pull_request_reviews.asyncio_detailed,
            ReviewPage,
            organization_id,
            repository,
            pull_request_number,
            **params,
        )

    async def get_pull_request_review(
        self, organization_id: UUID, repository: str, pull_request_number: int, run_number: int
    ) -> CustomerReviewDetail:
        return await self._call(
            get_pull_request_review.asyncio_detailed,
            CustomerReviewDetail,
            organization_id,
            repository,
            pull_request_number,
            run_number,
        )

    async def get_deployment_review(
        self, organization_id: UUID, public_key: str
    ) -> CustomerReviewDetail:
        return await self._call(
            get_deployment_review.asyncio_detailed,
            CustomerReviewDetail,
            organization_id,
            public_key,
        )

    async def get_review(self, organization_id: UUID, review_id: UUID) -> CustomerReviewDetail:
        return await self._call(
            get_review.asyncio_detailed, CustomerReviewDetail, organization_id, review_id
        )

    async def get_review_routing(self, organization_id: UUID, review_id: UUID) -> ReviewRoutingView:
        return await self._call(
            get_review_routing.asyncio_detailed,
            _REVIEW_ROUTING_MODELS,
            organization_id,
            review_id,
        )

    async def get_assessment(
        self, organization_id: UUID, review_id: UUID, assessment_id: UUID
    ) -> CustomerAssessmentDetail:
        return await self._call(
            get_assessment.asyncio_detailed,
            CustomerAssessmentDetail,
            organization_id,
            review_id,
            assessment_id,
        )

    async def get_finding(self, organization_id: UUID, finding_id: UUID) -> CustomerFinding:
        return await self._call(
            get_finding.asyncio_detailed, CustomerFinding, organization_id, finding_id
        )

    async def get_agent_session(self, organization_id: UUID, session_id: UUID) -> AgentSession:
        return await self._call(
            get_agent_session.asyncio_detailed, AgentSession, organization_id, session_id
        )

    async def get_agent_session_prompt(
        self, organization_id: UUID, finding_id: UUID
    ) -> AgentSessionPrompt:
        return await self._call(
            get_agent_session_prompt.asyncio_detailed,
            _AGENT_SESSION_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    async def start_agent_session(
        self, organization_id: UUID, finding_id: UUID, *, body: StartSession
    ) -> AgentSession:
        return await self._call(
            start_agent_session.asyncio_detailed,
            AgentSession,
            organization_id,
            finding_id,
            body=body,
        )

    async def get_finding_fix_prompt(
        self, organization_id: UUID, finding_id: UUID
    ) -> FindingFixPrompt:
        return await self._call(
            get_finding_fix_prompt.asyncio_detailed,
            _FINDING_FIX_PROMPT_MODELS,
            organization_id,
            finding_id,
        )

    async def get_review_guidance(
        self, organization_id: UUID, repository_id: UUID
    ) -> RepositoryGuidance:
        return await self._call(
            get_review_guidance.asyncio_detailed, RepositoryGuidance, organization_id, repository_id
        )

    async def list_repositories(self, organization_id: UUID) -> RepositoryNames:
        return await self._call(
            list_repositories.asyncio_detailed, RepositoryNames, organization_id
        )

    async def request_review(
        self,
        organization_id: UUID,
        repository_id: UUID,
        pull_request_number: int,
        *,
        body: RunNowRequest | Unset = UNSET,
    ) -> RunNowResponse:
        return await self._call(
            request_review.asyncio_detailed,
            RunNowResponse,
            organization_id,
            repository_id,
            pull_request_number,
            body=body,
        )

    async def request_patch_review(
        self, organization_id: UUID, repository_id: UUID, *, body: PatchReviewRequest
    ) -> PatchReviewResponse:
        return await self._call(
            request_patch_review.asyncio_detailed,
            PatchReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def upload_coverage_reports(
        self, organization_id: UUID, repository_id: UUID, *, body: CoverageUploadRequest
    ) -> CoverageUploadResponse:
        return await self._call(
            upload_coverage_reports.asyncio_detailed,
            CoverageUploadResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def request_file_review(
        self, organization_id: UUID, repository_id: UUID, *, body: FileReviewRequest
    ) -> FileReviewResponse:
        return await self._call(
            request_file_review.asyncio_detailed,
            FileReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def stop_review(self, organization_id: UUID, review_id: UUID) -> StopResponse:
        return await self._call(
            stop_review.asyncio_detailed, StopResponse, organization_id, review_id
        )

    async def request_commit_review(
        self, organization_id: UUID, repository_id: UUID, *, body: CommitReviewRequest
    ) -> CommitReviewResponse:
        return await self._call(
            request_commit_review.asyncio_detailed,
            CommitReviewResponse,
            organization_id,
            repository_id,
            body=body,
        )

    async def rerun_review(self, organization_id: UUID, review_id: UUID) -> RerunResponse:
        return await self._call(
            rerun_review.asyncio_detailed, RerunResponse, organization_id, review_id
        )

    async def iter_reviews(
        self,
        organization_id: UUID,
        *,
        page_size: int = 100,
        max_pages: int = 100,
        max_items: int = 10_000,
        filters: ReviewFilters | None = None,
    ) -> AsyncIterator[ReviewSummary]:
        _page_limits(page_size, max_pages, max_items)
        params: ReviewFilters = {}
        if filters:
            params.update(filters)
        params["limit"] = page_size
        seen: set[str] = set()
        cursor = params.get("cursor")
        if cursor:
            seen.add(cursor)
        count = 0
        for _ in range(max_pages):
            page = await self.list_reviews(organization_id, **params)
            for item in page.items:
                if count == max_items:
                    raise _pagination_limit()
                yield item
                count += 1
            cursor = _next_cursor(page, seen)
            if cursor is None:
                return
            params["cursor"] = cursor
        raise _pagination_limit()

    async def wait_for_review(
        self,
        organization_id: UUID,
        review_id: UUID,
        *,
        timeout: float = 300,
        head_commit_sha: str | None = None,
        on_poll: Callable[[CustomerReviewDetail], Awaitable[object] | None] | None = None,
    ) -> ReviewOutcome:
        """Wait for recorded review completion or return TIMED_OUT.

        A name lookup still running at the deadline returns TIMED_OUT; it never
        reports completion.

        head_commit_sha holds the outcome to that commit. A review pinned to
        another head ends the wait on that read and is never COMPLETED.

        When on_poll is provided, it must be a callable that accepts the review
        snapshot and returns None or an awaitable (supporting both sync and
        async callbacks). Any coroutines returned by on_poll must be unstarted, and
        any pending futures returned by on_poll must belong to the running event
        loop. Callbacks cannot return the running polling task (doing so raises
        ValueError). Callbacks must return promptly even when they return
        an awaitable, because the polling deadline cannot interrupt the
        invocation. Only reviews fetched and validated before the callback
        is reached are delivered; deadline expiry can suppress delivery. Oversized
        tuples or buffers in review extension data skip on_poll snapshot delivery
        even with time remaining, and snapshot copy errors on unsupported mutable
        values propagate before on_poll runs. Callback return-validation errors
        and exceptions propagate even when a terminal outcome has already been
        determined, preventing the waiter from returning a classified outcome.
        Inline failures and awaitable failures observed before the deadline propagate,
        but the deadline can suppress awaitable failures (and a pending future's
        failure can be suppressed if its done callback runs after the deadline),
        including when an outcome is already classified. When the deadline expires,
        unstarted coroutines returned by on_poll are closed without being scheduled,
        while already-running callback tasks and futures are detached without
        cancellation and may continue running. Synchronous
        callbacks must return before a terminal result can be delivered and the
        polling deadline cannot interrupt them.
        """
        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("The review timeout must be a finite nonnegative number of seconds.")
        _head_commit(head_commit_sha)
        url = _review_url(self._base_url, organization_id, review_id)
        last: CustomerReviewDetail | None = None
        result: ReviewOutcome | None = None
        deadline = _transport.DEADLINE.set(monotonic() + timeout)
        interval = 5.0
        try:
            while (_transport.remaining() or 0) > 0:
                try:
                    last = await self.get_review(organization_id, review_id)
                except ProoflineError as error:
                    if error.status == 0 and (_transport.remaining() or 0) <= 0:
                        break
                    raise
                if (_transport.remaining() or 0) <= 0:
                    break
                result = outcome(last, url, review_id=review_id, head_commit_sha=head_commit_sha)
                if on_poll is not None and (_transport.remaining() or 0) > 0:
                    snapshot = _snapshot_review(last)
                    if snapshot is not None and (_transport.remaining() or 0) > 0:
                        res = on_poll(snapshot)
                        try:
                            res_awaitable = isawaitable(res)
                        except Exception:
                            raise TypeError("Callbacks must return None or an awaitable.") from None
                        if res is not None and not res_awaitable:
                            raise TypeError("Callbacks must return None or an awaitable.")
                        if res_awaitable:
                            if res is async_current_task():
                                raise ValueError(
                                    "Callbacks cannot return the running polling task."
                                )

                            if iscoroutine(res) and getcoroutinestate(res) != CORO_CREATED:
                                raise ValueError("Callbacks must return unstarted coroutines.")
                            if isgenerator(res) and getgeneratorstate(res) != GEN_CREATED:
                                raise ValueError("Callbacks must return unstarted coroutines.")

                            if isinstance(res, (AsyncTask, AsyncFuture)):
                                is_done = (
                                    res.done() if hasattr(res, "done") else AsyncFuture.done(res)
                                )
                                if not is_done:
                                    try:
                                        res_loop = (
                                            res.get_loop()
                                            if hasattr(res, "get_loop")
                                            else AsyncFuture.get_loop(res)
                                        )
                                    except Exception:
                                        res_loop = None
                                    running_loop = async_get_running_loop()
                                    if res_loop is not running_loop or res_loop.is_closed():
                                        raise ValueError(
                                            "Pending callback futures must belong "
                                            "to the running event loop."
                                        )

                            remaining_budget = _transport.remaining()
                            if remaining_budget is not None and remaining_budget <= 0:
                                if iscoroutine(res) and getcoroutinestate(res) == CORO_CREATED:
                                    try:
                                        res.close()
                                    except BaseException:
                                        pass
                                elif isgenerator(res) and getgeneratorstate(res) == GEN_CREATED:
                                    try:
                                        res.close()
                                    except BaseException:
                                        pass
                                elif isinstance(res, (AsyncTask, AsyncFuture)):
                                    _detach_overdue_future(res)
                                if result is not None:
                                    return result
                                break

                            if isinstance(res, (AsyncTask, AsyncFuture)):
                                is_done = (
                                    res.done() if hasattr(res, "done") else AsyncFuture.done(res)
                                )
                                if is_done:
                                    if hasattr(res, "result"):
                                        res.result()
                                    else:
                                        AsyncFuture.result(res)
                                else:
                                    completion_fut = async_get_running_loop().create_future()
                                    completed_at: list[float] = []

                                    def _on_future_done(_: Any) -> None:
                                        completed_at.append(monotonic())
                                        if not completion_fut.done():
                                            completion_fut.set_result(None)

                                    if hasattr(res, "add_done_callback"):
                                        res.add_done_callback(_on_future_done)
                                    else:
                                        AsyncFuture.add_done_callback(res, _on_future_done)
                                    remaining_budget = _transport.remaining()
                                    if remaining_budget is not None and remaining_budget <= 0:
                                        _detach_overdue_future(res)
                                        if result is not None:
                                            return result
                                        break
                                    try:
                                        done, _ = await async_wait(
                                            {completion_fut}, timeout=remaining_budget
                                        )
                                    except BaseException:
                                        _detach_overdue_future(res)
                                        raise
                                    deadline_val = _transport.DEADLINE.get()
                                    cb_finished_in_budget = bool(completed_at) and (
                                        deadline_val is None or completed_at[0] <= deadline_val
                                    )
                                    if cb_finished_in_budget and completion_fut in done:
                                        if hasattr(res, "result"):
                                            res.result()
                                        else:
                                            AsyncFuture.result(res)
                                    else:
                                        _detach_overdue_future(res)
                                        if result is not None:
                                            return result
                                        break
                            else:
                                coro = res
                                completed_at = []
                                wrapper_started = False

                                async def _runner() -> None:
                                    nonlocal wrapper_started
                                    wrapper_started = True
                                    deadline_val = _transport.DEADLINE.get()
                                    if deadline_val is not None and monotonic() > deadline_val:
                                        if (
                                            iscoroutine(coro)
                                            and getcoroutinestate(coro) == CORO_CREATED
                                        ):
                                            try:
                                                coro.close()
                                            except BaseException:
                                                pass
                                        elif (
                                            isgenerator(coro)
                                            and getgeneratorstate(coro) == GEN_CREATED
                                        ):
                                            try:
                                                coro.close()
                                            except BaseException:
                                                pass
                                        return
                                    try:
                                        assert coro is not None
                                        await coro
                                    finally:
                                        completed_at.append(monotonic())

                                runner_coro = _runner()
                                try:
                                    task = async_create_task(runner_coro)
                                except BaseException:
                                    if (
                                        iscoroutine(runner_coro)
                                        and getcoroutinestate(runner_coro) == CORO_CREATED
                                    ):
                                        try:
                                            runner_coro.close()
                                        except BaseException:
                                            pass
                                    if iscoroutine(res) and getcoroutinestate(res) == CORO_CREATED:
                                        try:
                                            res.close()
                                        except BaseException:
                                            pass
                                    elif isgenerator(res) and getgeneratorstate(res) == GEN_CREATED:
                                        try:
                                            res.close()
                                        except BaseException:
                                            pass
                                    raise
                                task_completion_fut = async_get_running_loop().create_future()

                                def _on_task_done(t: Any) -> None:
                                    if not completed_at:
                                        try:
                                            is_canc = (
                                                t.cancelled() if hasattr(t, "cancelled") else False
                                            )
                                            if is_canc:
                                                completed_at.append(monotonic())
                                        except BaseException:
                                            pass
                                    if not task_completion_fut.done():
                                        task_completion_fut.set_result(None)

                                if hasattr(task, "add_done_callback"):
                                    task.add_done_callback(_on_task_done)
                                else:
                                    AsyncTask.add_done_callback(task, _on_task_done)

                                deadline_val = _transport.DEADLINE.get()
                                cb_finished_in_budget = bool(completed_at) and (
                                    deadline_val is None or completed_at[0] <= deadline_val
                                )
                                task_is_done = (
                                    task.done() if hasattr(task, "done") else AsyncFuture.done(task)
                                )
                                if task_is_done and cb_finished_in_budget:
                                    if not wrapper_started:
                                        if (
                                            iscoroutine(res)
                                            and getcoroutinestate(res) == CORO_CREATED
                                        ):
                                            try:
                                                res.close()
                                            except BaseException:
                                                pass
                                        elif (
                                            isgenerator(res)
                                            and getgeneratorstate(res) == GEN_CREATED
                                        ):
                                            try:
                                                res.close()
                                            except BaseException:
                                                pass
                                    if hasattr(task, "result"):
                                        task.result()
                                    else:
                                        AsyncTask.result(task)

                                remaining_budget = _transport.remaining()
                                if remaining_budget is not None and remaining_budget <= 0:
                                    _detach_overdue_task(task, res, wrapper_started)
                                    if result is not None:
                                        return result
                                    break
                                try:
                                    done, _ = await async_wait(
                                        {task_completion_fut}, timeout=remaining_budget
                                    )
                                except BaseException:
                                    _detach_overdue_task(task, res, wrapper_started)
                                    raise
                                deadline_val = _transport.DEADLINE.get()
                                cb_finished_in_budget = bool(completed_at) and (
                                    deadline_val is None or completed_at[0] <= deadline_val
                                )
                                task_is_done = (
                                    task.done() if hasattr(task, "done") else AsyncFuture.done(task)
                                )
                                if cb_finished_in_budget and (
                                    task_completion_fut in done or task_is_done
                                ):
                                    if not wrapper_started:
                                        if (
                                            iscoroutine(res)
                                            and getcoroutinestate(res) == CORO_CREATED
                                        ):
                                            try:
                                                res.close()
                                            except BaseException:
                                                pass
                                        elif (
                                            isgenerator(res)
                                            and getgeneratorstate(res) == GEN_CREATED
                                        ):
                                            try:
                                                res.close()
                                            except BaseException:
                                                pass
                                    if hasattr(task, "result"):
                                        task.result()
                                    else:
                                        AsyncTask.result(task)
                                else:
                                    _detach_overdue_task(task, res, wrapper_started)
                                    if result is not None:
                                        return result
                                    break
                if result is not None:
                    return result
                if (_transport.remaining() or 0) <= 0:
                    break
                await async_sleep(min(interval, _transport.remaining() or 0))
                interval = min(60, interval * 2)
            if result is not None:
                return result
            timed_out = outcome(last, url, "TIMED_OUT", head_commit_sha=head_commit_sha)
            return timed_out or ReviewOutcome("TIMED_OUT", url)
        finally:
            _transport.DEADLINE.reset(deadline)
