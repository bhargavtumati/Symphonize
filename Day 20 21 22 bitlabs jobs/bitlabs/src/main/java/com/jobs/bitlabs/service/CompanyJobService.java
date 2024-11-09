package com.jobs.bitlabs.service;

import java.util.List;

import com.jobs.bitlabs.dto.CompanyJobDto;

public interface CompanyJobService {

	CompanyJobDto postJob(CompanyJobDto companyjobdto);
	
	List<CompanyJobDto> getAllJobs();
	
	void deleteByJobId(String JobId);
}
