package com.springboot.StudentManagementSystem.Repo;

import org.springframework.data.jpa.repository.JpaRepository;

import com.springboot.StudentManagementSystem.Entity.Student;

public interface StudentRepo extends JpaRepository<Student, Long> {

}
