package com.jobs.bitlabs.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.service.CompanyJobService;


@RestController
@RequestMapping("bitlabs.com/companyJob")
public class CompanyJobController {
	
	@Autowired
	private CompanyJobService companyjobservice;

	public CompanyJobController(CompanyJobService companyjobservice) {
		super();
		this.companyjobservice = companyjobservice;
	}
	
	
	@PostMapping("postJob")
	public CompanyJob createjob(CompanyJob companyprofile) {
		return companyjobservice.postJob(companyprofile);
	}
	
	@GetMapping("getAllJobs")
	public List<CompanyJob> getAlljobs() {
		return companyjobservice.getAllJobs();
	}
	
	

}
