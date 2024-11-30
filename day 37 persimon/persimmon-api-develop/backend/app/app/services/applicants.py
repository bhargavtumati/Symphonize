# services/applicant.py
import json 
import os
from pathlib import Path
from typing import List, Tuple
from app.models.applicant import Applicant
from app.models.recruiter import Recruiter
from app.models.stages import Stages
from app.helpers import pdf_helper as pdfh, ai_helper as aih, json_helper as jsonh, s3_helper as s3h,solr_helper as solrh 
from app.api.v1.endpoints.models.applicant_model import FilterRequest
from sqlalchemy.orm import Session
from typing import Tuple, Dict
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException
import asyncio
import uuid
from typing import List, Optional, Dict

PDF_OUTPUT_PATH = "/tmp"  # Temporary directory for storing converted PDF files
BUCKET_NAME = 'persimmon-ai'


# Preference weight mapping
PREFERENCE_WEIGHTS = {
    "good to have": 1,
    "prefer to have": 2,
    "must have": 3,
}


async def process_resume(file, session: Session,created_by,job_id,job_code) -> Tuple[bool, str, Dict]:
    file_success = True
    error_message = ""
    error_list = []
    flatten_resume = None
    temp_files_to_clean = []
    original_pdf_name = None

    try:
        unique_id = uuid.uuid4()
        original_file_name = f"{unique_id}_{file.filename}"
        # Step 1: Extract text from the resume
        extracted_text = await pdfh.extract_text_from_file(file)

        if not extracted_text:
            raise ValueError(f"Failed to extract text from {file.filename}")

        processed_file_path = None
        flatten_resume_solr = None
        processed_upload = None 
        original_upload = None 
        generated_json = None      

        # Step 2: Convert DOCX to PDF if needed
        if file.filename.endswith('.docx'):
            output_pdf_name = f"{Path(original_file_name).stem}.pdf"
            output_pdf_path = os.path.join(PDF_OUTPUT_PATH, output_pdf_name)
            try:
                processed_file_path = await pdfh.convert_docx_to_pdf(extracted_text, output_pdf_path)

                if not processed_file_path:
                    raise ValueError(f"Failed to convert {original_file_name} to PDF")
                temp_files_to_clean.append(processed_file_path)
            except Exception as e:
                file_success = False
                error_message = f"Error converting {original_file_name} to PDF: {str(e)}"
                error_list.append(error_message)
                return file_success, error_list, flatten_resume

        # Step 3: Prepare upload paths and async upload tasks
        gcs_original_path = f"data/archive/resumes/pdf/{original_file_name}"
        gcs_processed_path = f"data/processed/{output_pdf_name if processed_file_path else original_file_name}"

        tasks=[]
        # Define tasks for uploading
        tasks.append(s3h.upload_to_gcp(BUCKET_NAME, file.file, gcs_original_path)) 

        if processed_file_path:
            processed_file = open(processed_file_path, 'rb')
            try:
                tasks.append(s3h.upload_to_gcp(BUCKET_NAME, processed_file, gcs_processed_path))
            except Exception as e :
                print(f"Error preparing processed file upload: {str(e)}")

        # Upload files concurrently
        gcp_paths = {
            'original_resume': '',
            'processed_resume': ''
        }
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print(f"the result of that are {results[0]}")
            if "The file" in results[0]:
                error_message = results[0]
                path_start = error_message.find("data/")
                print(f"this is path start : {path_start}")
                if path_start != -1:
                    file_path = error_message[path_start:]
                    file_name = file_path.split('/')[-1]
                    print(f"The file name extracted is {file_name}")
                error_message = f"the file {file_name} not got uploaded "
                error_list.append(error_message)
                file_success = False
            if  file_success:
                print("this is the original resume path  block started ")
                gcp_paths['original_resume'] = results[0] 
            print(f"the gcp original resume is {gcp_paths['original_resume']}")
            print(f"the resrults after upload are : {results}")
            if processed_file_path:
                processed_file.close()
            if processed_file_path and len(results) > 1:
                gcp_paths['processed_resume'] = results[1] if isinstance(results[1],str) else '' 
        except Exception as e:
            error_message += f"\nFailed to upload files to GCP: {str(e)}"
            error_list.append(error_message)
            return file_success, error_list, flatten_resume

        # Step 4: Generate JSON from the extracted text
        if file_success:
            try:
                generated_json = await aih.extract_features_from_resume(extracted_text)
                if isinstance(generated_json, str):
                    generated_json = json.loads(generated_json)
            except Exception as e:
                file_success = False
                error_message = f"Error generating JSON for {file.filename}: {str(e)}"
                error_list.append(error_message)
                return file_success, error_list, flatten_resume

        # Step 5: Flatten and store JSON
        if file_success:
            try:
                flatten_resume = await jsonh.flatten_resume_data(generated_json)
                print(f"flatenned resume is {flatten_resume}")
                flatten_resume['orignal_resume'] = gcp_paths["original_resume"]
                flatten_resume['processed_resume'] = gcp_paths["processed_resume"]

                default_stages = [
                    {
                        'uuid': str(uuid.uuid4()),
                        'name': 'new'
                    },
                    {
                        'uuid': str(uuid.uuid4()),
                        'name': 'Pre-Screened'
                    },
                    {
                        'uuid': str(uuid.uuid4()),
                        'name': 'Shortlisted'
                    },
                    {
                        'uuid': str(uuid.uuid4()),
                        'name': 'Interviewing'
                    },
                    {
                        'uuid': str(uuid.uuid4()),
                        'name': 'Deployed'
                    },
                    {
                        'uuid': str(uuid.uuid4()),
                        'name': 'Rejected'
                    }
                ]

                if flatten_resume:
                    try:
                        stages_existing: Stages = Stages.get_by_id(session=session, job_id=job_id)

                        if not stages_existing:
                            stage_uuid = default_stages[0]['uuid']
                        else:
                            stage_uuid = stages_existing.stages[0]['uuid']     

                        applicant_uuid = str(uuid.uuid4())
                        applicant_data = Applicant(details=flatten_resume, stage_uuid=stage_uuid, job_id=job_id, uuid=applicant_uuid)
                        applicant_data.create(session=session,created_by=created_by)
                        try:
                            flatten_resume_solr = await jsonh.flatten_resume_data_solr(generated_json)
                            flatten_resume_solr['uuid'] = applicant_uuid
                            flatten_resume_solr['stage_uuid'] = stage_uuid
                            flatten_resume_solr['job_code'] = job_code
                            result_solr = solrh.upload_to_solr(flatten_resume_solr)
                            print(f"the result from solr is {result_solr}")
                        except Exception as e :
                            raise HTTPException(status_code=400, detail="Invalid request or missing required fields.") 

                        if not stages_existing:
                            recruiter = Recruiter.get_by_email_id(session=session, email=created_by)
                            stages = Stages(recruiter_id=recruiter.id, job_id=job_id, stages=default_stages)
                            job_created = stages.create(session=session, created_by=created_by)

                    except Exception as e:
                        raise HTTPException(status_code=404, detail=f"Job not found")
                     
            except Exception as e:
                file_success = False
                if "Job not found" in str(e):
                    raise HTTPException(status_code=404, detail="Job not found. Please ensure the job ID is correct.")
                else:
                    error_message = f"Please try to upload again , Error storing flattened data for {file.filename}: {str(e)}"
                    error_list.append(error_message)
                    return file_success, error_list, flatten_resume

    except Exception as e:
        file_success = False
        if "Job not found" in str(e):
            raise HTTPException(status_code=404, detail="Job not found. Please ensure the job ID is correct.")
        elif "Invalid request" in str(e):
            raise HTTPException(status_code=400, detail="Invalid request or missing required fields.") 
        else:
            error_message = f"Unexpected error processing {file.filename}: {str(e)}"
            error_list.append(error_message)
            return file_success, error_list, flatten_resume

    # Cleanup temporary files
    for temp_file in temp_files_to_clean:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up temporary file: {temp_file}")
        except Exception as e:
            print(f"Error cleaning up file {temp_file}: {str(e)}")

    return file_success, error_list, flatten_resume


