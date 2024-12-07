from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai,
    applicants,
    candidates,
    company,
    jobs,
    resumes,
    recruiter,
    stages,
    zrapplicants,
)

api_router = APIRouter()
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(applicants.router, prefix="/applicants", tags=["applicants"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(recruiter.router, prefix="/recruiter", tags=["recruiter"])
api_router.include_router(stages.router, prefix="/stages", tags=["stages"])
api_router.include_router(
    zrapplicants.router, prefix="/zrapplicants", tags=["zrapplicants"]
)
