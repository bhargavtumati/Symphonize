from fastapi import (
    FastAPI, Request
)
from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.db.session import SessionLocal
from app.models.master_data import MasterData
from app.models.job import Job

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("startup fastapi")
    session = SessionLocal() 
    try:
        MasterData.seed_master_data(session=session)
        Job.load_enhanced_jd(session=session)
        yield
    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {e}")
    finally:
        session.close()
        # shutdown
        print("shutdown fastapi")
    


# Core Application Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS origins enabled
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
async def root():
    """
    An example "Hello world" FastAPI route.
    """
    # if oso.is_allowed(user, "read", message):
    return {"message": "Hello World"}


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    custom_errors = []
    
    for error in errors:
        custom_errors.append({
            "loc": error['loc'],
            "msg": error['msg'].replace('Value error, ',''),  
            "input": error.get('input')
        })

    return JSONResponse(
        status_code=422,
        content={"detail": custom_errors},
    )
