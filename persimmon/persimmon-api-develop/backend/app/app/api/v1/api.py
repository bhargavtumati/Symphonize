from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai,
    applicants,
    candidates,
    careerpage,
    company,
    integration,
    jobs,
    resumes,
    recruiter,
    stages,
    email,
    zrapplicants,
    templates,
    share_applicants,
    linkedin,
    whatsappintegration,
    watiintegration,
    whatchimpintegration
)

api_router = APIRouter()
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(applicants.router, prefix="/applicants", tags=["applicants"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(careerpage.router, prefix="/careerpage", tags=["careerpage"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(integration.router, prefix="/integration", tags=["integration"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(recruiter.router, prefix="/recruiter", tags=["recruiter"])
api_router.include_router(stages.router, prefix="/stages", tags=["stages"])
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(zrapplicants.router, prefix="/zrapplicants", tags=["zrapplicants"])
api_router.include_router(templates.router, prefix="/template", tags=["template"])
api_router.include_router(share_applicants.router, prefix="/share", tags=["share applicants"])
api_router.include_router(linkedin.router, prefix="/linkedin", tags=["linkedin"])
api_router.include_router(whatsappintegration.router, prefix="/whatsappintegration", tags=["whatsappintegration"])
api_router.include_router(watiintegration.router, prefix="/watiintegration", tags=["watiintegration"])
api_router.include_router(whatchimpintegration.router, prefix="/whatchimpintegration", tags=["whatchimpintegration"])