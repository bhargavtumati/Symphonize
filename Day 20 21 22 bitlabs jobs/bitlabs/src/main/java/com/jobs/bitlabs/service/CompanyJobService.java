package com.jobs.bitlabs.service;

import java.util.List;

import com.jobs.bitlabs.entity.CompanyJob;

public interface CompanyJobService {

	CompanyJob postJob(CompanyJob companyjob);
	
	List<CompanyJob> getAllJobs();
	
	void deleteByJobId(String JobId);
}
