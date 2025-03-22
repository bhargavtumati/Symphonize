# services/applicant.py
import asyncio
import json
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.models.applicant_model import FilterRequest, Filters
from app.helpers import ai_helper as aih
from app.helpers import gcp_helper as gcph
from app.helpers import json_helper as jsonh
from app.helpers import pdf_helper as pdfh
from app.helpers import solr_helper as solrh, image_helper as imageh
from app.models.applicant import Applicant
from app.models.stages import Stages
from app.models.job import Job
from app.helpers.match_score_helper import get_match_score
import traceback
import logging
import math
from io import BytesIO

PDF_OUTPUT_PATH = "/tmp"  # Temporary directory for storing converted PDF files

logger = logging.getLogger(__name__)

# Preference weight mapping
PREFERENCE_WEIGHTS = {
    "good to have": 1,
    "preferred to have": 2,
    "must have": 3,
}

SOFTSKILL_WEIGHTS = {
    "Basic": 2,
    "Medium": 4,
    "Advanced": 6,
}


async def process_resume(file, session: Session, created_by, job_id, job_code, phone_number: int=None, full_name:str =None, email_id:str = None, linkedin_url:str=None ) -> Tuple[bool, str, Dict]:
    file_success = True
    error_message = ""
    error_list = []
    flatten_resume = None
    temp_files_to_clean = []
    original_pdf_name = None

    try:
        base64_applicant_image = None
        unique_id = uuid.uuid4()
        original_file_name = f"{unique_id}_{file.filename}"
        content = await file.read()
        file.file.seek(0)

        # Step 1: Extract text from the resume
        extracted_text = await pdfh.extract_text_from_file(file)

        if not extracted_text:
            raise ValueError(f"Failed to extract text from {file.filename}")
        
        file_extension = file.filename.split('.')[-1].lower()
        try:
            if file_extension == "pdf":
                base64_applicant_image = imageh.extract_first_face_from_pdf(BytesIO(content))
            elif file_extension == "docx":
                base64_applicant_image = imageh.extract_first_face_from_docx(BytesIO(content))
        except HTTPException as e:
            raise e

        # processed_file_path = None
        flatten_resume_solr = None
        generated_json = None      

        # Step 2: Convert DOCX to PDF if needed
        # if file.filename.endswith('.docx'):
        #     output_pdf_name = f"{Path(original_file_name).stem}.pdf"
        #     output_pdf_path = os.path.join(PDF_OUTPUT_PATH, output_pdf_name)
        #     try:
        #         processed_file_path = await pdfh.convert_docx_to_pdf(extracted_text, output_pdf_path)

        #         if not processed_file_path:
        #             raise ValueError(f"Failed to convert {original_file_name} to PDF")
        #         temp_files_to_clean.append(processed_file_path)
        #     except Exception as e:
        #         file_success = False
        #         error_message = f"Error converting {original_file_name} to PDF: {str(e)}"
        #         error_list.append(error_message)
        #         return file_success, error_list, flatten_resume

        # Step 3: Prepare upload paths and async upload tasks
        PERSIMMON_DATA=os.getenv("PERSIMMON_DATA", "persimmon-data")
        ENVIRONMENT = os.getenv("ENVIRONMENT","development")
        gcs_original_path = f"{ENVIRONMENT}/resumes/raw/{original_file_name}"
        # gcs_processed_path = f"data/processed/{output_pdf_name if processed_file_path else original_file_name}"

        tasks=[]
        # Define tasks for uploading
        tasks.append(gcph.upload_to_gcp(PERSIMMON_DATA, file.file, gcs_original_path)) 

        # if processed_file_path:
        #     processed_file = open(processed_file_path, 'rb')
        #     try:
        #         tasks.append(gcph.upload_to_gcp(BUCKET_NAME, processed_file, gcs_processed_path))
        #     except Exception as e :
        #         print(f"Error preparing processed file upload: {str(e)}")

        # Upload files concurrently
        gcp_paths = {
            'original_resume': '',
            'processed_resume': ''
        }
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            if "The file" in results[0]:
                error_message = results[0]
                path_start = error_message.find("data/")
                if path_start != -1:
                    file_path = error_message[path_start:]
                    file_name = file_path.split('/')[-1]
                error_message = f"the file {file_name} not got uploaded "
                error_list.append(error_message)
                file_success = False
            if  file_success:
                gcp_paths['original_resume'] = results[0] 
            print(f"the gcp original resume is {gcp_paths['original_resume']}")
            print(f"the results after upload are : {results}")
            # if processed_file_path:
            #     processed_file.close()
            # if processed_file_path and len(results) > 1:
            #     gcp_paths['processed_resume'] = results[1] if isinstance(results[1],str) else '' 
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
                flatten_resume['original_resume'] = gcp_paths["original_resume"]
                flatten_resume['processed_resume'] = gcp_paths["processed_resume"]

                if flatten_resume:
                    try:
                        try:
                            stages_existing: Stages = Stages.get_by_id(session=session, job_id=job_id)
                            if len(stages_existing.stages) > 0:
                                stage_uuid = stages_existing.stages[0]['uuid']
                        except: 
                            raise HTTPException(status_code=404, detail="Stages not found")

                        if full_name and len(flatten_resume['personal_information']['full_name']) == 0:
                            flatten_resume['personal_information']['full_name'] = full_name
                        if phone_number and len(flatten_resume['personal_information']['phone']) == 0:
                            flatten_resume['personal_information']['phone'] = phone_number
                        if email_id and len(flatten_resume['personal_information']['email']) == 0:
                            flatten_resume['personal_information']['email'] = email_id
                        if linkedin_url and len(flatten_resume['social_media']['linkedin']) == 0:
                            flatten_resume['social_media']['linkedin'] = linkedin_url

                        db_job = Job.get_by_code(session=session, code=job_code)
                        match = get_match_score(db_job.description, extracted_text)
                        flatten_resume['match'] = match
                        flatten_resume['applicant_image'] = base64_applicant_image

                        applicant_uuid = str(uuid.uuid4())
                        applicant_data: Applicant = Applicant(details=flatten_resume, stage_uuid=stage_uuid, job_id=job_id, uuid=applicant_uuid)
                        solr_flag = False

                        try:
                            flatten_resume_solr = await jsonh.flatten_resume_data_solr(generated_json)
                            flatten_resume_solr['applicant_uuid'] = applicant_uuid
                            flatten_resume_solr['stage_uuid'] = stage_uuid
                            flatten_resume_solr['job_code'] = job_code
                            result_solr = await solrh.upload_to_solr(flatten_resume_solr)
                            logger.info(f"THE RESULT FROM SOLR IS {result_solr}") 
                            if result_solr["message"] != "Document uploaded successfully" :
                                solr_flag = True
                        except Exception as e :
                            traceback.print_exc()
                            logger.error("SOLR UPLOAD ERROR")
                            solr_flag = True
                            raise HTTPException(status_code=400, detail="Invalid request or missing required fields.") 
                        
                        if solr_flag:
                            file_success = False
                            error_message = f"Please try to upload again, Error uploading applicant data to solr for : '{file.filename}'"
                            error_list.append(error_message)
                            logger.error(f"SOLR UPLOAD ERROR : {error_message}", exc_info=True)
                            return  file_success, error_list, flatten_resume
                        try:
                            applicant_data.create(session=session,created_by=created_by)
                        except Exception as e:
                            traceback.print_exc()
                            print('error',str(e))

                    except Exception as e:
                        if "Stages not found" in str(e):
                            raise HTTPException(status_code=404, detail="Stages not found")
                        raise HTTPException(status_code=404, detail=f"Job not found")
                     
            except Exception as e:
                file_success = False
                if "Job not found" in str(e):
                    raise HTTPException(status_code=404, detail="Job not found. Please ensure the job ID is correct.")
                elif "Stages not found" in str(e):
                    raise HTTPException(status_code=404, detail="Stages not found")
                else:
                    error_message = f"Please try to upload again , Error storing flattened data for {file.filename}: {str(e)}"
                    error_list.append(error_message)
                    return file_success, error_list, flatten_resume

    except Exception as e:
        traceback.print_exc()
        file_success = False
        if "Job not found" in str(e):
            raise HTTPException(status_code=404, detail="Job not found. Please ensure the job ID is correct.")
        elif "Invalid request" in str(e):
            raise HTTPException(status_code=400, detail="Invalid request or missing required fields.") 
        elif "Stages not found" in str(e):
            raise HTTPException(status_code=404, detail="Stages not found")
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
    filters: Filters = filters.filters

    # Compute industry type weights
    individual_industry_weights = []
    weighted_industry_query=None
    experience_query=None
    industry_query= ""
    overall_industry_weight = 0
    experience_query_parts = []
    print("the industry type is ", filters.industry_type)
    if filters.industry_type: 
        for industry in filters.industry_type :
            if industry.name and industry.pref and industry.min and industry.max is not None:
                print("this is if block ")
                weight = PREFERENCE_WEIGHTS.get(industry.pref.lower(), 0) * math.ceil(industry.max + industry.min)
                individual_industry_weights.append(f'industry_type : "{industry.name}"^{weight}')
                overall_industry_weight += weight
            else:
                print("this is else block ")
                industry_query=None
            
            #construct the experience range query 
                experience_query_parts.append(f"work_experience:[{industry.min} TO {industry.max}]")
    else:
        industry_query=None
        print("thsi is the last else block ")
    if industry_query!=None:
        print("the another industry filter query is ", industry_query)
        industry_query = " OR ".join(individual_industry_weights)
        weighted_industry_query = f"(({industry_query})^{overall_industry_weight})"

        # Join the experience queries with OR for the final experience query
        experience_query = " OR ".join(experience_query_parts)
    print("the industry query is ", weighted_industry_query)
    remuneration_query = ""
    if filters.remuneration:
        remuneration_query = f"current_ctc:[{filters.remuneration.min} TO {filters.remuneration.max}]"

    # Skills
    individual_skills_weights = []
    overall_skills_weight = 0
    if filters.skills:
        for skill in filters.skills:
            if skill.name and skill.pref and skill.value is not None:
                weight = PREFERENCE_WEIGHTS.get(skill.pref.lower(), 0) * skill.value
                print("the skill weight is ", weight)
                individual_skills_weights.append(f'skills : "{skill.name}"^{weight}')
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
                if pedigree.specifications and pedigree.name.strip().lower() == 'education':
                    for spec in pedigree.specifications:
                        spec.institution_name = re.sub(r'\(.*?\)', '', spec.institution_name)
                        if spec.spec.lower() == "include" and spec.qualification and spec.institution_name:
                            inclusion_parts.append(f"(education:{spec.institution_name}*)")
                        elif spec.spec.lower() == "exclude" and spec.qualification and spec.institution_name:
                            exclusion_parts.append(f"-education:{spec.institution_name}*")
                elif pedigree.specifications and pedigree.name.strip().lower() == 'company':
                    for spec in pedigree.specifications:
                        spec.institution_name = re.sub(r'\(.*?\)', '', spec.institution_name)
                        if spec.spec.lower() == "include" and spec.qualification and spec.institution_name:
                            inclusion_parts.append(f"(company:{spec.institution_name}*)")
                        elif spec.spec.lower() == "exclude" and spec.qualification and spec.institution_name:
                            exclusion_parts.append(f"-company:{spec.institution_name}*")


    inclusion_query = " OR ".join(inclusion_parts) if inclusion_parts else ""
    exclusion_query = " AND ".join(exclusion_parts) if exclusion_parts else ""

    # Availability
    availability_query = ""
    if filters.availability and filters.availability.name and filters.availability.value:
        availability_query = f"availability:[0 TO {filters.availability.value}]"


    # Workmode
    workmode_query = ""
    if filters.workmode and filters.workmode.value:
        workmode_query = f'workmode:"{filters.workmode.value}"'

    print("the workmode query is ", workmode_query)

    # Soft Skills
    # Skills
    individual_soft_skills_weights = []
    overall_soft_skills_weight = 0
    if filters.soft_skills:
        for soft_skill in filters.soft_skills:
            print("the soft_skill is ", soft_skill.pref)
            if soft_skill.name and soft_skill.pref and soft_skill.min_value and soft_skill.max_value:
                print("the max value is ",soft_skill.max_value)
                weight = PREFERENCE_WEIGHTS.get(soft_skill.pref.lower(), 0) * int(soft_skill.max_value)
                print("the the weight is ", type(weight),weight)
                individual_soft_skills_weights.append(f'soft_skills : "{soft_skill.name}"^{weight}')
                overall_soft_skills_weight += weight

    soft_skills_query = " OR ".join(individual_soft_skills_weights)
    weighted_softskills_query = f"(({soft_skills_query})^{overall_soft_skills_weight})" if soft_skills_query else ""
    print("the soft skills query is ",soft_skills_query) 

    # Location
    location_query = ""
    if filters.location:
        location_parts = []
        if filters.location.first_priority:
            location_parts.append(f'locations_list:"{filters.location.first_priority}"^2')
            # Second priority location
        if filters.location.second_priority:
            location_parts.append(f'locations_list:"{filters.location.second_priority}"^1') 
        
        location_query = " OR ".join(location_parts)

    # Transition Behaviour
    transition_behaviour_query_parts = []
    overall_transition_behaviour_weight = 0
    if filters.transition_behaviour and filters.transition_behaviour[0].name:
        for behaviour in filters.transition_behaviour:
            weight = PREFERENCE_WEIGHTS.get(behaviour.preference.lower(), 0) * behaviour.value
            if behaviour.value > 5:
                range_query = f"transition_behaviour:[6 TO 50]^{weight}"
            else:
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
            weight = PREFERENCE_WEIGHTS.get(advanced_filter.preference.lower(), 0) * 10
            if field_name.lower() == "company size":
                advanced_filter_queries.append(f'company_size:"{advanced_filter.value}"^{weight}')
            elif field_name.lower() == "team size":
                advanced_filter_queries.append(f'team_size:"{advanced_filter.value}"^{weight}')

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
    return final_query , exclusion_query