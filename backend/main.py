from contextlib import asynccontextmanager

from fastapi import FastAPI

try:
    from backend.services.account_service import router as account_router
    from backend.services.transaction_service import router as transaction_router
    from backend.services.payment_service import router as payment_router
    from backend.mcp_server import mcp
except ImportError:
    from services.account_service import router as account_router
    from services.transaction_service import router as transaction_router
    from services.payment_service import router as payment_router
    from mcp_server import mcp

# Create MCP ASGI app first so we can use its lifespan
mcp_app = mcp.http_app(transport="streamable-http")


@asynccontextmanager
async def lifespan(app):
    async with mcp_app.router.lifespan_context(app):
        yield


app = FastAPI(title="Banking Backend Services", lifespan=lifespan)

app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(payment_router)

# Mount MCP server at /mcp for agent tool access
app.mount("/mcp", mcp_app)


@app.get("/health")
def health():
    return {"status": "ok"}
