package com.jobs.bitlabs.service;

import com.jobs.bitlabs.dto.CompanyProfileDto;

import java.util.Optional;

public interface CompanyProfileService  {

   CompanyProfileDto saveCompanyProfile(CompanyProfileDto companyProfiledto) ;

    Optional<CompanyProfileDto> getCompanyProfileById(String companyIddto) ;
    
    CompanyProfileDto updateProfile(CompanyProfileDto companyProfiledto);

    public void deleteCompanyProfile(String companyId);
}
