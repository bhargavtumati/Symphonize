package com.jobs.bitlabs.service;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.entity.JobSeeker;
import com.jobs.bitlabs.enums.JobStatus;

public interface CompanyJobService {

	CompanyJobDto postJob(CompanyJobDto companyjobdto);
	
	List<CompanyJobDto> getAllJobs();
	
	void deleteByJobId(String JobId);
	
	int getApplicantsCount() ;
	
	int getCountOfActiveJobs();
	
	String changeJobSeekerJobStatus(String companyjobid, Long jobseekerId, JobStatus changedstatus) ;

	List<JobSeeker> FilterData(Long Experience, String companyjobid) throws IOException;
 
	 CompanyJobDto updateJob(CompanyJobDto companyjobdto);
	
	 Optional<CompanyJobDto> getCompanyJobById(String companyJobId);
	
}
