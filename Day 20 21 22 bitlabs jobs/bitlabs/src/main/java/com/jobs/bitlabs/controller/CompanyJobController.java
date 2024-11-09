package com.jobs.bitlabs.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.service.CompanyJobService;



@RestController
@RequestMapping("bitlabs.com/companyJob")
public class CompanyJobController {
	
	@Autowired
	private CompanyJobService companyjobservice;

	
	
	
	@PostMapping("postJob")
	public CompanyJobDto createjob(CompanyJobDto companyprofiledto) {
		
		return companyjobservice.postJob(companyprofiledto);
	}
	
	@GetMapping("getAllJobs")
	public List<CompanyJobDto> getAlljobs() {
		return companyjobservice.getAllJobs();
	}
	
	
	
	

}
