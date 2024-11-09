package com.jobs.bitlabs.dto;

import java.util.Date;


import com.jobs.bitlabs.payloads.CompanyAddress;






public class CompanyProfileDto {

 
	
	    private String CompanyId;
	    private String CompanyName;
	    private String CompanyMail;
	    private String profileImage;
	    private String RecruiterName;
	    private Long CompanyMobileNumber;
	  
		private CompanyAddress companyaddress;
	 
	    private Date registeredDate;

	    public CompanyProfileDto() {
	        super();
	    }



		public CompanyProfileDto(String companyId, String companyName, String companyMail, String profileImage,
				String recruiterName, Long companyMobileNumber, CompanyAddress companyaddress, Date registeredDate) {
			super();
			CompanyId = companyId;
			CompanyName = companyName;
			CompanyMail = companyMail;
			this.profileImage = profileImage;
			RecruiterName = recruiterName;
			CompanyMobileNumber = companyMobileNumber;
			this.companyaddress = companyaddress;
			this.registeredDate = registeredDate;
		}


		public String getProfileImage() {
			return profileImage;
		}



		public void setProfileImage(String profileImage) {
			this.profileImage = profileImage;
		}



		public String getCompanyId() {
			return CompanyId;
		}

		public void setCompanyId(String companyId) {
			CompanyId = companyId;
		}

		public String getCompanyName() {
			return CompanyName;
		}

		public void setCompanyName(String companyName) {
			CompanyName = companyName;
		}

		public String getCompanyMail() {
			return CompanyMail;
		}

		public void setCompanyMail(String companyMail) {
			CompanyMail = companyMail;
		}


		public String getRecruiterName() {
			return RecruiterName;
		}

		public void setRecruiterName(String recruiterName) {
			RecruiterName = recruiterName;
		}

		public Long getCompanyMobileNumber() {
			return CompanyMobileNumber;
		}

		public void setCompanyMobileNumber(Long companyMobileNumber) {
			CompanyMobileNumber = companyMobileNumber;
		}

		public CompanyAddress getCompanyaddress() {
			return companyaddress;
		}

		public void setCompanyaddress(CompanyAddress companyaddress) {
			this.companyaddress = companyaddress;
		}

		public Date getRegisteredDate() {
			return registeredDate;
		}

		public void setRegisteredDate(Date registeredDate) {
			this.registeredDate = registeredDate;
		}

	

    
}
