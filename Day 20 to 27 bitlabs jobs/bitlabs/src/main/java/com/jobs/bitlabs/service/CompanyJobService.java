package com.jobs.bitlabs.service;

import java.io.IOException;
import java.util.List;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.entity.JobSeeker;

public interface CompanyJobService {

	CompanyJobDto postJob(CompanyJobDto companyjobdto);
	
	List<CompanyJobDto> getAllJobs();
	
	void deleteByJobId(String JobId);
	
	int getApplicantsCount() ;
	
	int getCountOfActiveJobs();
	
	String changeJobSeekerJobStatus(String companyjobid, Long jobseekerId, String changedstatus) ;

	List<JobSeeker> FilterData(Long Experience, String companyjobid) throws IOException;

	

	
}
