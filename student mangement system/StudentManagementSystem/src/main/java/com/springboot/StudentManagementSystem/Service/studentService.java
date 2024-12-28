package com.springboot.StudentManagementSystem.Service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.springboot.StudentManagementSystem.Entity.Student;
import com.springboot.StudentManagementSystem.Repo.StudentRepo;

@Service
public class studentService {
	
	private StudentRepo studentrepository;
	
    public studentService(StudentRepo studentrepository) {
    	super();
    	this.studentrepository = studentrepository;
    }
	public Student addStudent(Student student) {
		Student savedStudent = studentrepository.save(student);
		return savedStudent;
	}
	
	public Student getDetails(Long Id) {
		Student student = studentrepository.findById(Id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		
		return student;
	}
	
	public List<Student> getAllStudents() {
		List<Student> student = studentrepository.findAll();
		
		return student;
	}
	
	public Student changeDetails(Long Id, Student student) {
	Student savedstudent = studentrepository.findById(Id).orElseThrow(() -> new RuntimeException("Account does not exists"));
	   savedstudent.setId(student.getId());
	   savedstudent.setAge(student.getAge());
	   savedstudent.setGrade(student.getGrade());
	   savedstudent.setName(student.getName());
	   studentrepository.save(savedstudent);
	   return savedstudent;
     }
	public String deleteStudent(Long Id) {
		Student savedstudent = studentrepository.findById(Id).orElseThrow(() -> new RuntimeException("Account does not exists"));
		studentrepository.delete(savedstudent);
	   return "student acccount got deleted";
      }
}
