from fastapi import FastAPI

try:
    from backend.services.account_service import router as account_router
except ImportError:
    from services.account_service import router as account_router

app = FastAPI(title="Banking Backend Services")

app.include_router(account_router)


@app.get("/health")
def health():
    return {"status": "ok"}
