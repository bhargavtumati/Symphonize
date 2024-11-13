package com.jobs.bitlabs.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import java.util.Objects;

import com.jobs.bitlabs.payloads.Address;

@Entity
public class CompanyProfile {

    @Id
    private String companyId;

    @Lob
    private byte[] logo;
    
    private String companyName;

    private String recruiterName;
    
    
    private  Address companyAddress;
    
    
    private Long companyNumber;

    // Constructors
    public CompanyProfile() {
    	super();
    	
    }

    public CompanyProfile(String companyId, byte[] logo, String companyName, String recruiterName,
			Address companyAddress, Long companyNumber) {
		super();
		this.companyId = companyId;
		this.logo = logo;
		this.companyName = companyName;
		this.recruiterName = recruiterName;
		this.companyAddress = companyAddress;
		this.companyNumber = companyNumber;
	}

    // Getters and Setters
   
  
    public String getCompanyId() {
		return companyId;
	}

	public void setCompanyId(String companyId) {
		this.companyId = companyId;
	}

	public byte[] getLogo() {
		return logo;
	}

	public void setLogo(byte[] logo) {
		this.logo = logo;
	}

	public String getCompanyName() {
		return companyName;
	}

	public void setCompanyName(String companyName) {
		this.companyName = companyName;
	}

	public String getRecruiterName() {
		return recruiterName;
	}

	public void setRecruiterName(String recruiterName) {
		this.recruiterName = recruiterName;
	}

	public Address getCompanyAddress() {
		return companyAddress;
	}

	public void setCompanyAddress(Address companyAddress) {
		this.companyAddress = companyAddress;
	}

	public Long getCompanyNumber() {
		return companyNumber;
	}

	public void setCompanyNumber(Long companyNumber) {
		this.companyNumber = companyNumber;
	}

	
	// Equals and hashCode
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CompanyProfile that = (CompanyProfile) o;
        return Objects.equals(companyId, that.companyId);
    }
	@Override
    public int hashCode() {
        return Objects.hash(companyId);
    }
}
