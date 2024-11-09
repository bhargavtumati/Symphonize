package com.jobs.bitlabs.dto;

import com.jobs.bitlabs.entity.CompanyProfile;


public class CompanyprofileDtoMapper {

    public static CompanyProfile mapToCompanyprofile(CompanyProfileDto companyprofiledto) {
        return new CompanyProfile(
        		companyprofiledto.getCompanyId(),
        		companyprofiledto.getCompanyName(),
        		companyprofiledto.getCompanyMail(),
        		companyprofiledto.getProfileImage(),
        		companyprofiledto.getRecruiterName(),
        		companyprofiledto.getCompanyMobileNumber(),
        		companyprofiledto.getCompanyaddress(),
        		companyprofiledto.getRegisteredDate()
        );
    }

    public static CompanyProfileDto mapToCompanyProfileDto(CompanyProfile companyProfile) {
        return new CompanyProfileDto(
                companyProfile.getCompanyId(),
                companyProfile.getCompanyName(),
                companyProfile.getCompanyMail(),
                companyProfile.getProfileImage(),
                companyProfile.getRecruiterName(),
                companyProfile.getCompanyMobileNumber(),
                companyProfile.getCompanyaddress(),
                companyProfile.getRegisteredDate()
        );
    }
}
