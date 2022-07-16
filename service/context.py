from contextvars import ContextVar

REQUEST_ID: ContextVar[str] = ContextVar("REQUEST_ID", default="-")
