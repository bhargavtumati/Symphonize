package com.jobs.bitlabs.service;

import java.util.List;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.dto.JobSeekerDto;
import com.jobs.bitlabs.enums.Qualification;

public interface JobSeekerService {

	JobSeekerDto createJobSeekerProfile(JobSeekerDto JobSeekerDto);
	JobSeekerDto getUserById(Long id);
	boolean applyForJob(Long userId, String jobId);
	boolean isValidSpecialization(Qualification qualification, String specialization);
	JobSeekerDto updateUser(Long id, JobSeekerDto userDto);
	
	List<CompanyJobDto> getRecommendedJobs(Long userId);
}
