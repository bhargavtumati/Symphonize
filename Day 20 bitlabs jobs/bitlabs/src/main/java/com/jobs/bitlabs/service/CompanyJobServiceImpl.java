package com.jobs.bitlabs.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.repo.CompanyJobRepo;
import com.jobs.bitlabs.repo.CompanyProfileRepo;

@Service
public class CompanyJobServiceImpl implements CompanyJobService {

	@Autowired
	private CompanyJobRepo companyjobrepo;
	private CompanyProfileRepo companyprofilerepo;
	
	public CompanyJobServiceImpl() {
		super();
		
	}

	
	public CompanyJobServiceImpl(CompanyJobRepo companyjobrepo, CompanyProfileRepo companyprofilerepo) {
		super();
		this.companyjobrepo = companyjobrepo;
		this.companyprofilerepo =  companyprofilerepo;
	}



	public CompanyJob postJob(CompanyJob companyjob) {
		
		if (companyjobrepo.existsById(companyjob.getJobId())) { 
			throw new RuntimeException("Job Id already Exists");
		}
		if (companyprofilerepo.existsById(companyjob.getCompanyId())) { 
			throw new RuntimeException("Company Id already Exists");
		}
		return companyjobrepo.save(companyjob);
		}
	
	public List<CompanyJob> getAllJobs() {
		return companyjobrepo.findAll();
		}
}
