package com.jobs.bitlabs.service;


import java.util.List;


import com.jobs.bitlabs.dto.CompanyProfileDto;

public interface CompanyProfileService {

	CompanyProfileDto createCompanyProfile(CompanyProfileDto companyProfileDto) ;
	
	List<CompanyProfileDto> getAllCompanyProfiles();
	
	String deleteCompanyProfile(String CompanyId);
}
