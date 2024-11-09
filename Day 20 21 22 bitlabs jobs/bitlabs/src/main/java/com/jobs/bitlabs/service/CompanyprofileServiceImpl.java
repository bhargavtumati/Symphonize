package com.jobs.bitlabs.service;


import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.dto.CompanyprofileDtoMapper;
import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.exception.CustomException;
import com.jobs.bitlabs.repo.CompanyProfileRepo;




@Service
public class CompanyprofileServiceImpl implements CompanyProfileService {



	    @Autowired
	    private CompanyProfileRepo companyProfileRepo;

	    private static final Pattern SPECIAL_CHAR_PATTERN = Pattern.compile("[^a-zA-Z0-9]");
	    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[A-Za-z0-9+_.-]+@(.+)$");
	    private static final Pattern MOBILE_NUMBER_PATTERN = Pattern.compile("\\d{10}");

	    @Override
	    public CompanyProfileDto createCompanyProfile(CompanyProfileDto companyProfileDto) {
	    	 if (companyProfileDto.getCompanyId() == null || companyProfileDto.getCompanyId().isEmpty()) {
	    	        throw new CustomException("Company ID cannot be null or empty");
	    	    }
	        if (companyProfileRepo.existsById(companyProfileDto.getCompanyId())) {
	            throw new CustomException("Company Id already exists: " + companyProfileDto.getCompanyId());
	        }
	        if (SPECIAL_CHAR_PATTERN.matcher(companyProfileDto.getCompanyId()).find()) {
	            throw new CustomException("Company Id contains special characters: " + companyProfileDto.getCompanyId());
	        }
	        if (SPECIAL_CHAR_PATTERN.matcher(companyProfileDto.getCompanyName()).find()) {
	            throw new CustomException("Company Name contains special characters: " + companyProfileDto.getCompanyName());
	        }
	        if (!EMAIL_PATTERN.matcher(companyProfileDto.getCompanyMail()).find()) {
	            throw new CustomException("Company Mail is not valid: " + companyProfileDto.getCompanyMail());
	        }
	        if (SPECIAL_CHAR_PATTERN.matcher(companyProfileDto.getRecruiterName()).find()) {
	            throw new CustomException("Recruiter Name contains special characters: " + companyProfileDto.getRecruiterName());
	        }
	        String mobileNumberStr = String.valueOf(companyProfileDto.getCompanyMobileNumber());
	        if (!MOBILE_NUMBER_PATTERN.matcher(mobileNumberStr).find() || mobileNumberStr.length() != 10) {
	            throw new CustomException("Mobile Number not valid: " + mobileNumberStr);
	        }
	        if (companyProfileDto.getCompanyaddress().getAddressLine().equals(null)) {
	            throw new CustomException("Please provide full address.");
	        }

	        
	            CompanyProfile companyProfile = new CompanyProfile();
	            companyProfile.setCompanyId(companyProfileDto.getCompanyId());
	            companyProfile.setCompanyName(companyProfileDto.getCompanyName());
	            companyProfile.setCompanyMail(companyProfileDto.getCompanyMail());
	            companyProfile.setProfileImage(companyProfileDto.getProfileImage());
	            companyProfile.setRecruiterName(companyProfileDto.getRecruiterName());
	            companyProfile.setCompanyMobileNumber(companyProfileDto.getCompanyMobileNumber());
	            companyProfile.setCompanyaddress(companyProfileDto.getCompanyaddress());
	            companyProfile.setRegisteredDate(companyProfileDto.getRegisteredDate());

	            CompanyProfile savedProfile = companyProfileRepo.save(companyProfile);
	            return  CompanyprofileDtoMapper.mapToCompanyProfileDto(savedProfile);
	            
	       
	    }
	

	
	public List<CompanyProfileDto> getAllCompanyProfiles() {
		List<CompanyProfile> companyprofiles =  companyProfileRepo.findAll();
		return companyprofiles.stream().map((companyprofile)-> CompanyprofileDtoMapper.mapToCompanyProfileDto(companyprofile)).collect(Collectors.toList());
		}
	
	public String deleteCompanyProfile(String companyId) { 
		if (companyId == null || companyId.isEmpty()) {
			throw new CustomException("Company ID must not be null or empty");
			} 
		try { if (companyProfileRepo.existsById(companyId)) { 
			companyProfileRepo.deleteById(companyId); return "deleted"; 
			} 
		else { throw new CustomException("Company ID not found: " + companyId); 
		} 
		} 
		catch (Exception e) { 
			throw new RuntimeException("An error occurred while deleting the company profile", e); 
			} }


}
