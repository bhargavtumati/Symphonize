package com.jobs.bitlabs.service;

import java.util.Optional;
import java.util.regex.Pattern;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.dto.CompanyProfileDtoMapper;
import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.exception.CustomException;
import com.jobs.bitlabs.repo.CompanyProfileRepository;

@Service
public class CompanyProfileServiceImpl implements CompanyProfileService {

    private final CompanyProfileRepository companyProfileRepository;

    @Autowired
    public CompanyProfileServiceImpl(CompanyProfileRepository companyProfileRepository) {
        this.companyProfileRepository = companyProfileRepository;
    }
    private static final Pattern SPECIAL_CHAR_PATTERN = Pattern.compile("[^a-zA-Z0-9 ]");
    
    public CompanyProfileDto saveCompanyProfile(CompanyProfileDto companyProfiledto) {
    	
    	if (SPECIAL_CHAR_PATTERN.matcher(companyProfiledto.getCompanyId()).find()) {
			throw new CustomException("Company ID contains special characters: " + companyProfiledto.getCompanyId()); 
			}
		if (companyProfileRepository.existsById(companyProfiledto.getCompanyId())) { 
			throw new CustomException("Company ID already exists: " + companyProfiledto.getCompanyId()); 
			} 
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyProfiledto.getCompanyName()).find()) {
			throw new CustomException("Job Title contains special characters: " + companyProfiledto.getCompanyName()); 
			}
		 
    	CompanyProfile companyprofile = CompanyProfileDtoMapper.mapToCompanyProfile(companyProfiledto);
		CompanyProfile savedCompanyProfile = companyProfileRepository.save(companyprofile);
		
		return CompanyProfileDtoMapper.mapToCompanyProfileDto(savedCompanyProfile);
        
    }

    public Optional<CompanyProfileDto> getCompanyProfileById(String companyId) {
    	Optional<CompanyProfile> optionalCompanyProfile = companyProfileRepository.findById(companyId);
         CompanyProfile companyprofile = optionalCompanyProfile.get();
    	return Optional.of(CompanyProfileDtoMapper.mapToCompanyProfileDto(companyprofile));

    }

    public void deleteCompanyProfile(String companyId) {
        companyProfileRepository.deleteById(companyId);
    }
}