"""Small sync and async facades over the generated review operations."""

from __future__ import annotations

import array
import ctypes
import datetime
import math
import weakref
from asyncio import (
    CancelledError as AsyncCancelledError,
)
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
    isfuture as async_isfuture,
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
    ModuleType,
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
    if seen is None:
        seen = set()
    if id(val) in seen:
        return False
    seen.add(id(val))

    closure = getattr(val, "__closure__", None)
    if closure:
        return True

    defaults = getattr(val, "__defaults__", None)
    if defaults:
        for d in defaults:
            if not _is_immutable(d, seen):
                return True

    kwdefaults = getattr(val, "__kwdefaults__", None)
    if kwdefaults and isinstance(kwdefaults, dict):
        for d in kwdefaults.values():
            if not _is_immutable(d, seen):
                return True

    return False


_SAFE_BUILTIN_CLASSES: set[type] = {
    int,
    float,
    str,
    bool,
    bytes,
    list,
    dict,
    set,
    tuple,
    bytearray,
    deque,
    defaultdict,
    datetime.date,
    datetime.datetime,
    datetime.time,
    UUID,
}


def _is_identity_hashed(obj: Any) -> bool:
    try:
        return type(obj).__hash__ is object.__hash__
    except Exception:
        return False


def _deadline_expired() -> bool:
    budget = _transport.remaining()
    return budget is not None and budget <= 0


def _is_immutable(val: Any, seen: set[int] | None = None) -> bool:
    if val is None or val is UNSET:
        return True
    if isinstance(val, type):
        return val in _SAFE_BUILTIN_CLASSES
    t = type(val)
    if t in _IMMUTABLE_TYPES:
        return True
    if t is datetime.datetime:
        tz = val.tzinfo
        return tz is None or type(tz) is datetime.timezone
    if isinstance(val, (FunctionType, MethodType)):
        return False
    if isinstance(val, BuiltinFunctionType):
        if bool(getattr(val, "__dict__", None)):
            return False
        curr = getattr(val, "__self__", None)
        if curr is None:
            return True
        if isinstance(curr, ModuleType):
            return True
        if isinstance(curr, type):
            return curr in _SAFE_BUILTIN_CLASSES or curr is object
        local_seen = seen if seen is not None else set()
        val_id = id(val)
        if val_id in local_seen:
            return False
        local_seen.add(val_id)
        while curr is not None and isinstance(curr, (BuiltinFunctionType, MethodType)):
            curr_id = id(curr)
            if curr_id in local_seen:
                return False
            local_seen.add(curr_id)
            if _deadline_expired():
                return False
            curr = getattr(curr, "__self__", None)
        if curr is None:
            return True
        if isinstance(curr, ModuleType):
            return True
        if isinstance(curr, type):
            return curr in _SAFE_BUILTIN_CLASSES or curr is object
        return _is_immutable(curr, local_seen)
    return False


_SAFE_SPECIAL_ATTRS: set[str] = {
    "__abstractmethods__",
    "__annotations__",
    "__attrs_attrs__",
    "__attrs_own_setattr__",
    "__attrs_props__",
    "__class__",
    "__classcell__",
    "__dataclass_fields__",
    "__dataclass_params__",
    "__dict__",
    "__doc__",
    "__firstlineno__",
    "__hash__",
    "__match_args__",
    "__module__",
    "__mro_entries__",
    "__name__",
    "__orig_bases__",
    "__parameters__",
    "__pydantic_decorators__",
    "__pydantic_fields__",
    "__pydantic_generic_metadata__",
    "__qualname__",
    "__slots__",
    "__static_attributes__",
    "__subclasshook__",
    "__weakref__",
    "_fields",
    "_field_defaults",
    "_field_types",
}


def _has_mutable_class_attrs(cls: type) -> bool:
    for base in cls.__mro__:
        if base in _SAFE_BUILTIN_CLASSES or base is object:
            continue
        for name, attr in base.__dict__.items():
            if name in _SAFE_SPECIAL_ATTRS:
                continue
            if isinstance(attr, MemberDescriptorType) or type(attr).__name__ in (
                "member_descriptor",
                "getset_descriptor",
                "wrapper_descriptor",
                "method_descriptor",
                "slotwrapper",
                "classmethod_descriptor",
                "_tuplegetter",
            ):
                continue
            if isinstance(
                attr,
                (
                    FunctionType,
                    MethodType,
                    classmethod,
                    staticmethod,
                    property,
                    BuiltinFunctionType,
                ),
            ):
                continue
            if not _is_immutable(attr):
                return True
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

    return items


def _install_cloned_dict(
    val: Any,
    new_obj: Any,
    memo: dict[int, Any],
    stack: list[Any],
) -> None:
    if hasattr(val, "__dict__"):
        try:
            inst_dict = val.__dict__
            if isinstance(inst_dict, dict):
                dict_id = id(inst_dict)
                if dict_id in memo:
                    cloned_dict = memo[dict_id]
                else:
                    try:
                        cloned_dict = dict.__new__(type(inst_dict))
                        dict.clear(cloned_dict)
                    except Exception:
                        cloned_dict = {}
                    memo[dict_id] = cloned_dict
                    for k, v in inst_dict.items():
                        if _is_immutable(k) and _is_immutable(v):
                            if type(k) is bytes and len(k) > _MAX_SAFE_BUFFER_SIZE:
                                continue
                            if type(v) is bytes and len(v) > _MAX_SAFE_BUFFER_SIZE:
                                continue
                            cloned_dict[k] = v
                    stack.append((_DICT_EXPAND, cloned_dict, iter(inst_dict.items())))
                try:
                    new_obj.__dict__ = cloned_dict
                except AttributeError:
                    pass
        except Exception:
            pass


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
_UNRESOLVED_SLOT = object()
_MISSING = object()


class _Py_buffer(ctypes.Structure):
    _fields_ = [
        ("buf", ctypes.c_void_p),
        ("obj", ctypes.c_void_p),
        ("len", ctypes.c_ssize_t),
        ("itemsize", ctypes.c_ssize_t),
        ("readonly", ctypes.c_int),
        ("ndim", ctypes.c_int),
        ("format", ctypes.c_char_p),
        ("shape", ctypes.POINTER(ctypes.c_ssize_t)),
        ("strides", ctypes.POINTER(ctypes.c_ssize_t)),
        ("suboffsets", ctypes.POINTER(ctypes.c_ssize_t)),
        ("internal", ctypes.c_void_p),
    ]


_py_get_buffer = ctypes.pythonapi.PyObject_GetBuffer
_py_get_buffer.restype = ctypes.c_int
_py_get_buffer.argtypes = [ctypes.py_object, ctypes.POINTER(_Py_buffer), ctypes.c_int]

