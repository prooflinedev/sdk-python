"""Status errors deliberately exclude response content from repr and args."""


class UnexpectedStatus(Exception):
    def __init__(self, status_code: int, content: bytes):
        self.status_code = status_code
        super().__init__(f"Unexpected HTTP status: {status_code}")


__all__ = ["UnexpectedStatus"]
