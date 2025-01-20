package com.springboot.VirtualBookStrore.Controller;



import java.util.List;


import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.VirtualBookStrore.Entity.AssignBookRequest;
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


	// Add Book REST API
	@PostMapping("/addBook")
	public Library addBook(@RequestBody Library library){
		
        if (library.getAvailabilty()) { if (library.getUserName() != null || library.getPhoneNumber() != 0) { 
			throw new IllegalArgumentException("Username and phone number should not be provided if the book is available.");
		 } } 
		 else { if (library.getUserName() == null && library.getPhoneNumber() == 0) { 
			throw new IllegalArgumentException("Username and phone number must be provided if the book is not available.");
		 } }

		libraryservice.addBook(library);
		return library;
		
	}
	// get Availability REST API
	@GetMapping("/getAvailability/{Id}")
	public Library getAvailability(@PathVariable Long Id) {
		
		Library library = libraryservice.getAvailabity(Id);
		return library;
	}
	
	
	//get All Books REST API
	@GetMapping("/getAllBooks")
	public List<Library> getAllBooks() {
		
		List<Library> library = libraryservice.getAllBooks();
		return library;
	}
	

	// Assign Book Rest API
    @PutMapping("/assignBook/{Id}")
    public Library assignBook(@PathVariable Long Id, @RequestBody AssignBookRequest request) {
    String userName = request.getUserName();
    Long phoneNumber = request.getPhoneNumber();
    Boolean availability = false;

    Library library = libraryservice.AssignBook(Id, userName, availability, phoneNumber);
    return library;
    }

	
	
	@PutMapping("/changeAvailability/{Id}")
	public String changeAvailability(@PathVariable Long Id) {
		
		String username = "";
		String message = libraryservice.changeAvailability(Id, username, true);
		return message;
	}
	
	@GetMapping("/getPaginatedLibraries") 
	public Page<Library> getPaginatedLibraries( @RequestParam(value = "page", defaultValue = "0") int page, @RequestParam(value = "size", defaultValue = "10") int size) {
		return libraryservice.getPaginatedLibraries(page, size); 
		}
	
	@DeleteMapping("/deleteBook/{Id}")
	public String DeleteBook(@PathVariable Long Id) {
		
		String message = libraryservice.deleteBook(Id);
		return message;
	}
	
	

	
	
	
	
}
