package com.springboot.loginpage.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class users {
	
    @Id
	private String email;
	private String password;
	private String name;
	
public users( ) {
		
		super();
		
	}
	public users(String email, String name, String password ) {
		
		this.email = email;
		this.name = name;
		this.password = password;
		
	}
	public String getEmail() {
		return email;
	}
	public void setEmail(String email) {
		this.email = email;
	}
	public String getPassword() {
		return password;
	}
	public void setPassword(String password) {
		this.password = password;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	
}
