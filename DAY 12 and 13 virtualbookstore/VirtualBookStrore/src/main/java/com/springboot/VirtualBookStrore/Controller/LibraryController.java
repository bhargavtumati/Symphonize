package com.springboot.VirtualBookStrore.Controller;



import java.util.List;
import java.util.Map;

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
		
		libraryservice.addBook(library);
		return library;
		
	}
	// get Availability REST API
	@GetMapping("/getAvailability/{Id}")
	public Library getAvailability(@PathVariable Long Id) {
		
		Library library = libraryservice.getAvailabity(Id);
		return library;
	}
	
	@GetMapping("/getPaginatedLibraries") 
	public Page<Library> getPaginatedLibraries( @RequestParam(value = "page", defaultValue = "0") int page, @RequestParam(value = "size", defaultValue = "10") int size) {
		return libraryservice.getPaginatedLibraries(page, size); 
		}
	//get All Books REST API
	@GetMapping("/getAllBooks")
	public List<Library> getAllBooks() {
		
		List<Library> library = libraryservice.getAllBooks();
		return library;
	}
	

	// Assign Book Rest API
	@PutMapping("/assignBook/{Id}")
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
