package com.springboot.VirtualBookStrore.Service;

import org.springframework.stereotype.Service;

import com.springboot.VirtualBookStrore.Entity.Library;
import com.springboot.VirtualBookStrore.Repo.LibraryRepo;


@Service
public class LibraryService {
	
	public LibraryRepo libraryrepository; 
	
	public LibraryService(LibraryRepo libraryrepository) {
		super();
		this.libraryrepository = libraryrepository;
	}
	
	
	public Library addBook(Library library) {
		// TODO Auto-generated method stub
		
		Library savedAccount = libraryrepository.save(library);
		return savedAccount;
	}
	
	public Library getAvailabity(Long Id) {
		
		Library library = libraryrepository.findById(Id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		libraryrepository.save(library);
		return library;
		
	}
	
	
	public Library AssignBook(Long Id, String Name, boolean availability, Long phoneNumber) {
		
		Library library = libraryrepository.findById(Id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		library.setUserName(Name);
		library.setAvailabilty(availability);
		library.setPhoneNumber(phoneNumber);
		libraryrepository.save(library);
		return library;
		
	}
	
	public String deleteBook(Long Id) {
		Library library = libraryrepository.findById(Id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		libraryrepository.deleteById(library.getId());
		return "account deleted sucessfully";
		
	}
	
	public String changeAvailability(Long Id, String Name, boolean availability) {
		Library library = libraryrepository.findById(Id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		library.setUserName(Name);
		library.setAvailabilty(availability);
		libraryrepository.save(library);
		return "book id status changed";
	}

}
