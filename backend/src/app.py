from src.infrastructure.database.connection import init_models
from src.routes import V1_APPOINTMENT_ROUTER
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

'''@app.middleware("http")
async def add_middleware(request: Request, call_next):
    from src.app import db, request as ctx_request 
    from app.database import async_session
    token = ctx_request.set(request)
    async with async_session() as db_session:
        async with db_session.begin():
            db_token = db.set(db_session)
            response = await call_next(request) 
            db.reset(db_token)

    ctx_request.reset(token)
    return response'''

app.include_router(V1_APPOINTMENT_ROUTER, prefix="/v1")

@app.on_event("startup")
async def startup_event():
    await init_models()


