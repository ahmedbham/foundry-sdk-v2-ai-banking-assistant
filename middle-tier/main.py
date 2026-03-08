from fastapi import FastAPI

app = FastAPI(title="Banking Assistant Middle Tier")


@app.get("/health")
def health():
    return {"status": "ok"}
