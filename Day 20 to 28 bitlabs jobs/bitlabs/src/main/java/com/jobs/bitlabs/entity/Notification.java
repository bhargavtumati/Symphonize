package com.jobs.bitlabs.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Notification {
	
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;
    private String companyId;
    private String jobId;
    private Long applicantId;
    private String message;
    private LocalDateTime timestamp = LocalDateTime.now();
    
    //Constructors
    public Notification() {
		// TODO Auto-generated constructor stub
	}
    
	public Notification(Long id, String companyId, String jobId, Long applicantId, String message,
			LocalDateTime timestamp) {
		super();
		this.id = id;
		this.companyId=companyId;
		this.jobId = jobId;
		this.applicantId = applicantId;
		this.message = message;
		this.timestamp = timestamp;
	}
    
    
    
    





	// Getters and setters
	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getJobId() {
		return jobId;
	}
	public void setJobId(String jobId) {
		this.jobId = jobId;
	}
	public Long getApplicantId() {
		return applicantId;
	}
	public void setApplicantId(Long applicantId) {
		this.applicantId = applicantId;
	}
	public String getMessage() {
		return message;
	}
	public void setMessage(String message) {
		this.message = message;
	}
	public LocalDateTime getTimestamp() {
		return timestamp;
	}
	public void setTimestamp(LocalDateTime timestamp) {
		this.timestamp = timestamp;
	}

	public String getCompanyId() {
		return companyId;
	}

	public void setCompanyId(String companyId) {
		this.companyId = companyId;
	}

    
    
    
    
}
