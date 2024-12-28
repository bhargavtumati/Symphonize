package com.jobs.bitlabs.dto;

import java.util.Date;
import java.util.Set;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.jobs.bitlabs.enums.PrefferedLocation;
import com.jobs.bitlabs.enums.Qualification;
import com.jobs.bitlabs.enums.Skills;

import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;

import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;
import jakarta.validation.constraints.NotNull;



public class CompanyJobDto {
	


	private String JobId;
	private String JobTitle;
    @Column(length = 5000)
	private String JobDescription;
	@JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "dd-MM-yyyy")
	@Temporal(TemporalType.DATE)
	private Date jobposteddate = new Date();
	private String CompanyId;
	@NotNull(message = "Qualification is required.")
	@Enumerated(EnumType.STRING)
    private Qualification Qualification;
	private Long ExperienceMin;
	private Long ExperienceMax;
	@ElementCollection
	@Enumerated(EnumType.STRING)
	private Set<Skills> Skills;
	private Long SalaryMin;
	private Long SalaryMax;
	@ElementCollection
	@Enumerated(EnumType.STRING)
	private Set<PrefferedLocation> PreferdJobLocation;
	private String JobType;
	private Boolean Status;
	
	

	
	public CompanyJobDto() {
		super();
		
	}


   
	public CompanyJobDto(String jobId, String jobTitle, String jobDescription, Date jobposteddate , String companyId,
			Qualification qualification, Long experienceMin, Long experienceMax,
			Set<com.jobs.bitlabs.enums.Skills> skills, Long salaryMin, Long salaryMax,
			Set<PrefferedLocation> preferdJobLocation, String jobType, Boolean status) {
		super();
		JobId = jobId;
		JobTitle = jobTitle;
		JobDescription = jobDescription;
		this.jobposteddate =  new Date();
		CompanyId = companyId;
		Qualification = qualification;
		ExperienceMin = experienceMin;
		ExperienceMax = experienceMax;
		Skills = skills;
		SalaryMin = salaryMin;
		SalaryMax = salaryMax;
		PreferdJobLocation = preferdJobLocation;
		JobType = jobType;
		Status = status;
	}




	public String getJobId() {
		return JobId;
	}




	public void setJobId(String jobId) {
		JobId = jobId;
	}




	public String getJobTitle() {
		return JobTitle;
	}




	public void setJobTitle(String jobTitle) {
		JobTitle = jobTitle;
	}




	public String getJobDescription() {
		return JobDescription;
	}




	public void setJobDescription(String jobDescription) {
		JobDescription = jobDescription;
	}




	public Date getJobposteddate() {
		return jobposteddate;
	}




	public void setJobposteddate(Date jobposteddate) {
		this.jobposteddate = jobposteddate;
	}




	public String getCompanyId() {
		return CompanyId;
	}




	public void setCompanyId(String companyId) {
		CompanyId = companyId;
	}




	public Qualification getQualification() {
		return Qualification;
	}




	public void setQualification(Qualification qualification) {
		Qualification = qualification;
	}




	public Long getExperienceMin() {
		return ExperienceMin;
	}




	public void setExperienceMin(Long experienceMin) {
		ExperienceMin = experienceMin;
	}




	public Long getExperienceMax() {
		return ExperienceMax;
	}




	public void setExperienceMax(Long experienceMax) {
		ExperienceMax = experienceMax;
	}




	public Set<Skills> getSkills() {
		return Skills;
	}




	public void setSkills(Set<Skills> skills) {
		Skills = skills;
	}




	public Long getSalaryMin() {
		return SalaryMin;
	}




	public void setSalaryMin(Long salaryMin) {
		SalaryMin = salaryMin;
	}




	public Long getSalaryMax() {
		return SalaryMax;
	}




	public void setSalaryMax(Long salaryMax) {
		SalaryMax = salaryMax;
	}




	public Set<PrefferedLocation> getPreferdJobLocation() {
		return PreferdJobLocation;
	}




	public void setPreferdJobLocation(Set<PrefferedLocation> preferdJobLocation) {
		PreferdJobLocation = preferdJobLocation;
	}




	public String getJobType() {
		return JobType;
	}




	public void setJobType(String jobType) {
		JobType = jobType;
	}




	public Boolean getStatus() {
		return Status;
	}




	public void setStatus(Boolean status) {
		Status = status;
	}


	
	
	

	






	
	
	
	
	
		

}
