package com.jobs.bitlabs.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.repo.CompanyProfileRepo;

@Service
public class CompanyprofileServiceImpl implements CompanyProfileService {

	@Autowired
	private CompanyProfileRepo companyprofilerepo;
	
	public CompanyprofileServiceImpl() {
		super();
		
	}

	
	public CompanyprofileServiceImpl(CompanyProfileRepo companyprofilerepo) {
		super();
		this.companyprofilerepo = companyprofilerepo;
	}



	public CompanyProfile createCompanyProfile(CompanyProfile companyprofile) {
		
		if (companyprofilerepo.existsById(companyprofile.getCompanyId())) { 
			throw new RuntimeException("Company Id already Exists");
		}
			
		return companyprofilerepo.save(companyprofile);
		
	}
	
	public List<CompanyProfile> getAllCompanyProfiles() {
		return companyprofilerepo.findAll();
		}
}
