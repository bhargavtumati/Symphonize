package com.jobs.bitlabs.payloads;

import jakarta.persistence.Embeddable;

@Embeddable
public class CompanyAddress {

	
	private String addressLine;
    private String city;
    private String state;
    private String pinCode;
    private String alternateMobile;

    
    
    
    public CompanyAddress(String addressLine, String city, String state, String pinCode, String alternateMobile) {
		super();
		this.addressLine = addressLine;
		this.city = city;
		this.state = state;
		this.pinCode = pinCode;
		this.alternateMobile = alternateMobile;
	}

	// Getters and Setters
    public String getAddressLine() {
        return addressLine;
    }

    public void setAddressLine(String addressLine) {
        this.addressLine = addressLine;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }

    public String getPinCode() {
        return pinCode;
    }

    public void setPinCode(String pinCode) {
        this.pinCode = pinCode;
    }

    public String getAlternateMobile() {
        return alternateMobile;
    }

    public void setAlternateMobile(String alternateMobile) {
        this.alternateMobile = alternateMobile;
    }
}