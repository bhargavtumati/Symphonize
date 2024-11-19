package com.example.Patient.repo;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.Patient.entity.patient;

@Repository
public interface patientrepo extends JpaRepository<patient, Long> {

}
