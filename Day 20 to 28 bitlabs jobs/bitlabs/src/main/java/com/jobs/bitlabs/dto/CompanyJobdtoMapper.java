package com.jobs.bitlabs.dto;


import com.jobs.bitlabs.entity.CompanyJob;

public class CompanyJobdtoMapper {
	public static CompanyJob mapToCompanyJob(CompanyJobDto companyjobdto) {
	    CompanyJob companyjob = new CompanyJob();
	    
	    companyjob.setJobId(companyjobdto.getJobId());
	    companyjob.setJobTitle(companyjobdto.getJobTitle());
	    companyjob.setJobDescription(companyjobdto.getJobDescription());
	    companyjob.setJobposteddate(companyjobdto.getJobposteddate());
	    companyjob.setCompanyId(companyjobdto.getCompanyId());
	    companyjob.setQualification(companyjobdto.getQualification());
	    companyjob.setExperienceMin(companyjobdto.getExperienceMin());
	    companyjob.setExperienceMax(companyjobdto.getExperienceMax());
	    companyjob.setSkills(companyjobdto.getSkills());
	    companyjob.setSalaryMin(companyjobdto.getSalaryMin());
	    companyjob.setSalaryMax(companyjobdto.getSalaryMax());
	    companyjob.setPreferdJobLocation(companyjobdto.getPreferdJobLocation());
	    companyjob.setJobType(companyjobdto.getJobType());
	    companyjob.setStatus(companyjobdto.getStatus());
	    
	    return companyjob;
	}

	public static CompanyJobDto mapToCompanyJobDto(CompanyJob companyjob) {
	    CompanyJobDto companyjobdto = new CompanyJobDto();
	    
	    companyjobdto.setJobId(companyjob.getJobId());
	    companyjobdto.setJobTitle(companyjob.getJobTitle());
	    companyjobdto.setJobDescription(companyjob.getJobDescription());
	    companyjobdto.setJobposteddate(companyjob.getJobposteddate());
	    companyjobdto.setCompanyId(companyjob.getCompanyId());
	    companyjobdto.setQualification(companyjob.getQualification());
	    companyjobdto.setExperienceMin(companyjob.getExperienceMin());
	    companyjobdto.setExperienceMax(companyjob.getExperienceMax());
	    companyjobdto.setSkills(companyjob.getSkills());
	    companyjobdto.setSalaryMin(companyjob.getSalaryMin());
	    companyjobdto.setSalaryMax(companyjob.getSalaryMax());
	    companyjobdto.setPreferdJobLocation(companyjob.getPreferdJobLocation());
	    companyjobdto.setJobType(companyjob.getJobType());
	    companyjobdto.setStatus(companyjob.getStatus());
	    
	    return companyjobdto;
	}


}