def construct_query(filters: FilterRequest) -> str:
    filters = filters.filters

    # Compute industry type weights
    individual_industry_weights = []
    overall_industry_weight = 0
    experience_query_parts = []
    if filters.industry_type: 
        for industry in filters.industry_type:
            weight = PREFERENCE_WEIGHTS.get(industry.pref, 0) * (industry.max + industry.min)
            individual_industry_weights.append(f"industry_type : {industry.name}^{weight}")
            overall_industry_weight += weight
            
            #construct the experience range query 
            experience_query_parts.append(f"work_experience:[{industry.min} TO {industry.max}]")

    industry_query = " OR ".join(individual_industry_weights)
    weighted_industry_query = f"(({industry_query})^{overall_industry_weight})"

    # Join the experience queries with OR for the final experience query
    experience_query = " OR ".join(experience_query_parts)
    
    remuneration_query = ""
    if filters.remuneration:
        remuneration_query = f"current_ctc:[{filters.remuneration.min} TO {filters.remuneration.max}]"

    # Skills
    individual_skills_weights = []
    overall_skills_weight = 0
    if filters.skills:
        for skill in filters.skills:
            if skill.name and skill.pref and skill.value is not None:
                weight = PREFERENCE_WEIGHTS.get(skill.pref, 0) * skill.value
                individual_skills_weights.append(f"skills : {skill.name}^{weight}")
                overall_skills_weight += weight

    skills_query = " OR ".join(individual_skills_weights)
    weighted_skills_query = f"(({skills_query})^{overall_skills_weight})" if skills_query else ""

    # Responsibilities
    responsibilities_query = ""
    if filters.responsibilities:
        valid_responsibilities = [resp for resp in filters.responsibilities if resp]
        responsibilities_query = " OR ".join([f"responsibilities: \"{resp}\"" for resp in valid_responsibilities])
        if responsibilities_query:
            responsibilities_query = f"({responsibilities_query})"

    # Pedigree
    inclusion_query = ""
    exclusion_query = ""
    exclusion_parts = []
    inclusion_parts = []
    if filters.pedigree:
        inclusion_parts = []
        for pedigree in filters.pedigree:
            if pedigree.specifications:
                for spec in pedigree.specifications:
                    if spec.spec == "include" and spec.qualification and spec.institution_name:
                        inclusion_parts.append(f"(education:\"{spec.institution_name}\")")
                    elif spec.spec == "exclude" and spec.qualification and spec.institution_name:
                         exclusion_parts.append(f"-education:\"{spec.institution_name}\"")

    inclusion_query = " OR ".join(inclusion_parts) if inclusion_parts else ""
    exclusion_query = " AND ".join(exclusion_parts) if exclusion_parts else ""

    # Availability
    availability_query = ""
    if filters.availability and filters.availability.name and filters.availability.value:
        availability_query = f"availability:[0 TO {filters.availability.value}]"

    # Workmode
    workmode_query = ""
    if filters.workmode and filters.workmode.value:
        workmode_query = f"workmode:{filters.workmode.value}"

    # Soft Skills
    softskills_query_parts = []
    overall_softskills_weight = 0

    if filters.soft_skills:
        for soft_skill in filters.soft_skills:
            if soft_skill.name and soft_skill.pref and soft_skill.min_value and soft_skill.max_value:
                # Weight calculation for min_value and max_value
                min_weight = PREFERENCE_WEIGHTS.get(soft_skill.pref, 0)
                max_weight = min_weight * 1.5  # Giving higher preference to max_value

                # Adding queries for min_value and max_value
                softskills_query_parts.append(f"soft_skills:\"{soft_skill.name} - {soft_skill.min_value}\"^{min_weight}")
                softskills_query_parts.append(f"soft_skills:\"{soft_skill.name} - {soft_skill.max_value}\"^{max_weight}")

                # Updating the overall weight
                overall_softskills_weight += (min_weight + max_weight)
    
    # Combining the parts into a weighted query
    softskills_query = " OR ".join(softskills_query_parts)
    weighted_softskills_query = f"(({softskills_query})^{overall_softskills_weight})" if softskills_query else ""

    # Location
    location_query = ""
    if filters.location:
        location_parts = []
        if filters.location.first_priority:
            location_parts.append(f"locations_list:{filters.location.first_priority}")
        location_query = " OR ".join(location_parts)

    # Transition Behaviour
    transition_behaviour_query_parts = []
    overall_transition_behaviour_weight = 0
    if filters.transition_behaviour:
        for behaviour in filters.transition_behaviour:
            weight = PREFERENCE_WEIGHTS.get(behaviour.preference, 0) * behaviour.value
            range_query = f"transition_behaviour:[0 TO {behaviour.value}]^{weight}"
            transition_behaviour_query_parts.append(range_query)
            overall_transition_behaviour_weight += weight
        
    transition_behaviour_query = " OR ".join(transition_behaviour_query_parts)
    weighted_transition_behaviour_query = f"(({transition_behaviour_query})^{overall_transition_behaviour_weight})" if transition_behaviour_query else ""

    # Advanced Filters
    advanced_filter_queries = []
    if filters.advanced_filters:
        for advanced_filter in filters.advanced_filters:
            field_name = advanced_filter.name
            weight = PREFERENCE_WEIGHTS.get(advanced_filter.preference, 0) * advanced_filter.value
            if field_name == "company_size":
                advanced_filter_queries.append(f"company_size:{advanced_filter.value}^{weight}")
            elif field_name == "team_size":
                advanced_filter_queries.append(f"team_size:{advanced_filter.value}^{weight}")

    advanced_filter_query = " OR ".join(advanced_filter_queries)

    # Combine all queries
    combined_query_parts = [
        weighted_industry_query,
        experience_query,
        weighted_skills_query,
        remuneration_query,
        responsibilities_query,
        inclusion_query,
        availability_query,
        workmode_query,
        location_query,
        weighted_softskills_query,
        weighted_transition_behaviour_query,
        advanced_filter_query,
    ]
    final_query = " OR ".join([q for q in combined_query_parts if q])
    print(f"the query is {exclusion_query}")
    return final_query , exclusion_query