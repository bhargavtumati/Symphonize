package com.jobs.bitlabs.service;

import java.util.List;
import java.util.regex.Pattern;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.exception.CompanyIdAlreadyExistsException;
import com.jobs.bitlabs.exception.InvalidTitleException;
import com.jobs.bitlabs.repo.CompanyProfileRepo;




@Service
public class CompanyprofileServiceImpl implements CompanyProfileService {

	@Autowired
	private CompanyProfileRepo companyprofilerepo;
	
	public CompanyprofileServiceImpl() {
		super();	
	}
	
	public CompanyprofileServiceImpl(CompanyProfileRepo companyprofilerepo) {
		super();
		this.companyprofilerepo = companyprofilerepo;
	}

	private static final Pattern SPECIAL_CHAR_PATTERN = Pattern.compile("[^a-zA-Z0-9 ]");
	
	private static final Pattern EMAIL_PATTERN = Pattern.compile("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$");
	
	private static final Pattern MOBILE_NUMBER_PATTERN = Pattern.compile("^\\d{10}$");
	
    
	public CompanyProfile createCompanyProfile(CompanyProfile companyprofile) {
		if (companyprofilerepo.existsById(companyprofile.getCompanyId())) {
			throw new CompanyIdAlreadyExistsException("Company Id already exists: " + companyprofile.getCompanyId()); 
			} 
		if (SPECIAL_CHAR_PATTERN.matcher(companyprofile.getCompanyId()).find()) {
			throw new InvalidTitleException("Company Id contains special characters: " + companyprofile.getCompanyId()); 
			}
		if (SPECIAL_CHAR_PATTERN.matcher(companyprofile.getCompanyName()).find()) {
			throw new InvalidTitleException("Company Name contains special characters: " + companyprofile.getCompanyName()); 
			}
		if (!EMAIL_PATTERN.matcher(companyprofile.getCompanyMail()).find()) {
			throw new InvalidTitleException("Company Mail is not Valid: " + companyprofile.getCompanyMail()); 
			} 
		if (SPECIAL_CHAR_PATTERN.matcher(companyprofile.getRecruiterName()).find()) {
			throw new InvalidTitleException("Recruiter Name contains special characters: " + companyprofile.getRecruiterName()); 
			}
		String mobileNumberStr = String.valueOf(companyprofile.getCompanyMobileNumber());
		if (!MOBILE_NUMBER_PATTERN.matcher(mobileNumberStr).find() & mobileNumberStr.length()!=10) {
			throw new InvalidTitleException("Mobile Number Not valid: " + mobileNumberStr); 
			}
		if (companyprofile.getCompanyAddress().length()<90) {
			throw new InvalidTitleException("Please provide full Address. "); 
			}
		return companyprofilerepo.save(companyprofile);
	}
	
	public List<CompanyProfile> getAllCompanyProfiles() {
		return companyprofilerepo.findAll();
		}
	
	public String deleteCompanyProfile(String companyId) { 
		if (companyId == null || companyId.isEmpty()) {
			throw new InvalidTitleException("Company ID must not be null or empty");
			} 
		try { if (companyprofilerepo.existsById(companyId)) { 
			companyprofilerepo.deleteById(companyId); return "deleted"; 
			} 
		else { throw new InvalidTitleException("Company ID not found: " + companyId); 
		} 
		} 
		catch (Exception e) { 
			throw new RuntimeException("An error occurred while deleting the company profile", e); 
			} }
}
