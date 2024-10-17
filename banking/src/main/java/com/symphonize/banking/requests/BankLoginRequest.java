package com.symphonize.banking.requests;

public class BankLoginRequest {

	String AccountNumber;
	
	public BankLoginRequest() {
		
	}
	
	public BankLoginRequest(String accountnumber) {
		super();
		this.AccountNumber=accountnumber;
		
	}
	
	public void setAccountNumber(String accountnumber) {
		this.AccountNumber=accountnumber;
	}
	
	public String getaccountNumber() {
		return this.AccountNumber;
	}
	
	
}
