package com.example.Patient.service;



import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.Patient.entity.patient;

@Service
public class patientservice {
	
	@Autowired
	private com.example.Patient.repo.patientrepo patientrepo;

	public boolean savepatient(patient patient) {
		 patientrepo.save(patient);
		 return true;
	}
	
	public patient getpatient(Long id) {
		return patientrepo.findById(id).get();
		
		
	}
	
	public boolean updatePatient(com.example.Patient.entity.patient patient) {
		patient p=patientrepo.findById(patient.getPatientid()).get();
		p=patient;
		patientrepo.save(p);
		return true;
		
	}
	
	public boolean deletePatient(Long id) {
		patient p = patientrepo.findById(id).get();
		
		patientrepo.delete(p);
		return true;
	}
	
	
	
}
