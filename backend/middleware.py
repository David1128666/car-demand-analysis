import time
import json
from fastapi import Request
from database import execute
from auth_utils import decode_token


SKIP_PATHS = {"/", "/health", "/docs", "/openapi.json", "/favicon.ico"}


async def request_logging_middleware(request: Request, call_next):
    path = request.url.path
    if path in SKIP_PATHS or path.startswith("/docs") or path.startswith("/openapi"):
        return await call_next(request)

    start = time.time()

    # Try to extract user from token
    operator_name = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = decode_token(auth[7:])
            operator_name = payload.get("username")
        except Exception:
            pass

    # Call the actual endpoint
    response = await call_next(request)

    elapsed_ms = int((time.time() - start) * 1000)

    # Determine module from path
    if path.startswith("/api/v1/"):
        parts = path[8:].split("/")
        module = parts[0] if parts else "unknown"
    else:
        module = "system"

    # Determine operation type from path + method
    operation_type = f"{request.method}_{module}"

    try:
        execute(
            """INSERT INTO operation_log
               (operator_name, operation_type, operation_module, operation_desc,
                request_method, request_url, response_code, execution_time,
                ip_address)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                operator_name,
                operation_type,
                module,
                f"{request.method} {path}",
                request.method,
                path[:500],
                str(response.status_code),
                elapsed_ms,
                request.client.host if request.client else None,
            ),
        )
    except Exception as e:
        print(f"[middleware] Failed to log request: {e}")

    return response
