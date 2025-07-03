from typing import Optional, Any
from enum import Enum


class HarmonyErrorScope(Enum):
    NETWORKING = 'NETWORKING'
    SERVICE = 'SERVICE'
    SESSION = 'SESSION'
    INVALID_PARAMS = 'INVALID_PARAMS'


class HarmonyApiException(Exception):
    def __init__(
        self,
        error_scope: HarmonyErrorScope,
        request_id: str = None,
        message: Optional[str] = None,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        payload_error: Optional[Any] = None,
        network_error: Optional[Any] = None,
    ):
        self.error_scope = error_scope
        self.request_id = request_id
        self.message = message
        self.url = url
        self.status_code = status_code
        self.payload_error = payload_error
        self.network_error = network_error

    def __str__(self):
        return (
            f"HarmonyApiException: error_scope='{self.error_scope}', request_id='{self.request_id}', "
            f"message='{self.message}', url='{self.url}', status_code='{self.status_code}', "
            f"payload_error='{self.payload_error}', network_error='{self.network_error}'"
        )
