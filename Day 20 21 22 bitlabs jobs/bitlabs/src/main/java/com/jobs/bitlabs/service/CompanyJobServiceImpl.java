package com.jobs.bitlabs.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.repo.CompanyJobRepo;
import com.jobs.bitlabs.repo.CompanyProfileRepo;
import com.jobs.bitlabs.exception.CompanyIdNotYetRegisteredException;
import com.jobs.bitlabs.exception.InvalidTitleException; 
import com.jobs.bitlabs.exception.JobIdAlreadyExistsException; 
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
			throw new InvalidTitleException("Job ID contains special characters: " + companyjob.getJobId()); 
			}
		if (companyjobrepo.existsById(companyjob.getJobId())) { 
			throw new JobIdAlreadyExistsException("Job ID already exists: " + companyjob.getJobId()); 
			} 
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyjob.getJobTitle()).find()) {
			throw new InvalidTitleException("Job Title contains special characters: " + companyjob.getJobTitle()); 
			}
		if (companyjob.getJobDescription().equals(null)) {
			throw new InvalidTitleException("Job Description is null: " + companyjob.getJobDescription()); 
			}
		if (!companyprofilerepo.existsById(companyjob.getCompanyId())) {
			throw new CompanyIdNotYetRegisteredException("Company not yet registered: please register " + companyjob.getCompanyId()); 
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
