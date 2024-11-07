package com.jobs.bitlabs.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.service.CompanyProfileService;


@RestController
@RequestMapping("bitlabs.com/companyProfile")
public class CompanyProfileController {
	
	@Autowired
	private CompanyProfileService companyprofileservice;
	
	
	
	public CompanyProfileController(CompanyProfileService companyprofileservice) {
		super();
		this.companyprofileservice = companyprofileservice;
	}



	@PostMapping("createProfile")
	public CompanyProfile createCompanyprofile(CompanyProfile companyprofile) {
		return companyprofileservice.createCompanyProfile(companyprofile);
		
	}
	
	@GetMapping("getAllCompanyProfiles")
	public List<CompanyProfile> getAllCompanyProfiles() {
		return companyprofileservice.getAllCompanyProfiles();
	}
	
	@DeleteMapping("/deleteCompanyProfile/{companyId}") 
	public String deleteCompanyProfile(@PathVariable("companyId") String companyId) { 
		return companyprofileservice.deleteCompanyProfile(companyId);
		}

}