_py_release_buffer = ctypes.pythonapi.PyBuffer_Release
_py_release_buffer.restype = None
_py_release_buffer.argtypes = [ctypes.POINTER(_Py_buffer)]


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
    pending_frozenset_ids: set[int] = set()
    pending_assignments: dict[int, list[tuple[Any, Any, bool]]] = {}
    fallback_built_frozensets: list[tuple[Any, list[Any]]] = []
    deferred_attr_assignments: list[tuple[Any, tuple[Any, bool], Any]] = []
    populated_mutable_sets: list[tuple[Any, list[Any]]] = []

    def _collect_set_members(val: Any) -> list[Any] | None:
        if isinstance(val, set):
            if set.__len__(val) > _MAX_SAFE_BUFFER_SIZE:
                return None
        elif isinstance(val, frozenset):
            if frozenset.__len__(val) > _MAX_SAFE_BUFFER_SIZE:
                return None
        elif hasattr(val, "__len__") and len(val) > _MAX_SAFE_BUFFER_SIZE:
            return None
        members: list[Any] = []
        it = iter(val)
        batch_count = 0
        while True:
            try:
                m = next(it)
            except StopIteration:
                break
            members.append(m)
            if len(members) > _MAX_SAFE_BUFFER_SIZE:
                return None
            batch_count += 1
            if (batch_count & 63) == 0 and _deadline_expired():
                return None
        return members

    stack: list[Any] = [(_OBJ_EXPAND, root, iter(_get_obj_attrs(detail)))]
    _install_cloned_dict(detail, root, memo, stack)

    while stack:
        if _deadline_expired():
            return None

        task_type, target, it_or_key, *extra = stack.pop()

        if task_type == _ITEM_TASK:
            key, is_attr, val = it_or_key, extra[0], extra[1]
            if isinstance(
                val,
                (
                    FunctionType,
                    MethodType,
                    weakref.ref,
                    weakref.ProxyType,
                    weakref.CallableProxyType,
                ),
            ):
                raise TypeError(
                    f"Unsupported mutable value in review extension data: {type(val).__name__}"
                )
            if _is_immutable(val):
                if type(val) is bytes and len(val) > _MAX_SAFE_BUFFER_SIZE:
                    return None
                _assign_target(target, key, is_attr, val)
                continue
            val_id = id(val)
            if val_id in memo:
                _assign_target(target, key, is_attr, memo[val_id])
                continue
            if val_id in pending_frozenset_ids:
                if target is not None:
                    pending_assignments.setdefault(val_id, []).append((target, key, is_attr))
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
                if type(val) is not tuple and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
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
                        _install_cloned_dict(val, res_empty, memo, stack)
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
                if type(val) not in (dict, defaultdict) and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
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
                    _install_cloned_dict(val, new_dict, memo, stack)
                    stack.append((_OBJ_EXPAND, new_dict, iter(_get_obj_attrs(val))))
                stack.append((_DICT_EXPAND, new_dict, iter(val.items())))
            elif isinstance(val, list):
                if type(val) is not list and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
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
                    _install_cloned_dict(val, new_list, memo, stack)
                    stack.append((_OBJ_EXPAND, new_list, iter(_get_obj_attrs(val))))
            elif isinstance(val, set):
                if type(val) is not set and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
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
                    _install_cloned_dict(val, new_set, memo, stack)
                    stack.append((_OBJ_EXPAND, new_set, iter(_get_obj_attrs(val))))
                if set_len > 0:
                    orig_set_members = _collect_set_members(val)
                    if orig_set_members is None:
                        return None
                    deferred_set_insertions.append((new_set, val, orig_set_members))
                    stack.append((_SET_EXPAND, None, iter(val)))
            elif isinstance(val, frozenset):
                if type(val) is not frozenset and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
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
                        _install_cloned_dict(val, res_empty_fs, memo, stack)
                        stack.append((_OBJ_EXPAND, res_empty_fs, iter(_get_obj_attrs(val))))
                    _assign_target(target, key, is_attr, res_empty_fs)
                else:
                    orig_fs_members = _collect_set_members(val)
                    if orig_fs_members is None:
                        return None
                    pending_frozenset_ids.add(val_id)
                    deferred_frozenset_insertions.append(
                        (target, key, is_attr, val_id, val, orig_fs_members)
                    )
                    if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                        for slot_or_name, is_desc, attr_val in _get_obj_attrs(val):
                            if (
                                not _is_immutable(attr_val)
                                and id(attr_val) not in memo
                                and id(attr_val) not in pending_frozenset_ids
                            ):
                                stack.append((_ITEM_TASK, None, None, False, attr_val))
                    stack.append((_SET_EXPAND, None, iter(val)))
            elif isinstance(val, deque):
                if deque.__len__(val) > _MAX_SAFE_BUFFER_SIZE:
                    return None
                if type(val) is deque:
                    new_deque: deque[Any] = deque(maxlen=val.maxlen)
                else:
                    if type(val) is not deque and _has_mutable_class_attrs(type(val)):
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
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
                    _install_cloned_dict(val, new_deque, memo, stack)
                    stack.append((_OBJ_EXPAND, new_deque, iter(_get_obj_attrs(val))))
            elif isinstance(val, bytearray):
                if type(val) is not bytearray and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
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
                    _install_cloned_dict(val, resolved, memo, stack)
                    stack.append((_OBJ_EXPAND, resolved, iter(_get_obj_attrs(val))))
            elif isinstance(val, array.array):
                if type(val) is not array.array and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
                native_len: int | None = None
                try:
                    b_arr = _Py_buffer()
                    if _py_get_buffer(val, ctypes.byref(b_arr), 0x0118) == 0:
                        try:
                            native_len = b_arr.len
                        finally:
                            _py_release_buffer(ctypes.byref(b_arr))
                except BaseException:
                    pass
                if native_len is not None:
                    if native_len > _MAX_SAFE_BUFFER_SIZE:
                        return None
                else:
                    try:
                        arr_byte_count = array.array.buffer_info(val)[
                            1
                        ] * array.array.itemsize.__get__(val)
                    except BaseException:
                        arr_byte_count = val.buffer_info()[1] * val.itemsize
                    if arr_byte_count > _MAX_SAFE_BUFFER_SIZE:
                        return None
                try:
                    try:
                        native_tc = array.array.typecode.__get__(val)
                    except BaseException:
                        native_tc = val.typecode
                    resolved_arr = cast(Any, array.array).__new__(type(val), native_tc, val)
                except Exception as exc:
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    ) from exc
                clone_len: int | None = None
                try:
                    b_chk = _Py_buffer()
                    if _py_get_buffer(resolved_arr, ctypes.byref(b_chk), 0x0118) == 0:
                        try:
                            clone_len = b_chk.len
                        finally:
                            _py_release_buffer(ctypes.byref(b_chk))
                except BaseException:
                    pass
                if clone_len is not None:
                    if clone_len > _MAX_SAFE_BUFFER_SIZE:
                        return None
                else:
                    try:
                        arr_clone_bytes = array.array.buffer_info(resolved_arr)[
                            1
                        ] * array.array.itemsize.__get__(resolved_arr)
                    except BaseException:
                        arr_clone_bytes = resolved_arr.buffer_info()[1] * resolved_arr.itemsize
                    if arr_clone_bytes > _MAX_SAFE_BUFFER_SIZE:
                        return None
                memo[val_id] = resolved_arr
                _assign_target(target, key, is_attr, resolved_arr)
                if hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                    _install_cloned_dict(val, resolved_arr, memo, stack)
                    stack.append((_OBJ_EXPAND, resolved_arr, iter(_get_obj_attrs(val))))
            elif isinstance(val, memoryview):
                if val.nbytes > _MAX_SAFE_BUFFER_SIZE:
                    return None
                exporter = getattr(val, "obj", None)
                if exporter is not None:
                    try:
                        b_exp_check = _Py_buffer()
                        if _py_get_buffer(exporter, ctypes.byref(b_exp_check), 0x0118) == 0:
                            try:
                                if b_exp_check.len > _MAX_SAFE_BUFFER_SIZE:
                                    return None
                            finally:
                                _py_release_buffer(ctypes.byref(b_exp_check))
                    except BaseException:
                        pass
                resolved_mv: Any
                if isinstance(exporter, (bytearray, array.array, bytes)):
                    if type(exporter) not in (
                        bytearray,
                        array.array,
                        bytes,
                    ) and _has_mutable_class_attrs(type(exporter)):
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(exporter).__name__}"
                        )
                    exp_id = id(exporter)
                    if exp_id in memo:
                        cloned_exporter = memo[exp_id]
                    else:
                        exp_native_len: int | None = None
                        try:
                            b_chk2 = _Py_buffer()
                            if _py_get_buffer(exporter, ctypes.byref(b_chk2), 0x0118) == 0:
                                try:
                                    exp_native_len = b_chk2.len
                                finally:
                                    _py_release_buffer(ctypes.byref(b_chk2))
                        except BaseException:
                            pass
                        if exp_native_len is not None:
                            if exp_native_len > _MAX_SAFE_BUFFER_SIZE:
                                return None
                        else:
                            if isinstance(exporter, bytearray):
                                exp_bytes_len = bytearray.__len__(exporter)
                            elif isinstance(exporter, bytes):
                                exp_bytes_len = bytes.__len__(exporter)
                            else:
                                exp_bytes_len = array.array.buffer_info(exporter)[
                                    1
                                ] * array.array.itemsize.__get__(exporter)
                            if exp_bytes_len > _MAX_SAFE_BUFFER_SIZE:
                                return None
                        try:
                            if isinstance(exporter, bytes):
                                if type(exporter) is bytes:
                                    cloned_exporter = bytes(exporter)
                                else:
                                    mv_exp = memoryview(exporter)
                                    if mv_exp.nbytes > _MAX_SAFE_BUFFER_SIZE:
                                        return None
                                    raw_exp = bytes(mv_exp)
                                    cloned_exporter = bytes.__new__(type(exporter), raw_exp)
                            elif isinstance(exporter, bytearray):
                                cloned_exporter = bytearray.__new__(type(exporter))
                                bytearray.__init__(cloned_exporter, exporter)
                            else:
                                try:
                                    native_exp_tc = array.array.typecode.__get__(exporter)
                                except BaseException:
                                    native_exp_tc = exporter.typecode
                                cloned_exporter = cast(Any, array.array).__new__(
                                    type(exporter), native_exp_tc, exporter
                                )
                                clone_exp_len: int | None = None
                                try:
                                    b_chk = _Py_buffer()
                                    if (
                                        _py_get_buffer(cloned_exporter, ctypes.byref(b_chk), 0x0118)
                                        == 0
                                    ):
                                        try:
                                            clone_exp_len = b_chk.len
                                        finally:
                                            _py_release_buffer(ctypes.byref(b_chk))
                                except BaseException:
                                    pass
                                if clone_exp_len is not None:
                                    if clone_exp_len > _MAX_SAFE_BUFFER_SIZE:
                                        return None
                                else:
                                    try:
                                        arr_exp_bytes = array.array.buffer_info(cloned_exporter)[
                                            1
                                        ] * array.array.itemsize.__get__(cloned_exporter)
                                    except BaseException:
                                        arr_exp_bytes = (
                                            cloned_exporter.buffer_info()[1]
                                            * cloned_exporter.itemsize
                                        )
                                    if arr_exp_bytes > _MAX_SAFE_BUFFER_SIZE:
                                        return None
                        except Exception as exc:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(exporter).__name__}"
                            ) from exc
                        memo[exp_id] = cloned_exporter
                        if hasattr(exporter, "__dict__") or hasattr(exporter, "__slots__"):
                            _install_cloned_dict(exporter, cloned_exporter, memo, stack)
                            stack.append(
                                (_OBJ_EXPAND, cloned_exporter, iter(_get_obj_attrs(exporter)))
                            )
                    b_val = _Py_buffer()
                    b_exp = _Py_buffer()
                    if _py_get_buffer(val, ctypes.byref(b_val), 0x0118) != 0:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
                    try:
                        if _py_get_buffer(exporter, ctypes.byref(b_exp), 0x0118) != 0:
                            raise TypeError(
                                "Unsupported mutable value in review extension data: "
                                f"{type(exporter).__name__}"
                            )
                        try:
                            offset = b_val.buf - b_exp.buf
                        finally:
                            _py_release_buffer(ctypes.byref(b_exp))
                    finally:
                        _py_release_buffer(ctypes.byref(b_val))
                    base_bytes = cast(Any, memoryview(cloned_exporter)).cast("B")
                    val_strides = val.strides
                    val_shape = val.shape
                    if val.ndim == 1 and val_shape is not None and val_strides is not None:
                        shape = val_shape[0]
                        itemsize = val.itemsize
                        stride = val_strides[0]
                        elem_stride = stride // itemsize
                        if shape == 0:
                            casted = cast(Any, base_bytes[0:0]).cast(val.format)
                            resolved_mv = casted[::elem_stride]
                        elif stride >= 0:
                            byte_len = (shape - 1) * stride + itemsize
                            byte_slice = base_bytes[offset : offset + byte_len]
                            casted = cast(Any, byte_slice).cast(val.format)
                            resolved_mv = casted[::elem_stride]
                        else:
                            lowest_byte = offset + (shape - 1) * stride
                            byte_len = (shape - 1) * abs(stride) + itemsize
                            byte_slice = base_bytes[lowest_byte : lowest_byte + byte_len]
                            casted = cast(Any, byte_slice).cast(val.format)
                            start_elem = (shape - 1) * (-elem_stride)
                            resolved_mv = casted[start_elem:None:elem_stride]
                    elif val.ndim == 0:
                        resolved_mv = cast(Any, base_bytes[offset : offset + val.itemsize]).cast(
                            val.format, shape=()
                        )
                    elif val.c_contiguous:
                        resolved_mv = cast(Any, base_bytes[offset : offset + val.nbytes]).cast(
                            val.format, shape=val.shape
                        )
                    else:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
                else:
                    if not val.c_contiguous:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        )
                    if exporter is not None:
                        exp_id = id(exporter)
                        if exp_id in memo:
                            cloned_buf = memo[exp_id]
                        else:
                            exp_readonly = False
                            try:
                                b_exp_chk = _Py_buffer()
                                if _py_get_buffer(exporter, ctypes.byref(b_exp_chk), 0x0118) == 0:
                                    try:
                                        exp_readonly = bool(b_exp_chk.readonly)
                                    finally:
                                        _py_release_buffer(ctypes.byref(b_exp_chk))
                                else:
                                    exp_readonly = getattr(
                                        exporter, "readonly", False
                                    ) or isinstance(exporter, (bytes, tuple))
                            except BaseException:
                                exp_readonly = getattr(exporter, "readonly", False) or isinstance(
                                    exporter, (bytes, tuple)
                                )
                            if exp_readonly:
                                cloned_buf = bytes(exporter)
                            else:
                                cloned_buf = bytearray(exporter)
                            memo[exp_id] = cloned_buf
                        offset = 0
                        try:
                            b_val = _Py_buffer()
                            b_exp = _Py_buffer()
                            if _py_get_buffer(val, ctypes.byref(b_val), 0x0118) == 0:
                                try:
                                    if _py_get_buffer(exporter, ctypes.byref(b_exp), 0x0118) == 0:
                                        try:
                                            offset = b_val.buf - b_exp.buf
                                        finally:
                                            _py_release_buffer(ctypes.byref(b_exp))
                                finally:
                                    _py_release_buffer(ctypes.byref(b_val))
                        except BaseException:
                            pass
                        resolved_mv = memoryview(cloned_buf)[offset : offset + val.nbytes]
                    else:
                        if val.readonly:
                            resolved_mv = memoryview(bytes(val))
                        else:
                            resolved_mv = memoryview(bytearray(val))
                    val_strides = val.strides
                    val_shape = val.shape
                    try:
                        if val.ndim == 1 and val_shape is not None and val_strides is not None:
                            shape = val_shape[0]
                            itemsize = val.itemsize
                            stride = val_strides[0]
                            elem_stride = stride // itemsize if itemsize > 0 else 1
                            if shape == 0:
                                casted = cast(Any, resolved_mv).cast(val.format)
                                resolved_mv = casted[::elem_stride]
                            elif val.format != "B":
                                resolved_mv = cast(Any, resolved_mv).cast(val.format)
                        elif val.ndim == 0:
                            resolved_mv = cast(Any, resolved_mv).cast(val.format, shape=())
                        elif val.format != "B" or (val.ndim > 1 and val.shape != resolved_mv.shape):
                            resolved_mv = cast(Any, resolved_mv).cast(val.format, shape=val.shape)
                    except Exception as exc:
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(val).__name__}"
                        ) from exc
                if val.readonly:
                    resolved_mv = resolved_mv.toreadonly()
                memo[val_id] = resolved_mv
                _assign_target(target, key, is_attr, resolved_mv)
            elif isinstance(val, datetime.datetime):
                if type(val) is not datetime.datetime and _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
                tz = val.tzinfo
                copied_tz = tz
                if tz is not None and type(tz) is not datetime.timezone:
                    if _has_mutable_class_attrs(type(tz)):
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(tz).__name__}"
                        )
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
                            _install_cloned_dict(tz, copied_tz, memo, stack)
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
                        _install_cloned_dict(val, new_dt, memo, stack)
                        stack.append((_OBJ_EXPAND, new_dt, iter(_get_obj_attrs(val))))
            elif hasattr(val, "__dict__") or hasattr(val, "__slots__"):
                if _has_mutable_class_attrs(type(val)):
                    raise TypeError(
                        f"Unsupported mutable value in review extension data: {type(val).__name__}"
                    )
                new_obj: Any
                try:
                    if isinstance(val, str):
                        new_obj = str.__new__(type(val), val)
                    elif isinstance(val, bytes):
                        mv_bytes = memoryview(val)
                        if mv_bytes.nbytes > _MAX_SAFE_BUFFER_SIZE:
                            return None
                        raw_bytes = bytes(mv_bytes)
                        new_obj = bytes.__new__(type(val), raw_bytes)
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
                _install_cloned_dict(val, new_obj, memo, stack)
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
                if (type(k) is bytes and len(k) > _MAX_SAFE_BUFFER_SIZE) or (
                    type(v) is bytes and len(v) > _MAX_SAFE_BUFFER_SIZE
                ):
                    return None
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
                if type(m) is bytes and len(m) > _MAX_SAFE_BUFFER_SIZE:
                    return None
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
                if type(v) is bytes and len(v) > _MAX_SAFE_BUFFER_SIZE:
                    return None
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
                if type(attr_val) is bytes and len(attr_val) > _MAX_SAFE_BUFFER_SIZE:
                    return None
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
                if type(v) is bytes and len(v) > _MAX_SAFE_BUFFER_SIZE:
                    return None
                if _is_immutable(v):
                    temp_list.append(v)
                elif id(v) in memo:
                    temp_list.append(memo[id(v)])
                else:
                    idx = len(temp_list)
                    temp_list.append(_UNRESOLVED_SLOT)
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
            if any(x is _UNRESOLVED_SLOT for x in temp_list):
                deferred_tuple_finalizations.append(
                    (target, key, is_attr, val_id, orig_val, temp_list)
                )
                if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                    for slot_or_name, is_desc, attr_val in _get_obj_attrs(orig_val):
                        if not _is_immutable(attr_val) and id(attr_val) not in memo:
                            stack.append((_ITEM_TASK, None, None, False, attr_val))
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
                    if _has_mutable_class_attrs(type(orig_val)):
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(orig_val).__name__}"
                        )
                    try:
                        orig_cls: Any = type(orig_val)
                        res_tuple = tuple.__new__(orig_cls, temp_list)
                    except Exception:
                        return None
                memo[val_id] = res_tuple
            if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                _install_cloned_dict(orig_val, res_tuple, memo, stack)
                stack.append((_OBJ_EXPAND, res_tuple, iter(_get_obj_attrs(orig_val))))
            _assign_target(target, key, is_attr, res_tuple)

    if _deadline_expired():
        return None

    dict_ordered_entries: dict[int, list[tuple[Any, Any]]] = {}
    dict_targets: dict[int, Any] = {}
    dict_next_index: dict[int, int] = {}

    for count, (target_dict, orig_k, orig_v) in enumerate(deferred_dict_insertions):
        if (count & 63) == 0 and _deadline_expired():
            return None
        td_id = id(target_dict)
        if td_id not in dict_ordered_entries:
            dict_ordered_entries[td_id] = []
            dict_targets[td_id] = target_dict
            dict_next_index[td_id] = 0
        dict_ordered_entries[td_id].append((orig_k, orig_v))

    pending_frozensets: list[Any] = deferred_frozenset_insertions

    def _is_member_state_populated(m_clone: Any, current_target_id: int | None = None) -> bool:
        if _is_immutable(m_clone):
            return True
        if _is_identity_hashed(m_clone):
            return True
        visited: set[int] = set()
        root_in_custom = not _is_identity_hashed(m_clone) and type(m_clone) not in (
            tuple,
            frozenset,
        )
        stack_nodes: list[tuple[Any, bool]] = [(m_clone, root_in_custom)]
        container_ids: set[int] = set()
        while stack_nodes:
            cur, in_custom = stack_nodes.pop()
            if _is_immutable(cur):
                continue
            cid = id(cur)
            if cid in visited:
                continue
            visited.add(cid)
            container_ids.add(cid)
            if (
                not in_custom
                and not _is_identity_hashed(cur)
                and type(cur)
                not in (
                    tuple,
                    frozenset,
                )
            ):
                in_custom = True
            if in_custom:
                if hasattr(cur, "__dict__") and isinstance(cur.__dict__, dict):
                    stack_nodes.append((cur.__dict__, True))
                if hasattr(cur, "__slots__") or hasattr(cur, "__dict__"):
                    for _, _, slot_val in _get_obj_attrs(cur):
                        if not _is_immutable(slot_val):
                            stack_nodes.append((slot_val, True))
                if isinstance(cur, dict):
                    for k, v in cur.items():
                        if not _is_immutable(k):
                            stack_nodes.append((k, True))
                        if not _is_immutable(v):
                            stack_nodes.append((v, True))
                elif isinstance(cur, tuple):
                    for item in cur:
                        if not _is_immutable(item):
                            stack_nodes.append((item, True))
                elif isinstance(cur, (list, set, frozenset, deque)):
                    for item in cur:
                        if not _is_immutable(item):
                            stack_nodes.append((item, True))
            else:
                if isinstance(cur, (tuple, frozenset)):
                    for item in cur:
                        if _is_immutable(item):
                            continue
                        if _is_identity_hashed(item):
                            continue
                        item_is_custom = type(item) not in (tuple, frozenset)
                        stack_nodes.append((item, item_is_custom))

        for target, _, _, _, _, _ in deferred_tuple_finalizations:
            if id(target) in container_ids:
                if id(target) == current_target_id:
                    try:
                        hash(m_clone)
                        _ = m_clone == m_clone
                        continue
                    except Exception:
                        return False
                return False
        for target, _, _, _, _, _ in pending_frozensets:
            if id(target) in container_ids:
                if id(target) == current_target_id:
                    try:
                        hash(m_clone)
                        _ = m_clone == m_clone
                        continue
                    except Exception:
                        return False
                return False
        for s, _, _ in deferred_set_insertions:
            if id(s) in container_ids:
                if id(s) == current_target_id:
                    try:
                        hash(m_clone)
                        _ = m_clone == m_clone
                        continue
                    except Exception:
                        return False
                return False
        for td_id, entries in dict_ordered_entries.items():
            if td_id in container_ids:
                if td_id == current_target_id:
                    try:
                        hash(m_clone)
                        _ = m_clone == m_clone
                        continue
                    except Exception:
                        return False
                if dict_next_index[td_id] < len(entries):
                    return False
        return True

    def _flush_pending_structures() -> None:
        nonlocal deferred_tuple_finalizations, deferred_set_insertions, deferred_attr_assignments
        changed = True
        while changed:
            if _deadline_expired():
                return
            changed = False
            if deferred_tuple_finalizations:
                still_tuples = []
                for (
                    target,
                    key,
                    is_attr,
                    val_id,
                    orig_val,
                    temp_list,
                ) in deferred_tuple_finalizations:
                    elements_ready = not any(x is _UNRESOLVED_SLOT for x in temp_list)
                    attrs_ready = True
                    if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                        for _, _, attr_val in _get_obj_attrs(orig_val):
                            if not _is_immutable(attr_val) and id(attr_val) not in memo:
                                attrs_ready = False
                                break
                    if elements_ready and attrs_ready:
                        if val_id in memo:
                            res_tuple = memo[val_id]
                        else:
                            if type(orig_val) is tuple:
                                res_tuple = tuple(temp_list)
                            else:
                                if _has_mutable_class_attrs(type(orig_val)):
                                    raise TypeError(
                                        "Unsupported mutable value in review extension data: "
                                        f"{type(orig_val).__name__}"
                                    )
                                try:
                                    orig_tuple_cls: Any = type(orig_val)
                                    res_tuple = tuple.__new__(orig_tuple_cls, temp_list)
                                except Exception:
                                    continue
                            memo[val_id] = res_tuple
                        if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                            for slot_or_name, is_desc, attr_val in _get_obj_attrs(orig_val):
                                val_to_set = (
                                    attr_val if _is_immutable(attr_val) else memo[id(attr_val)]
                                )
                                _assign_target(res_tuple, (slot_or_name, is_desc), True, val_to_set)
                        _assign_target(target, key, is_attr, res_tuple)
                        changed = True
                    else:
                        still_tuples.append((target, key, is_attr, val_id, orig_val, temp_list))
                deferred_tuple_finalizations = still_tuples

            if deferred_set_insertions:
                still_sets = []
                for s, orig_val, orig_members in deferred_set_insertions:
                    if _deadline_expired():
                        return
                    members_ready = True
                    for m_idx, m in enumerate(orig_members):
                        if (m_idx & 63) == 0 and _deadline_expired():
                            return
                        if not (_is_immutable(m) or id(m) in memo):
                            members_ready = False
                            break
                    if not members_ready:
                        still_sets.append((s, orig_val, orig_members))
                        continue
                    resolved_members = []
                    for m_idx, m in enumerate(orig_members):
                        if (m_idx & 63) == 0 and _deadline_expired():
                            return
                        rm = m if _is_immutable(m) else memo[id(m)]
                        resolved_members.append(rm)
                        if not _is_member_state_populated(rm, current_target_id=id(s)):
                            members_ready = False
                            break
                    if not members_ready:
                        still_sets.append((s, orig_val, orig_members))
                        continue
                    for ins_idx in range(0, len(resolved_members), 64):
                        if ins_idx > 0 and _deadline_expired():
                            return
                        chunk = resolved_members[ins_idx : ins_idx + 64]
                        set.update(s, chunk)
                    if _deadline_expired():
                        return
                    if set.__len__(s) != len(orig_members):
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(orig_val).__name__}"
                        )
                    populated_mutable_sets.append((s, resolved_members))
                    changed = True
                deferred_set_insertions = still_sets

            op_count = 0
            for td_id, entries in dict_ordered_entries.items():
                target_dict = dict_targets[td_id]
                idx = dict_next_index[td_id]
                while idx < len(entries):
                    op_count += 1
                    if (op_count & 63) == 0 and _deadline_expired():
                        return
                    orig_k, orig_v = entries[idx]
                    k_ready = _is_immutable(orig_k) or id(orig_k) in memo
                    v_ready = _is_immutable(orig_v) or id(orig_v) in memo
                    if k_ready and v_ready:
                        k = orig_k if _is_immutable(orig_k) else memo[id(orig_k)]
                        v = orig_v if _is_immutable(orig_v) else memo[id(orig_v)]
                        if not _is_member_state_populated(k, current_target_id=td_id):
                            break
                        target_dict[k] = v
                        idx += 1
                        changed = True
                    else:
                        break
                dict_next_index[td_id] = idx

            if deferred_attr_assignments:
                still_attrs = []
                for res_obj, key_desc, orig_attr in deferred_attr_assignments:
                    if _is_immutable(orig_attr) or id(orig_attr) in memo:
                        val_to_set = orig_attr if _is_immutable(orig_attr) else memo[id(orig_attr)]
                        _assign_target(res_obj, key_desc, True, val_to_set)
                        changed = True
                    else:
                        still_attrs.append((res_obj, key_desc, orig_attr))
                deferred_attr_assignments = still_attrs

    _flush_pending_structures()
    if _deadline_expired():
        return None

    pending_frozensets = deferred_frozenset_insertions
    while pending_frozensets:
        if _deadline_expired():
            return None
        progress = False
        remaining_frozensets = []
        for target, key, is_attr, val_id, orig_val, orig_members in pending_frozensets:
            if val_id in memo:
                _assign_target(target, key, is_attr, memo[val_id])
                progress = True
                continue
            members_ready = True
            for m_idx, m in enumerate(orig_members):
                if (m_idx & 63) == 0 and _deadline_expired():
                    return None
                if not (_is_immutable(m) or id(m) in memo):
                    members_ready = False
                    break
            attrs_ready = True
            if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                for _, _, attr_val in _get_obj_attrs(orig_val):
                    if (
                        not _is_immutable(attr_val)
                        and id(attr_val) not in memo
                        and id(attr_val) != val_id
                    ):
                        attrs_ready = False
                        break
            if members_ready and attrs_ready:
                resolved_members = []
                for m_idx, m in enumerate(orig_members):
                    if (m_idx & 63) == 0 and _deadline_expired():
                        return None
                    rm = m if _is_immutable(m) else memo[id(m)]
                    resolved_members.append(rm)
                    if not _is_member_state_populated(rm, current_target_id=id(target)):
                        members_ready = False
                        break
                if not members_ready:
                    remaining_frozensets.append(
                        (target, key, is_attr, val_id, orig_val, orig_members)
                    )
                    continue
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
                    if frozenset.__len__(res_set) != len(orig_members):
                        raise TypeError(
                            "Unsupported mutable value in review extension data: "
                            f"{type(orig_val).__name__}"
                        )
                memo[val_id] = res_set
                pending_frozenset_ids.discard(val_id)
                if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                    for slot_or_name, is_desc, attr_val in _get_obj_attrs(orig_val):
                        if _is_immutable(attr_val):
                            _assign_target(res_set, (slot_or_name, is_desc), True, attr_val)
                        elif id(attr_val) in memo:
                            _assign_target(
                                res_set, (slot_or_name, is_desc), True, memo[id(attr_val)]
                            )
                        else:
                            deferred_attr_assignments.append(
                                (res_set, (slot_or_name, is_desc), attr_val)
                            )
                _assign_target(target, key, is_attr, res_set)
                for p_target, p_key, p_is_attr in pending_assignments.pop(val_id, []):
                    _assign_target(p_target, p_key, p_is_attr, res_set)
                progress = True
                _flush_pending_structures()
            else:
                remaining_frozensets.append((target, key, is_attr, val_id, orig_val, orig_members))

        pending_frozensets = remaining_frozensets

        if not progress and pending_frozensets:
            resolved_any = False
            still_pending = []
            for target, key, is_attr, val_id, orig_val, orig_members in pending_frozensets:
                can_resolve = True
                resolved_members = []
                for m in orig_members:
                    if _is_immutable(m):
                        rm = m
                    else:
                        rm = memo.get(id(m), _MISSING)
                        if rm is _MISSING:
                            can_resolve = False
                            break
                    try:
                        hash(rm)
                        _ = rm == rm
                    except Exception:
                        can_resolve = False
                        break
                    resolved_members.append(rm)
                if can_resolve:
                    if type(orig_val) is frozenset:
                        res_set = frozenset(resolved_members)
                    else:
                        res_set = frozenset.__new__(type(orig_val), resolved_members)
                    memo[val_id] = res_set
                    pending_frozenset_ids.discard(val_id)
                    fallback_built_frozensets.append((res_set, resolved_members))
                    if hasattr(orig_val, "__dict__") or hasattr(orig_val, "__slots__"):
                        for slot_or_name, is_desc, attr_val in _get_obj_attrs(orig_val):
                            if _is_immutable(attr_val):
                                _assign_target(res_set, (slot_or_name, is_desc), True, attr_val)
                            elif id(attr_val) in memo:
                                _assign_target(
                                    res_set, (slot_or_name, is_desc), True, memo[id(attr_val)]
                                )
                            else:
                                deferred_attr_assignments.append(
                                    (res_set, (slot_or_name, is_desc), attr_val)
                                )
                    _assign_target(target, key, is_attr, res_set)
                    for p_target, p_key, p_is_attr in pending_assignments.pop(val_id, []):
                        _assign_target(p_target, p_key, p_is_attr, res_set)
                    resolved_any = True
                else:
                    still_pending.append((target, key, is_attr, val_id, orig_val, orig_members))
            if resolved_any:
                pending_frozensets = still_pending
                _flush_pending_structures()
                continue
            raise TypeError("Unsupported cyclic reference in frozenset")

    _flush_pending_structures()
    if _deadline_expired():
        return None
    for fb_set, fb_members in fallback_built_frozensets:
        try:
            for rm in fb_members:
                if rm not in fb_set:
                    raise TypeError("Member lookup failed in fallback frozenset")
        except TypeError:
            raise
        except Exception as exc:
            raise TypeError("Member lookup failed in fallback frozenset") from exc
    if deferred_set_insertions:
        raise TypeError("Unsupported cyclic reference in set")
    for td_id, entries in dict_ordered_entries.items():
        if dict_next_index[td_id] < len(entries):
            raise TypeError("Unsupported cyclic reference in dict")
        target_dict = dict_targets[td_id]
        for orig_k, _ in entries:
            if _deadline_expired():
                return None
            k = orig_k if _is_immutable(orig_k) else memo.get(id(orig_k), orig_k)
            try:
                if k not in target_dict:
                    return None
            except Exception:
                return None
    for s, members in populated_mutable_sets:
        for rm in members:
            if _deadline_expired():
                return None
            try:
                if rm not in s:
                    return None
            except Exception:
                return None
    if deferred_tuple_finalizations:
        raise TypeError("Unsupported cyclic reference in tuple")
    if deferred_attr_assignments:
        raise TypeError("Unsupported cyclic reference in attributes")
    return root


