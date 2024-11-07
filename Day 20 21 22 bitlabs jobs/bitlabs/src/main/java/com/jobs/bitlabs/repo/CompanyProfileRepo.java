package com.jobs.bitlabs.repo;


import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.jobs.bitlabs.entity.CompanyProfile;

@Repository
public interface CompanyProfileRepo extends JpaRepository<CompanyProfile, String>{

}
