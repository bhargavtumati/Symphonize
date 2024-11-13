package com.jobs.bitlabs.service;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.dto.JobSeekerDto;
import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.entity.JobSeeker;
import com.jobs.bitlabs.enums.BTechSpecialization;
import com.jobs.bitlabs.enums.DegreeSpecialization;
import com.jobs.bitlabs.enums.DiplomaSpecialization;
import com.jobs.bitlabs.enums.IntermediateSpecialization;
import com.jobs.bitlabs.enums.MCASpecialization;
import com.jobs.bitlabs.enums.Qualification;
import com.jobs.bitlabs.enums.Skills;
import com.jobs.bitlabs.exception.CustomException;
import com.jobs.bitlabs.repo.CompanyJobRepo;
import com.jobs.bitlabs.repo.JobSeekerRepo;

@Service
public class JobSeekerServieceImpl implements JobSeekerService {

	@Autowired
	private JobSeekerRepo JobSeekerRepo;

	@Autowired
	private ModelMapper modelMapper;

	@Autowired
	private CompanyJobRepo companyJobRepo;
	
	
	

	public JobSeeker dtoToUser(JobSeekerDto userDto) {
		JobSeeker user = this.modelMapper.map(userDto, JobSeeker.class);
		return user;

	}

	public JobSeekerDto UserToDto(JobSeeker jobseeker) {
		JobSeekerDto userDto = this.modelMapper.map(jobseeker, JobSeekerDto.class);
		return userDto;
	}
	
	

	public CompanyJob dtoToJob(CompanyJobDto companyjobDto) {
		CompanyJob job = this.modelMapper.map(companyjobDto, CompanyJob.class);
		return job;

	}

	public CompanyJobDto JobToDto(CompanyJob companyjob) {
		CompanyJobDto jobDto = this.modelMapper.map(companyjob, CompanyJobDto.class);
		return jobDto;
	}

	@Override
	public JobSeekerDto createJobSeekerProfile(JobSeekerDto JobSeekerDto) {
		JobSeeker user = this.dtoToUser(JobSeekerDto);
		JobSeeker savedUser = this.JobSeekerRepo.save(user);
		return this.UserToDto(savedUser);
	}

	@Override
	public JobSeekerDto getUserById(Long userId) {

		JobSeeker user = this.JobSeekerRepo.findById(userId)
				.orElseThrow(() -> new CustomException("User not found with id: " + userId));
		return this.UserToDto(user);
	}

	@Override
	public boolean isValidSpecialization(Qualification qualification, String specialization) {

		switch (qualification) {
		case BTECH:
			return BTechSpecialization.valueOf(specialization) != null;
		case MCA:
			return MCASpecialization.valueOf(specialization) != null;
		case DEGREE:
			return DegreeSpecialization.valueOf(specialization) != null;
		case INTERMEDIATE:
			return IntermediateSpecialization.valueOf(specialization) != null;
		case DIPLOMA:
			return DiplomaSpecialization.valueOf(specialization) != null;
		default:
			return false;
		}

	}

