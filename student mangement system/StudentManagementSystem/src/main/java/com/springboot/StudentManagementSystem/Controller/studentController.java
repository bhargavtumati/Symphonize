package com.springboot.StudentManagementSystem.Controller;


import java.util.List;



import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.springboot.StudentManagementSystem.Entity.Student;
import com.springboot.StudentManagementSystem.Service.studentService;





@RestController
@RequestMapping("/")
public class studentController {
	
	private studentService studentservice;
	
	
 
	public studentController(studentService service) {
		super();
		this.studentservice = service;
	}


	// Add Book REST API
	@PostMapping("/addStudent")
	public Student addBook(@RequestBody Student student){
		
		studentservice.addStudent(student);
		return student;
		
	}
	// get Availability REST API
	@GetMapping("/getStudentDetails/{Id}")
	public Student getAvailability(@PathVariable Long Id) {
		
		Student student = studentservice.getDetails(Id);
		return student;
	}
	
	//get All Books REST API
	@GetMapping("/getAllStudents")
	public List<Student> getAllBooks() {
		
		List<Student> student = studentservice.getAllStudents();
		return student;
	}
	

	
	@PutMapping("/changeDetails/{Id}")
	public Student changeAvailability(@PathVariable Long Id, @RequestBody Student student) {
		
		
		Student savedstudent = studentservice.changeDetails(Id, student);
		return savedstudent;
	}
	
	@DeleteMapping("/deleteStudent/{Id}")
	public String DeleteBook(@PathVariable Long Id) {
		
		String message = studentservice.deleteStudent(Id);
		return message;
	}
	
}

