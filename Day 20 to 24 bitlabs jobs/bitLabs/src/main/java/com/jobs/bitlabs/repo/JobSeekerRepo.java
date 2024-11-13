package com.jobs.bitlabs.repo;

import org.springframework.data.jpa.repository.JpaRepository;

import com.jobs.bitlabs.entity.JobSeeker;

public interface JobSeekerRepo extends JpaRepository<JobSeeker, Long>{

}
