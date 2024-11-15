package com.jobs.bitlabs.exception;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.dto.JobSeekerDto;


public class Response {
    private int status;
    private String message;
    private long timestamp;
    private CompanyJobDto companyjob;
    private JobSeekerDto jobseeker;
    private CompanyProfileDto companyprofile;

    // Constructors
    public Response() {}

    public Response(int status, String message, long timestamp) {
        this.status = status;
        this.message = message;
        this.timestamp = timestamp;
    }
    
    

    public Response(int status, String message, long timestamp, CompanyJobDto companyjob) {
		super();
		this.status = status;
		this.message = message;
		this.timestamp = timestamp;
		this.companyjob = companyjob;
	}

    
    
	public Response(int status, String message, long timestamp, CompanyProfileDto companyprofile) {
		super();
		this.status = status;
		this.message = message;
		this.timestamp = timestamp;
		this.companyprofile = companyprofile;
	}
	
	

	public Response(int status, String message, long timestamp, JobSeekerDto jobseeker) {
		super();
		this.status = status;
		this.message = message;
		this.timestamp = timestamp;
		this.jobseeker = jobseeker;
	}

	// Getters and setters
	
	
	
    public int getStatus() {
        return status;
    }

    public CompanyJobDto getCompanyjob() {
		return companyjob;
	}

	public void setCompanyjob(CompanyJobDto companyjob) {
		this.companyjob = companyjob;
	}

	public JobSeekerDto getJobseeker() {
		return jobseeker;
	}

	public void setJobseeker(JobSeekerDto jobseeker) {
		this.jobseeker = jobseeker;
	}

	public CompanyProfileDto getCompanyprofile() {
		return companyprofile;
	}

	public void setCompanyprofile(CompanyProfileDto companyprofile) {
		this.companyprofile = companyprofile;
	}

	public void setStatus(int status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }
}