	@Override
	public JobSeekerDto updateUser(Long jobseekerId, JobSeekerDto jobSeekerDto) {
		// TODO Auto-generated method stub
		JobSeeker jobseeker = this.JobSeekerRepo.findById(jobseekerId)
				.orElseThrow(() -> new CustomException("User not found with id: " + jobseekerId));
		jobseeker.setPreferdJobLocation(jobSeekerDto.getPreferdJobLocation());
		jobseeker.setName(jobSeekerDto.getName());
		jobseeker.setEmail(jobSeekerDto.getEmail());
		jobseeker.setWhatsappnumber(jobSeekerDto.getWhatsappnumber());
		jobseeker.setQualification(jobSeekerDto.getQualification());
		jobseeker.setSpecialization(jobSeekerDto.getSpecialization());

		jobseeker.setTotalExperience(jobSeekerDto.getTotalExperience());
		jobseeker.setSkills(jobSeekerDto.getSkills());
		jobseeker.setAddress(jobSeekerDto.getAddress());
		jobseeker.setDateOfBirth(jobSeekerDto.getDateOfBirth());
		jobseeker.setProfileImage(jobSeekerDto.getProfileImage());
		jobseeker.setResume(jobSeekerDto.getResume());

		JobSeekerRepo.save(jobseeker);

		return this.UserToDto(jobseeker);
	}

	
	public boolean isUserQualifiedForJob(JobSeekerDto user, CompanyJobDto job) {
 
		if (user.getQualification().ordinal() < job.getQualification().ordinal()) {
			return false;
		}
		Set<Skills> userSkills = user.getSkills();
	    Set<Skills> jobSkills = job.getSkills();
	    for (Skills skill : jobSkills) {
	       
	        
	        if (!userSkills.contains(skill)) {
	            throw new IllegalArgumentException("User lacks the required skills for this job.");
	        }
	    }
	    if(user.getTotalExperience()< job.getExperienceMin())return false;
		return true;
	}
	
	
	@Override
	public boolean applyForJob(Long userId, String jobId) {
	    JobSeeker user = JobSeekerRepo.findById(userId)
	            .orElseThrow(() -> new CustomException("User not found with id: " + userId));
	   CompanyJob job = companyJobRepo.findById(jobId)
	              .orElseThrow(() -> new CustomException("Job not found with id: " + jobId));
	   JobSeekerDto userDto = this.UserToDto(user);
	    CompanyJobDto jobDto = this.JobToDto(job);
	    if (isUserQualifiedForJob(userDto, jobDto)) {
	    	user.getAppliedJobs().add(job);
 
	        // Add the user to the job's list of applicants
	        job.getJobApplicants().add(user);
 
	        // Save the updated entities to the database
	        JobSeekerRepo.save(user);  // Persist the updated user
	        companyJobRepo.save(job);    
	        return true; 
	    }
	    return false; 
	}
	
	@Override
	public List<CompanyJobDto> getRecommendedJobs(Long userId) {
		JobSeeker user = this.JobSeekerRepo.findById(userId)
				.orElseThrow(() -> new CustomException("User not found with id: " + userId));
		List<CompanyJob> recommendedJobs = companyJobRepo.findAll().stream()
				.filter(job -> matchesUserProfile(user, job)).collect(Collectors.toList());
		return recommendedJobs.stream().map(this::JobToDto).collect(Collectors.toList());
	}
 
	private boolean matchesUserProfile(JobSeeker user, CompanyJob job) {
		// Checking if the user's qualification matches the job's qualification
		boolean matchesQualification = user.getQualification() != null
				&& user.getQualification().toString().equalsIgnoreCase(job.getQualification().toString());
 
		// Checking if the user's experience matches the job's experience range
		boolean matchesExperience = user.getTotalExperience() >= job.getExperienceMin()
				&& user.getTotalExperience() <= job.getExperienceMax();
 
		// Convert user skills (Set<Skills>) to List<String> for comparison with job's
		// skills (List<String>)
		List<String> userSkills = user.getSkills().stream().map(Enum::name).collect(Collectors.toList());
		List<String> jobSkills = job.getSkills().stream().map(Enum::name).collect(Collectors.toList());
		 
		// Checking if the user's skills match the job's required skills
		boolean matchesSkills = userSkills.containsAll(jobSkills);

 
		// Checking if the user's preferred job location contains the job's location
	
		boolean matchesLocation = user.getPreferdJobLocation() != null 
		        && job.getPreferdJobLocation() != null
		        && user.getPreferdJobLocation().stream()
		            .map(Enum::name)  // Convert user's enum values to string names
		            .anyMatch(location -> job.getPreferdJobLocation().stream()
		                .map(Enum::name)  // Convert job's enum values to string names
		                .anyMatch(jobLocation -> jobLocation.equals(location)));

		// Return true if all criteria match
		System.out.println(matchesQualification +" "+ matchesExperience+" "+ matchesSkills +" "+ matchesLocation);
		return matchesQualification && matchesExperience && matchesSkills && matchesLocation;
	}



}