_DETACHED_TASKS: weakref.WeakValueDictionary[int, Any] = weakref.WeakValueDictionary()
_DETACHED_FUTURES: dict[int, Any] = {}


def _safe_cancel_target(target: Any) -> None:
    try:
        target.cancel()
    except BaseException:
        pass


def _ensure_loop_close_hooked(loop: Any) -> bool:
    hook_installed = getattr(loop, "_proofline_close_hooked", False)
    if hook_installed:
        return True
    try:
        orig_loop_close = loop.close

        def _drain_exception(target: Any) -> None:
            try:
                is_done = target.done() if hasattr(target, "done") else AsyncFuture.done(target)
                is_canc = (
                    target.cancelled()
                    if hasattr(target, "cancelled")
                    else AsyncFuture.cancelled(target)
                )
                if is_done and not is_canc:
                    if hasattr(target, "exception"):
                        target.exception()
                    else:
                        AsyncFuture.exception(target)
            except BaseException:
                pass

        def _hooked_loop_close(*args: Any, **kwargs: Any) -> Any:
            close_res = orig_loop_close(*args, **kwargs)
            l_futs = getattr(loop, "_proofline_detached_futures", None)
            if l_futs is not None:
                for fid, f in list(l_futs.items()):
                    _drain_exception(f)
                    _DETACHED_FUTURES.pop(fid, None)
                l_futs.clear()
            l_tasks = getattr(loop, "_proofline_detached_tasks", None)
            if l_tasks is not None:
                for tid, t in list(l_tasks.items()):
                    _drain_exception(t)
                    _DETACHED_TASKS.pop(tid, None)
                l_tasks.clear()
            for fid, f in list(_DETACHED_FUTURES.items()):
                f_loop = None
                try:
                    f_loop = f.get_loop() if hasattr(f, "get_loop") else AsyncFuture.get_loop(f)
                except BaseException:
                    f_loop = getattr(f, "_loop", None)
                if f_loop is loop:
                    _drain_exception(f)
                    _DETACHED_FUTURES.pop(fid, None)
            for tid, t in list(_DETACHED_TASKS.items()):
                t_loop = None
                try:
                    t_loop = t.get_loop() if hasattr(t, "get_loop") else AsyncTask.get_loop(t)
                except BaseException:
                    t_loop = getattr(t, "_loop", None)
                if t_loop is loop:
                    _drain_exception(t)
                    _DETACHED_TASKS.pop(tid, None)
            return close_res

        loop.close = _hooked_loop_close
        setattr(loop, "_proofline_close_hooked", True)
        return True
    except BaseException:
        return False


