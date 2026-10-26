"""Published knowledge operations through the scoped MCP server."""

from ._mcp import AsyncMcpTools, KnowledgeResult, McpTools, _repository


class KnowledgeClient(McpTools):
    def list_wiki_pages(self, repository: str, *, commit: str | None = None) -> KnowledgeResult:
        return self._call("list_wiki_pages", _repository(repository, commit))

    def get_wiki_page(
        self, repository: str, page_key: str, *, commit: str | None = None
    ) -> KnowledgeResult:
        return self._call(
            "get_wiki_page", {**_repository(repository, commit), "page_key": page_key}
        )

    def ask_codebase(
        self, repository: str, question: str, *, commit: str | None = None
    ) -> KnowledgeResult:
        return self._call("ask_codebase", {**_repository(repository, commit), "question": question})

    def get_architecture_document(self, environment_id: str) -> KnowledgeResult:
        return self._call("get_architecture_document", {"environment_id": environment_id})

    def get_plan(self, plan_id: str) -> KnowledgeResult:
        return self._call("get_plan", {"plan_id": plan_id})

    def start_plan_implementation(self, plan_id: str) -> KnowledgeResult:
        return self._call("start_plan_implementation", {"plan_id": plan_id})

    def get_plan_implementation(self, implementation_id: str) -> KnowledgeResult:
        return self._call("get_plan_implementation", {"implementation_id": implementation_id})


class AsyncKnowledgeClient(AsyncMcpTools):
    async def list_wiki_pages(
        self, repository: str, *, commit: str | None = None
    ) -> KnowledgeResult:
        return await self._call("list_wiki_pages", _repository(repository, commit))

    async def get_wiki_page(
        self, repository: str, page_key: str, *, commit: str | None = None
    ) -> KnowledgeResult:
        return await self._call(
            "get_wiki_page", {**_repository(repository, commit), "page_key": page_key}
        )

    async def ask_codebase(
        self, repository: str, question: str, *, commit: str | None = None
    ) -> KnowledgeResult:
        return await self._call(
            "ask_codebase", {**_repository(repository, commit), "question": question}
        )

    async def get_architecture_document(self, environment_id: str) -> KnowledgeResult:
        return await self._call("get_architecture_document", {"environment_id": environment_id})

    async def get_plan(self, plan_id: str) -> KnowledgeResult:
        return await self._call("get_plan", {"plan_id": plan_id})

    async def start_plan_implementation(self, plan_id: str) -> KnowledgeResult:
        return await self._call("start_plan_implementation", {"plan_id": plan_id})

    async def get_plan_implementation(self, implementation_id: str) -> KnowledgeResult:
        return await self._call("get_plan_implementation", {"implementation_id": implementation_id})
