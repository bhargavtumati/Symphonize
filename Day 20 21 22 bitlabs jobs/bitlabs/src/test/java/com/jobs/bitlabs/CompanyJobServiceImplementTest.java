package com.jobs.bitlabs;

import org.mockito.InjectMocks;
import org.mockito.Mock;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.repo.CompanyJobRepo;
import com.jobs.bitlabs.service.CompanyJobServiceImpl;

public class CompanyJobServiceImplementTest {
	
	@Mock 
    private CompanyJobRepo companyjobrepo;
	
	
	@InjectMocks
	private CompanyJobServiceImpl companyserviceimpl;
	
	
	private CompanyJobDto companyjobdto;
	private CompanyJob companyjob;
	
	
	
}
