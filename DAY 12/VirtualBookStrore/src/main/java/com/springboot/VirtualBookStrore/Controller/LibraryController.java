package com.springboot.VirtualBookStrore.Controller;



import java.util.Map;


import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.VirtualBookStrore.Entity.Library;
import com.springboot.VirtualBookStrore.Service.LibraryService;



@RestController
@RequestMapping("/")
public class LibraryController {
	
	private LibraryService libraryservice;
	
	
 
	public LibraryController(LibraryService service) {
		super();
		this.libraryservice = service;
	}


	// Add Account REST API
	@PostMapping("/addBook")
	public Library addBook(@RequestBody Library library){
		
		libraryservice.addBook(library);
		return library;
		
	}
	
	@GetMapping("/getAvailability/{Id}")
	public Library getAvailabity(@PathVariable Long Id) {
		
		Library library = libraryservice.getAvailabity(Id);
		return library;
	}
	

	
	@PostMapping("/assignBook/{Id}")
	public Library assignBook(@PathVariable Long Id, @RequestBody Map<String, Object> request) {
	    String userName = (String) request.get("userName");
	    Long phoneNumber = ((Number) request.get("phoneNumber")).longValue();
	    Boolean availability = false;

	    Library library = libraryservice.AssignBook(Id, userName, availability, phoneNumber);
	    return library;
	}

	@DeleteMapping("/deleteBook/{Id}")
	public String DeleteBook(@PathVariable Long Id) {
		
		String message = libraryservice.deleteBook(Id);
		return message;
	}
	
	@PutMapping("/changeAvailability/{Id}")
	public String changeAvailability(@PathVariable Long Id) {
		
		String username = "";
		String message = libraryservice.changeAvailability(Id, username, true);
		return message;
	}
	
	
	

	
	
	
	
}
