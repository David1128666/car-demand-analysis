import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import APP_TITLE, APP_VERSION
from routers import dashboard, analysis, cars, recommendations, auth, market, admin
from middleware import request_logging_middleware

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": f"服务器内部错误: {str(exc)}"},
    )


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(analysis.router)
app.include_router(cars.router)
app.include_router(recommendations.router)
app.include_router(market.router)
app.include_router(admin.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    return await request_logging_middleware(request, call_next)


@app.get("/")
def root():
    return {"message": APP_TITLE, "version": APP_VERSION, "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn, os, socket, subprocess

    def free_port(port: int):
        """Kill any process occupying the given port, with retries (Windows)."""
        import time

        # First attempt: just try to bind
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            s.close()
            return
        except OSError:
            pass

        # Kill processes holding the port
        try:
            result = subprocess.run(
                f'netstat -ano | findstr ":{port}.*LISTENING"',
                shell=True, capture_output=True, text=True
            )
            killed = set()
            for line in result.stdout.strip().split("\n"):
                parts = line.strip().split()
                if parts:
                    pid = parts[-1]
                    if pid not in killed and pid != "0":
                        killed.add(pid)
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True,
                                       capture_output=True)
                        print(f"[startup] Killed PID {pid} occupying port {port}")
        except Exception as e:
            print(f"[startup] Failed to free port {port}: {e}")

        # Retry binding with backoff (handles ghost sockets)
        for i in range(5):
            time.sleep(1)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                s.close()
                return
            except OSError:
                pass

        print(f"[startup] Warning: could not free port {port}, attempting anyway")

    free_port(8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
