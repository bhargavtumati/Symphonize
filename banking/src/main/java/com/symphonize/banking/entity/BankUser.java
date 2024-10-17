package com.symphonize.banking.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class BankUser {

	
	@Id
	String AccountNumber;
	String Name;
    double Balance;
    
    public BankUser() {
    	super();
    }
    
	public BankUser(String name, String accountNumber, double balance) {
		super();
		
		this.AccountNumber = accountNumber;
		this.Name = name;
		this.Balance = balance;
	}

	public String getAccountNumber() {
		return AccountNumber;
	}

	public void setAccountNumber(String accountNumber) {
		AccountNumber = accountNumber;
	}

	public String getName() {
		return Name;
	}

	public void setName(String name) {
		Name = name;
	}

	public double getBalance() {
		return Balance;
	}

	public void setBalance(double balance) {
		Balance = balance;
	}
	


    
    
    
}
