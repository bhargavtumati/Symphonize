package com.jobs.bitlabs.dto;

import com.jobs.bitlabs.entity.CompanyProfile;

public class CompanyProfileDtoMapper {

    // Maps from CompanyProfileDto to CompanyProfile entity
    public static CompanyProfile mapToCompanyProfile(CompanyProfileDto companyProfileDto) {
        CompanyProfile companyProfile = new CompanyProfile();
        
        companyProfile.setCompanyId(companyProfileDto.getCompanyId());
        companyProfile.setLogo(companyProfileDto.getLogo());
        companyProfile.setCompanyName(companyProfileDto.getCompanyName());
        companyProfile.setRecruiterName(companyProfileDto.getRecruiterName());
        companyProfile.setCompanyAddress(companyProfileDto.getCompanyAddress());
        companyProfile.setCompanyNumber(companyProfileDto.getCompanyNumber());
        
        return companyProfile;
    }

    // Maps from CompanyProfile entity to CompanyProfileDto
    public static CompanyProfileDto mapToCompanyProfileDto(CompanyProfile companyProfile) {
        CompanyProfileDto companyProfileDto = new CompanyProfileDto();
        
        companyProfileDto.setCompanyId(companyProfile.getCompanyId());
        companyProfileDto.setLogo(companyProfile.getLogo());
        companyProfileDto.setCompanyName(companyProfile.getCompanyName());
        companyProfileDto.setRecruiterName(companyProfile.getRecruiterName());
        companyProfileDto.setCompanyAddress(companyProfile.getCompanyAddress());
        companyProfileDto.setCompanyNumber(companyProfile.getCompanyNumber());
        
        return companyProfileDto;
    }
}
