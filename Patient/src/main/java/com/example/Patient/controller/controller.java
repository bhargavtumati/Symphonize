package com.example.Patient.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.Patient.entity.patient;
import com.example.Patient.service.patientservice;

@RestController
@RequestMapping("Patient")
public class controller {
	
	@Autowired
	private patientservice patservice;
	
	
	@PostMapping("savepatient")
	public boolean savePatient(patient p){
		return patservice.savepatient(p);
		
	}

	@GetMapping("getpatient")
	public patient getPatient(Long id){
		return patservice.getpatient(id);
		
	}
	@PutMapping("updatepatient")
	public boolean updatePatient(patient p){
		return patservice.updatePatient(p);
		
	}
	@DeleteMapping("deletepatient")
	public boolean deletePatient(Long id){
		return patservice.deletePatient(id);
	}
	
	
	
}
