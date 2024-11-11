package com.jobs.bitlabs.dto;

import java.util.Date;
import java.util.List;

import org.springframework.format.annotation.DateTimeFormat;

import jakarta.persistence.Column;
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;





public class CompanyJobDto {
	


	private String JobId;
	private String JobTitle;
	 @Column(length = 5000)
	private String JobDescription;
	@Temporal(TemporalType.DATE)
	@DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
	private Date jobposteddate;
	private String CompanyId;
    private String Qualification;
	private Long ExperienceMin;
	private Long ExperienceMax;
	private List<String> Skills;
	private Long SalaryMin;
	private Long SalaryMax;
	private String Location;
	private String JobType;
	private Boolean Status;
	
	public CompanyJobDto() {
		super();
		
	}

	public CompanyJobDto(String jobId, String jobTitle, String jobDescription, Date jobposteddate, String companyId,
			String qualification, Long experienceMin, Long experienceMax, List<String> skills, Long salaryMin,
			Long salaryMax, String location, String jobType, Boolean status) {
		super();
		JobId = jobId;
		JobTitle = jobTitle;
		JobDescription = jobDescription;
		this.jobposteddate = jobposteddate;
		CompanyId = companyId;
		Qualification = qualification;
		ExperienceMin = experienceMin;
		ExperienceMax = experienceMax;
		Skills = skills;
		SalaryMin = salaryMin;
		SalaryMax = salaryMax;
		Location = location;
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

	public String getQualification() {
		return Qualification;
	}

	public void setQualification(String qualification) {
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

	public List<String> getSkills() {
		return Skills;
	}

	public void setSkills(List<String> skills) {
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

	public String getLocation() {
		return Location;
	}

	public void setLocation(String location) {
		Location = location;
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
