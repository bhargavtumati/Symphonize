package com.springboot.banking.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;




@Table(name = "accounts")
@Entity
public class Account {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private long id;
	@Column(name="account_holder_name")
	private String AccountHolderName;
	@Column
	private double balance;
	
	public Account() {
		super();
	
	}
	public Account(long id, String accountHolderName, double balance) {
		super();
		this.id = id;
		AccountHolderName = accountHolderName;
		this.balance = balance;
	}
	public void setId(long id) {
		this.id = id;
	}
	public void setAccountHolderName(String accountHolderName) {
		AccountHolderName = accountHolderName;
	}
	public void setBalance(double balance) {
		this.balance = balance;
	}
	
	public long getId() {
		return id;
	}
	public String getAccountHolderName() {
		return AccountHolderName;
	}
	public double getBalance() {
		return balance;
	}
	
	}


	
	
	


