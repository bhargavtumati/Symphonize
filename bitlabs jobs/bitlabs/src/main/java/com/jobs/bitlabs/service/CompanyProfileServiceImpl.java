package com.jobs.bitlabs.service;

import java.util.Optional;
import java.util.regex.Pattern;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.dto.CompanyProfileDtoMapper;
import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.exception.CustomException;
import com.jobs.bitlabs.repo.CompanyProfileRepo;

@Service
public class CompanyProfileServiceImpl implements CompanyProfileService {

	@Autowired
    private CompanyProfileRepo companyProfileRepo;
   

   


    public CompanyProfileServiceImpl(CompanyProfileRepo companyProfileRepo) {
        this.companyProfileRepo = companyProfileRepo;
    }
    
    
    private static final Pattern SPECIAL_CHAR_PATTERN = Pattern.compile("[^a-zA-Z0-9 ]");
    
    public CompanyProfileDto saveCompanyProfile(CompanyProfileDto companyProfiledto) {
    	
    	if (SPECIAL_CHAR_PATTERN.matcher(companyProfiledto.getCompanyId()).find()) {
			throw new CustomException("Company ID contains special characters: " + companyProfiledto.getCompanyId()); 
			}
		if (companyProfileRepo.existsById(companyProfiledto.getCompanyId())) { 
			throw new CustomException("Company ID already exists: " + companyProfiledto.getCompanyId()); 
			} 
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyProfiledto.getCompanyName()).find()) {
			throw new CustomException("Company Name contains special characters: " + companyProfiledto.getCompanyName()); 
			}
		 
    	CompanyProfile companyprofile = CompanyProfileDtoMapper.mapToCompanyProfile(companyProfiledto);
		CompanyProfile savedCompanyProfile = companyProfileRepo.save(companyprofile);
		
		return CompanyProfileDtoMapper.mapToCompanyProfileDto(savedCompanyProfile);
        
    }
    
    public CompanyProfileDto updateProfile( CompanyProfileDto companyProfiledto) {
    	
    	this.companyProfileRepo.findById( companyProfiledto.getCompanyId())
    			.orElseThrow(() -> new CustomException("company not found with id: " + companyProfiledto.getCompanyId()));
    	
    	
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyProfiledto.getCompanyName()).find()) {
			throw new CustomException("Company Name contains special characters: " + companyProfiledto.getCompanyName()); 
			}
		
		
    	CompanyProfile updatedcompanyprofile = CompanyProfileDtoMapper.mapToCompanyProfile(companyProfiledto);
		
		
		CompanyProfile savedCompanyProfile = companyProfileRepo.save(updatedcompanyprofile);
		
		return CompanyProfileDtoMapper.mapToCompanyProfileDto(savedCompanyProfile);
        
    }

    public Optional<CompanyProfileDto> getCompanyProfileById(String companyId) {
    	CompanyProfile companyprofile = this.companyProfileRepo.findById(companyId)
    			.orElseThrow(() -> new CustomException("company not found with id: " + companyId));
        
    	return Optional.of(CompanyProfileDtoMapper.mapToCompanyProfileDto(companyprofile));

    }

    public void deleteCompanyProfile(String companyId) {
        companyProfileRepo.deleteById(companyId);
    }
}