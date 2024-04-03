import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    ItemNotFoundError,
    RateLimitExceededError,
    UnhandledExternalError,
)
from app.router import router
from app.services.client import DotabuffClient
from settings import CLIENTS

app = FastAPI()
app.include_router(router)


@app.get("/health")
def get_health() -> dict:
    """Health endpoint."""
    return {"health": "ok"}


@app.on_event("startup")
async def app_startup() -> None:
    """Startup event."""
    CLIENTS["dotabuff"] = DotabuffClient()


@app.exception_handler(ItemNotFoundError)
async def handle_not_found_error(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    """Handle ItemNotFoundError."""
    return JSONResponse(status_code=404, content={"detail": "Item does not exist."})


@app.exception_handler(RateLimitExceededError)
async def handle_rate_limit_error(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    """Handle ItemNotFoundError."""
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})


@app.exception_handler(UnhandledExternalError)
async def handle_external_unhandled_error(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    """Handle ItemNotFoundError."""
    return JSONResponse(status_code=500, content={"detail": "Unknown error occurred."})


if __name__ == "__main__":
    uvicorn.run(app)