def _detach_overdue_future(fut: Any) -> None:
    if hasattr(fut, "get_coro"):
        _detach_overdue_task(fut)
        return
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
        loop_futures = getattr(loop, "_proofline_detached_futures", None)
        if loop_futures is None:
            loop_futures = {}
            try:
                setattr(loop, "_proofline_detached_futures", loop_futures)
            except Exception:
                pass
        if loop_futures is not None:
            loop_futures[fut_id] = fut

        hook_installed = _ensure_loop_close_hooked(loop)

        if hook_installed:
            try:
                _DETACHED_FUTURES[fut_id] = fut
            except (TypeError, BaseException):
                pass

        def _on_detached_fut_done(t: Any) -> None:
            _DETACHED_FUTURES.pop(fut_id, None)
            if loop is not None:
                l_futs = getattr(loop, "_proofline_detached_futures", None)
                if l_futs is not None:
                    l_futs.pop(fut_id, None)
                    l_futs.pop(id(t), None)
            try:
                is_canc = t.cancelled() if hasattr(t, "cancelled") else False
                if not is_canc:
                    if hasattr(t, "exception"):
                        t.exception()
            except BaseException:
                pass

        registered = False
        if hasattr(fut, "add_done_callback"):
            try:
                fut.add_done_callback(_on_detached_fut_done)
                registered = True
            except BaseException:
                pass
        if not registered:
            try:
                AsyncFuture.add_done_callback(fut, _on_detached_fut_done)
                registered = True
            except BaseException:
                pass
        if not registered:
            try:
                loop = async_get_running_loop()

                async def _observe_fut() -> None:
                    try:
                        await fut
                    except BaseException:
                        pass
                    finally:
                        _DETACHED_FUTURES.pop(fut_id, None)

                obs_fut = loop.create_task(_observe_fut())
                obs_fut.add_done_callback(lambda _: None)
            except BaseException:
                _DETACHED_FUTURES.pop(fut_id, None)
    except BaseException:
        pass


