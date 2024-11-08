package com.jobs.bitlabs.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.exception.GeneralException;
import com.jobs.bitlabs.repo.CompanyJobRepo;
import com.jobs.bitlabs.repo.CompanyProfileRepo;

import java.util.regex.Pattern;


@Service
public class CompanyJobServiceImpl implements CompanyJobService {

	@Autowired
	private CompanyJobRepo companyjobrepo;
	@Autowired
	private CompanyProfileRepo companyprofilerepo;
	
	public CompanyJobServiceImpl() {
		super();
		
	}

	
	public CompanyJobServiceImpl(CompanyJobRepo companyjobrepo, CompanyProfileRepo companyprofilerepo) {
		super();
		this.companyjobrepo = companyjobrepo;
		this.companyprofilerepo =  companyprofilerepo;
	}

	private static final Pattern SPECIAL_CHAR_PATTERN = Pattern.compile("[^a-zA-Z0-9 ]");

	public CompanyJob postJob(CompanyJob companyjob) {
		if (SPECIAL_CHAR_PATTERN.matcher(companyjob.getJobId()).find()) {
			throw new GeneralException("Job ID contains special characters: " + companyjob.getJobId()); 
			}
		if (companyjobrepo.existsById(companyjob.getJobId())) { 
			throw new GeneralException("Job ID already exists: " + companyjob.getJobId()); 
			} 
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyjob.getJobTitle()).find()) {
			throw new GeneralException("Job Title contains special characters: " + companyjob.getJobTitle()); 
			}
		if (companyjob.getJobDescription().equals(null)) {
			throw new GeneralException("Job Description is null: " + companyjob.getJobDescription()); 
			}
		if (!companyprofilerepo.existsById(companyjob.getCompanyId())) {
			throw new GeneralException("Company not yet registered: please register " + companyjob.getCompanyId()); 
			} 
		
		
		 return companyjobrepo.save(companyjob); 
		}
	
	public List<CompanyJob> getAllJobs() {
		return companyjobrepo.findAll();
		}
	
	public void deleteByJobId(String JobId) {
		companyjobrepo.deleteById(JobId);
		}
}
