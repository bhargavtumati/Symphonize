package com.jobs.bitlabs.repo;




import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.jobs.bitlabs.entity.CompanyJob;


@Repository
public interface CompanyJobRepo  extends JpaRepository<CompanyJob, String>{
	
}
