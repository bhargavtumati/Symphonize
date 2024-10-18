package com.springboot.banking.dto;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Table(name = "accounts")
@Entity
public class AccountDto {
	
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private long id;
	@Column(name="account_holder_name")
	private String AccountHolderName;
	@Column
	private double balance;
	
	
	public AccountDto() {
		super();
		
	}
	
	public AccountDto(Long id, String accountHolderName, double balance) {
		super();
		this.id = id;
		AccountHolderName = accountHolderName;
		this.balance = balance;
	}
	
	public AccountDto( String accountHolderName, double balance) {
		super();
		
		AccountHolderName = accountHolderName;
		this.balance = balance;
	}
	public Long getId() {
		return id;
	}
	public void setId(Long id) {
		this.id = id;
	}
	public String getAccountHolderName() {
		return AccountHolderName;
	}
	public void setAccountHolderName(String accountHolderName) {
		AccountHolderName = accountHolderName;
	}
	public double getBalance() {
		return balance;
	}
	public void setBalance(double balance) {
		this.balance = balance;
	}
	
	

	
	
	
}
