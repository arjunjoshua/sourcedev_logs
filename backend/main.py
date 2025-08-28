#! venv/bin/python
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from api.logs import router
import uvicorn

cors_origins = [
    "http://localhost:5173",
]

app = fastapi.FastAPI(
    root_path="/api",
    title="Source.dev logs API",
    description="API demo for Source.dev logs",
    version="0.0.1",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include the router
app.include_router(router, tags=["logs"])



@app.get("/")
async def root():
    return {"message": "Welcome to the Source.dev logs API!"}


if __name__ == "__main__":
    exec("uvicorn.run('main:app', host='0.0.0.0', port=5000, reload=True, log_level='info')")