package com.jobs.bitlabs.service;

import java.util.List;

import com.jobs.bitlabs.entity.CompanyProfile;

public interface CompanyProfileService {

	CompanyProfile createCompanyProfile(CompanyProfile companyprofile);
	
	List<CompanyProfile> getAllCompanyProfiles();
	
	String deleteCompanyProfile(String CompanyId);
}
