package com.springboot.VirtualBookStrore.Entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Table(name = "Library")
@Entity
public class Library {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private long id;
	@Column(name= "BookName")
	private String bookName;
	@Column
	private String bookAuthor;
	@Column
	private Boolean availabilty;
	@Column
	private String userName;
	@Column
	private Long phoneNumber; 
	
	
	public Library() {
		super();
		
	}

	// use this attributees in json file
	public Library(long id, String bookName, String bookAuthor, Boolean availabilty, String userName,
			Long phoneNumber) {
		super();
		this.id = id;
		this.bookName = bookName;
		this.bookAuthor = bookAuthor;
		this.availabilty = availabilty;
		this.userName = userName;
		this.phoneNumber = phoneNumber;
	}


	public long getId() {
		return id;
	}


	public void setId(long id) {
		this.id = id;
	}


	public String getBookName() {
		return bookName;
	}


	public void setBookName(String bookName) {
		this.bookName = bookName;
	}


	public String getBookAuthor() {
		return bookAuthor;
	}


	public void setBookAuthor(String bookAuthor) {
		this.bookAuthor = bookAuthor;
	}


	public Boolean getAvailabilty() {
		return availabilty;
	}


	public void setAvailabilty(Boolean availabilty) {
		this.availabilty = availabilty;
	}


	public String getUserName() {
		return userName;
	}


	public void setUserName(String userName) {
		this.userName = userName;
	}


	public Long getPhoneNumber() {
		return phoneNumber;
	}


	public void setPhoneNumber(Long phoneNumber) {
		this.phoneNumber = phoneNumber;
	}

  
	
	
	
	
	
	
	
	
	
	
}
