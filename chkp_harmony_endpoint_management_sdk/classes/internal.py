from typing import Any, Callable


class SessionOperations:
    def __init__(self, job_status_operation: Callable[[], Any], login_operation: Callable[[], Any], keep_alive_operation: Callable[[], Any] = None):
        self.login_operation = login_operation
        self.keep_alive_operation = keep_alive_operation
        self.job_status_operation = job_status_operation
