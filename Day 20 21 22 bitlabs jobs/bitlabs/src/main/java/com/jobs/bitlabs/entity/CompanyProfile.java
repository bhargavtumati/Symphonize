package com.jobs.bitlabs.entity;

import java.util.Date;

import org.springframework.format.annotation.DateTimeFormat;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;


@Entity
public class CompanyProfile {

    @Id
    @Column(name = "CompanyId", updatable = false, nullable = false)
    private String CompanyId;
    private String CompanyName;
    private String CompanyMail;
    private String RecruiterName;
    private Long CompanyMobileNumber;
    @Column(length = 5000)
    private String CompanyAddress;
    @Temporal(TemporalType.DATE)
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private Date registeredDate;

    public CompanyProfile() {
        super();
    }

	public CompanyProfile(String companyId, String companyName, String companyMail, String recruiterName,
			Long companyMobileNumber, String companyAddress, Date registeredDate) {
		super();
		CompanyId = companyId;
		CompanyName = companyName;
		CompanyMail = companyMail;
		RecruiterName = recruiterName;
		CompanyMobileNumber = companyMobileNumber;
		CompanyAddress = companyAddress;
		this.registeredDate = registeredDate;
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

	public void setRecuriterName(String recuriterName) {
		RecruiterName = recuriterName;
	}

	public Long getCompanyMobileNumber() {
		return CompanyMobileNumber;
	}

	public void setCompanyMobileNumber(Long companyMobileNumber) {
		CompanyMobileNumber = companyMobileNumber;
	}

	public String getCompanyAddress() {
		return CompanyAddress;
	}

	public void setCompanyAddress(String companyAddress) {
		CompanyAddress = companyAddress;
	}

	public Date getRegisteredDate() {
		return registeredDate;
	}

	public void setRegisteredDate(Date registeredDate) {
		this.registeredDate = registeredDate;
	}

    
}
