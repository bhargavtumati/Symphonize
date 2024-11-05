package com.springboot.StudentManagementSystem.Entity;



import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Table(name = "Students")
@Entity
public class Student {

	@Id
	private Long id;
	@Column
	private String Name;
	private Long Age;
	private Long Grade;
	
	public Student() {
		super();
		
	}
	
	public Student(Long id, String name,Long age, Long grade) {
		super();
		this.id = id;
		Name = name;
		Age = age;
		Grade = grade;
	}
	public Long getId() {
		return id;
	}
	public void setId(Long id) {
		this.id = id;
	}
	public String getName() {
		return Name;
	}
	public void setName(String name) {
		Name = name;
	}
	public Long getAge() {
		return Age;
	}
	public void setAge(Long age) {
		Age = age;
	}
	public Long getGrade() {
		return Grade;
	}
	public void setGrade (Long grade) {
		Grade = grade;
	}
	
	
}
