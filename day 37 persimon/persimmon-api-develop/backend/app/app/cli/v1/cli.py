import asyncio
import typer
from app.services import applicants as sa

app = typer.Typer(no_args_is_help=True)

import os

os.environ["BACKEND_CORS_ORIGINS"] = "['*']"


@app.command()
def applicant_classify(candidate_id: str, applicant_id: str, job_id: str):
    print("classifying applicants ...")
    asyncio.run(
        sa.classify(candidate_id=candidate_id, applicant_id=applicant_id, job_id=job_id)
    )


if __name__ == "__main__":
    app()
