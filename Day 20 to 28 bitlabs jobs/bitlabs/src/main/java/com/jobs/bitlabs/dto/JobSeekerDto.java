package com.jobs.bitlabs.dto;

import java.util.Date;
import java.util.Set;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.jobs.bitlabs.enums.PefferedLocation;
import com.jobs.bitlabs.enums.Qualification;
import com.jobs.bitlabs.enums.Skills;
import com.jobs.bitlabs.payloads.Address;


import jakarta.persistence.ElementCollection;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Lob;
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;
import jakarta.validation.constraints.NotNull;

public class JobSeekerDto {

	private Long id;

	private String name;

	private String email; 

	private String whatsappnumber;
	
	
	@NotNull(message = "Qualification is required.")
	@Enumerated(EnumType.STRING)
	private Qualification qualification;

	private String specialization;

	private int totalExperience;

	// private ProfilePicture profilePicture;

	@ElementCollection
	@Enumerated(EnumType.STRING)
	private Set<PefferedLocation> PreferdJobLocation;

	
	private Address address;

	@JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "dd-MM-yyyy")
	@Temporal(TemporalType.DATE)
	private Date dateOfBirth;

	@ElementCollection
	@Enumerated(EnumType.STRING)
	private Set<Skills> skills;

	@Lob
	private byte[] profileImage;

	@Lob
	private byte[] resume;


	
	
	public JobSeekerDto() {
		super();
		// TODO Auto-generated constructor stub
	}

	public JobSeekerDto(Long id, String name, String email, String whatsappnumber,
			@NotNull(message = "Qualification is required.") Qualification qualification, String specialization,
			int totalExperience, Set<PefferedLocation> preferdJobLocation, Address address, Date dateOfBirth,
			Set<Skills> skills, byte[] profileImage, byte[] resume) {
		super();
		this.id = id;
		this.name = name;
		this.email = email;
		this.whatsappnumber = whatsappnumber;
		this.qualification = qualification;
		this.specialization = specialization;
		this.totalExperience = totalExperience;
		PreferdJobLocation = preferdJobLocation;
		this.address = address;
		this.dateOfBirth = dateOfBirth;
		this.skills = skills;
		this.profileImage = profileImage;
		this.resume = resume;
		
	}

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getWhatsappnumber() {
		return whatsappnumber;
	}

	public void setWhatsappnumber(String whatsappnumber) {
		this.whatsappnumber = whatsappnumber;
	}

	public Qualification getQualification() {
		return qualification;
	}

	public void setQualification(Qualification qualification) {
		this.qualification = qualification;
	}

	public String getSpecialization() {
		return specialization;
	}

	public void setSpecialization(String specialization) {
		this.specialization = specialization;
	}

	public int getTotalExperience() {
		return totalExperience;
	}

	public void setTotalExperience(int totalExperience) {
		this.totalExperience = totalExperience;
	}

	public Set<PefferedLocation> getPreferdJobLocation() {
		return PreferdJobLocation;
	}

	public void setPreferdJobLocation(Set<PefferedLocation> preferdJobLocation) {
		PreferdJobLocation = preferdJobLocation;
	}

	public Address getAddress() {
		return address;
	}

	public void setAddress(Address address) {
		this.address = address;
	}

	public Date getDateOfBirth() {
		return dateOfBirth;
	}

	public void setDateOfBirth(Date dateOfBirth) {
		this.dateOfBirth = dateOfBirth;
	}

	public Set<Skills> getSkills() {
		return skills;
	}

	public void setSkills(Set<Skills> skills) {
		this.skills = skills;
	}

	public byte[] getProfileImage() {
		return profileImage;
	}

	public void setProfileImage(byte[] profileImage) {
		this.profileImage = profileImage;
	}

	public byte[] getResume() {
		return resume;
	}

	public void setResume(byte[] resume) {
		this.resume = resume;
	}

	

	


	

}