def _safe_close(obj: Any) -> None:
    try:
        closer = getattr(obj, "close", None)
        if callable(closer):
            closer()
    except BaseException:
        pass


def _cleanup_discarded_awaitable(res: Any, waiter_task: Any = None) -> None:
    if res is None:
        return
    if async_isfuture(res):
        if waiter_task is None or res is not waiter_task:
            _detach_overdue_future(res)
        return
    if iscoroutine(res):
        try:
            if getcoroutinestate(res) == CORO_CREATED:
                res.close()
        except BaseException:
            pass
        return
    if isgenerator(res):
        try:
            if getgeneratorstate(res) == GEN_CREATED:
                res.close()
        except BaseException:
            pass
        return
    try:
        if getattr(res, "_proofline_cleaned_up", False):
            return
        setattr(res, "_proofline_cleaned_up", True)
    except BaseException:
        pass
    _safe_close(res)


def _detach_overdue_task(
    task: Any,
    res: Any = None,
    wrapper_started: bool = True,
) -> None:
    try:
        is_done = task.done() if hasattr(task, "done") else False
    except BaseException:
        is_done = False

    if is_done:
        try:
            is_canc = task.cancelled() if hasattr(task, "cancelled") else False
            if not is_canc and hasattr(task, "exception"):
                task.exception()
        except BaseException:
            pass
        if not wrapper_started:
            try:
                task.cancel()
            except BaseException:
                pass
            _cleanup_discarded_awaitable(res)
        return

    try:
        running_loop = async_get_running_loop()
    except Exception:
        running_loop = None

    try:
        loop = task.get_loop() if hasattr(task, "get_loop") else running_loop
    except Exception:
        loop = running_loop

    if running_loop is not None and loop is not running_loop:
        return
    if loop is None or loop.is_closed():
        return

    try:
        loop = task.get_loop() if hasattr(task, "get_loop") else async_get_running_loop()
    except Exception:
        try:
            loop = async_get_running_loop()
        except Exception:
            loop = None

    task_id = id(task)
    hook_installed = False
    if loop is not None and not loop.is_closed():
        loop_tasks = getattr(loop, "_proofline_detached_tasks", None)
        if loop_tasks is None:
            loop_tasks = {}
            try:
                setattr(loop, "_proofline_detached_tasks", loop_tasks)
            except Exception:
                pass
        if loop_tasks is not None:
            loop_tasks[task_id] = task

        hook_installed = _ensure_loop_close_hooked(loop)

    if hook_installed:
        try:
            _DETACHED_TASKS[task_id] = task
        except (TypeError, BaseException):
            pass

    def _on_detached_task_done(t: Any) -> None:
        _DETACHED_TASKS.pop(task_id, None)
        if loop is not None:
            loop_tasks = getattr(loop, "_proofline_detached_tasks", None)
            if loop_tasks is not None:
                loop_tasks.pop(task_id, None)
                loop_tasks.pop(id(t), None)
        try:
            is_canc = t.cancelled() if hasattr(t, "cancelled") else False
            if not is_canc:
                if hasattr(t, "exception"):
                    t.exception()
        except BaseException:
            pass

    registered = False
    if hasattr(task, "add_done_callback"):
        try:
            task.add_done_callback(_on_detached_task_done)
            registered = True
        except BaseException:
            pass
    if not registered:
        try:
            if isinstance(task, AsyncTask):
                AsyncTask.add_done_callback(task, _on_detached_task_done)
                registered = True
            elif isinstance(task, AsyncFuture):
                AsyncFuture.add_done_callback(task, _on_detached_task_done)
                registered = True
            else:
                AsyncFuture.add_done_callback(task, _on_detached_task_done)
                registered = True
        except BaseException:
            pass
    if not registered:
        try:
            loop = async_get_running_loop()

            async def _observe_task() -> None:
                try:
                    await task
                except BaseException:
                    pass
                finally:
                    _DETACHED_TASKS.pop(task_id, None)
                    if loop is not None:
                        loop_tasks = getattr(loop, "_proofline_detached_tasks", None)
                        if loop_tasks is not None:
                            loop_tasks.pop(task_id, None)

            obs = loop.create_task(_observe_task())
            obs.add_done_callback(lambda _: None)
        except BaseException:
            _DETACHED_TASKS.pop(task_id, None)

    if not wrapper_started:
        try:
            task.cancel()
        except BaseException:
            pass
        _cleanup_discarded_awaitable(res)


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
        delivery. Tuples with more than 1,000 items, immutable bytes, mutable buffers
        or memoryviews with more than 65,536 bytes (or backed by a buffer larger than 65,536
        bytes), sets, frozensets, or deques with more than 65,536 items in review extension
        data skip on_poll snapshot delivery even with time remaining, and snapshot copy errors on
        unsupported mutable values propagate before on_poll runs.
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
                        deadline_token = _transport.DEADLINE.set(None)
                        try:
                            res = on_poll(snapshot)
                        finally:
                            _transport.DEADLINE.reset(deadline_token)
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
                if on_poll is not None and (_transport.remaining() or 0) <= 0:
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
        is reached are delivered; deadline expiry can suppress delivery. Tuples
        with more than 1,000 items, immutable bytes, mutable buffers or memoryviews
        with more than 65,536 bytes (or backed by a buffer larger than 65,536 bytes),
        sets, frozensets, or deques with more than 65,536 items in review extension data
        skip on_poll snapshot delivery even with time remaining, and snapshot copy errors
        on unsupported mutable values propagate before on_poll runs. Callback
        return-validation errors and inline exceptions propagate unconditionally, even when a
        terminal outcome has already been determined (cancellation requested during callback
        invocation takes precedence over return validation), preventing the waiter from
        returning a classified outcome.
        Failure propagation depends on the awaitable type and the polling deadline:
        already-done futures must be returned before the deadline to propagate (failures of
        already-done futures returned after expiry are detached and suppressed), coroutine
        failures are timed at wrapper completion rather than when the waiter retrieves
        them, and pending future failures propagate only if their done callback executes before
        the deadline expires (cutting off at done-callback execution and allowing any
        classified outcome to be returned).
        This allows any classified outcome to be returned when a callback finishes or returns
        after the deadline. When the deadline expires or when the wait is
        cancelled, unstarted coroutines returned by on_poll are closed without entering
        their body (a wrapper task may already have been scheduled), while already-running
        callback tasks and futures are detached without cancellation and may continue
        running (late SystemExit and KeyboardInterrupt from already-scheduled tasks are not
        suppressed). Synchronous callbacks must return before a terminal result can be
        delivered and the polling deadline cannot interrupt them.
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
                        waiter_task = async_current_task()
                        initial_cancelling = 0
                        if waiter_task is not None:
                            try:
                                if hasattr(waiter_task, "cancelling"):
                                    initial_cancelling = waiter_task.cancelling()
                            except BaseException:
                                pass
                        deadline_token = _transport.DEADLINE.set(None)
                        try:
                            res = on_poll(snapshot)
                        finally:
                            _transport.DEADLINE.reset(deadline_token)
                        cb_return_time = monotonic()
                        if waiter_task is not None:
                            is_task_cancelled = False
                            try:
                                if (
                                    hasattr(waiter_task, "cancelling")
                                    and waiter_task.cancelling() > initial_cancelling
                                ):
                                    is_task_cancelled = True
                                if hasattr(waiter_task, "cancelled") and waiter_task.cancelled():
                                    is_task_cancelled = True
                                if getattr(waiter_task, "_must_cancel", False):
                                    is_task_cancelled = True
                            except BaseException:
                                pass
                            if is_task_cancelled:
                                try:
                                    if isawaitable(res):
                                        _cleanup_discarded_awaitable(res, waiter_task=waiter_task)
                                except Exception:
                                    pass
                                await async_sleep(0)
                                raise AsyncCancelledError()
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

                            if async_isfuture(res):
                                try:
                                    is_done = res.done()
                                except BaseException:
                                    is_done = False
                                if is_done:
                                    deadline_val = _transport.DEADLINE.get()
                                    cb_returned_in_budget = (
                                        deadline_val is None or cb_return_time <= deadline_val
                                    )
                                    if cb_returned_in_budget:
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
                                    try:
                                        res_loop = (
                                            res.get_loop()
                                            if hasattr(res, "get_loop")
                                            else AsyncFuture.get_loop(res)
                                        )
                                    except Exception:
                                        res_loop = None
                                    running_loop = async_get_running_loop()
                                    if res_loop is not running_loop or (
                                        res_loop is not None and res_loop.is_closed()
                                    ):
                                        raise ValueError(
                                            "Pending callback futures must belong "
                                            "to the running event loop."
                                        )

                                    remaining_budget = _transport.remaining()
                                    if remaining_budget is not None and remaining_budget <= 0:
                                        _detach_overdue_future(res)
                                        if result is not None:
                                            return result
                                        break

                                    try:
                                        completion_fut = async_get_running_loop().create_future()
                                    except BaseException:
                                        _detach_overdue_future(res)
                                        raise
                                    completed_at: list[float] = []

                                    def _on_future_done(_: Any) -> None:
                                        completed_at.append(monotonic())
                                        if not completion_fut.done():
                                            completion_fut.set_result(None)

                                    fut_registered = False
                                    if hasattr(res, "add_done_callback"):
                                        try:
                                            res.add_done_callback(_on_future_done)
                                            fut_registered = True
                                        except BaseException:
                                            pass
                                    if not fut_registered:
                                        try:
                                            AsyncFuture.add_done_callback(res, _on_future_done)
                                            fut_registered = True
                                        except BaseException:
                                            _detach_overdue_future(res)
                                            raise
                                    deadline_val = _transport.DEADLINE.get()
                                    cb_finished_in_budget = bool(completed_at) and (
                                        deadline_val is None or completed_at[0] <= deadline_val
                                    )
                                    if cb_finished_in_budget:
                                        if hasattr(res, "result"):
                                            res.result()
                                        else:
                                            AsyncFuture.result(res)
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
                                    finally:
                                        try:
                                            if hasattr(res, "remove_done_callback"):
                                                res.remove_done_callback(_on_future_done)
                                            else:
                                                AsyncFuture.remove_done_callback(
                                                    res, _on_future_done
                                                )
                                        except BaseException:
                                            pass
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
                                remaining_budget = _transport.remaining()
                                if remaining_budget is not None and remaining_budget <= 0:
                                    _cleanup_discarded_awaitable(res)
                                    if result is not None:
                                        return result
                                    break
                                coro = res
                                completed_at = []
                                wrapper_started = False
                                captured_deadline = _transport.DEADLINE.get()

                                async def _runner() -> Any:
                                    nonlocal wrapper_started
                                    waiter_cancelling = False
                                    if waiter_task is not None:
                                        try:
                                            if hasattr(waiter_task, "cancelling"):
                                                waiter_cancelling = (
                                                    waiter_task.cancelling() > initial_cancelling
                                                )
                                            elif hasattr(waiter_task, "cancelled"):
                                                waiter_cancelling = waiter_task.cancelled()
                                        except BaseException:
                                            pass
                                    try:
                                        if hasattr(task, "cancelling") and task.cancelling() > 0:
                                            waiter_cancelling = True
                                        elif hasattr(task, "cancelled") and task.cancelled():
                                            waiter_cancelling = True
                                    except BaseException:
                                        pass

                                    deadline_expired = (
                                        captured_deadline is not None
                                        and monotonic() > captured_deadline
                                    )
                                    if waiter_cancelling or deadline_expired:
                                        _cleanup_discarded_awaitable(coro)
                                        return None
                                    wrapper_started = True
                                    _transport.DEADLINE.set(None)
                                    handback_exc: BaseException | None = None
                                    try:
                                        assert coro is not None
                                        await coro
                                    except (SystemExit, KeyboardInterrupt) as exc:
                                        handback_exc = exc
                                    finally:
                                        completed_at.append(monotonic())
                                    return handback_exc

                                runner_coro = _runner()
                                deadline_token_task = _transport.DEADLINE.set(None)
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
                                    _cleanup_discarded_awaitable(res)
                                    raise
                                finally:
                                    _transport.DEADLINE.reset(deadline_token_task)
                                try:
                                    task_completion_fut = async_get_running_loop().create_future()
                                except BaseException:
                                    _detach_overdue_task(task, res, wrapper_started)
                                    raise

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

                                cb_registered = False
                                if hasattr(task, "add_done_callback"):
                                    try:
                                        task.add_done_callback(_on_task_done)
                                        cb_registered = True
                                    except BaseException:
                                        pass
                                if not cb_registered:
                                    try:
                                        if isinstance(task, AsyncTask):
                                            AsyncTask.add_done_callback(task, _on_task_done)
                                            cb_registered = True
                                        elif isinstance(task, AsyncFuture):
                                            AsyncFuture.add_done_callback(task, _on_task_done)
                                            cb_registered = True
                                        else:
                                            AsyncFuture.add_done_callback(task, _on_task_done)
                                            cb_registered = True
                                    except BaseException:
                                        _detach_overdue_task(task, res, wrapper_started)
                                        raise

                                deadline_val = _transport.DEADLINE.get()
                                cb_finished_in_budget = bool(completed_at) and (
                                    deadline_val is None or completed_at[0] <= deadline_val
                                )
                                try:
                                    task_is_done = task.done() if hasattr(task, "done") else False
                                except BaseException:
                                    _detach_overdue_task(task, res, wrapper_started)
                                    raise

                                if task_is_done and cb_finished_in_budget:
                                    if not wrapper_started:
                                        try:
                                            task.cancel()
                                        except BaseException:
                                            pass
                                        _cleanup_discarded_awaitable(res)
                                    if hasattr(task, "result"):
                                        res_val = task.result()
                                    else:
                                        res_val = AsyncTask.result(task)
                                    if isinstance(res_val, (SystemExit, KeyboardInterrupt)):
                                        raise res_val

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
                                try:
                                    task_is_done = task.done() if hasattr(task, "done") else False
                                except BaseException:
                                    _detach_overdue_task(task, res, wrapper_started)
                                    raise

                                if cb_finished_in_budget and (
                                    task_completion_fut in done or task_is_done
                                ):
                                    if not wrapper_started:
                                        try:
                                            task.cancel()
                                        except BaseException:
                                            pass
                                        _cleanup_discarded_awaitable(res)
                                    if hasattr(task, "result"):
                                        res_val = task.result()
                                    else:
                                        res_val = AsyncTask.result(task)
                                    if isinstance(res_val, (SystemExit, KeyboardInterrupt)):
                                        raise res_val
                                else:
                                    _detach_overdue_task(task, res, wrapper_started)
                                    if result is not None:
                                        return result
                                    break
                if result is not None:
                    return result
                if on_poll is not None and (_transport.remaining() or 0) <= 0:
                    break
                await async_sleep(min(interval, _transport.remaining() or 0))
                interval = min(60, interval * 2)
            if result is not None:
                return result
            timed_out = outcome(last, url, "TIMED_OUT", head_commit_sha=head_commit_sha)
            return timed_out or ReviewOutcome("TIMED_OUT", url)
        finally:
            _transport.DEADLINE.reset(deadline)
