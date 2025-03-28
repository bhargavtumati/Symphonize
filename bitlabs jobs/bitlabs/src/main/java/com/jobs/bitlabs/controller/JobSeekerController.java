package com.jobs.bitlabs.controller;

import java.io.IOException;
import java.util.Date;
import java.util.List;
import java.util.Set;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.dto.JobSeekerDto;
import com.jobs.bitlabs.enums.JobStatus;
import com.jobs.bitlabs.enums.PrefferedLocation;
import com.jobs.bitlabs.enums.Qualification;
import com.jobs.bitlabs.enums.Skills;

import com.jobs.bitlabs.payloads.Address;
import com.jobs.bitlabs.service.JobSeekerService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;



@Tag(name = "Job Seekers", description = "profile ")
@RestController
@RequestMapping("bitlabs.com/jobSeekers")
public class JobSeekerController {

	@Autowired
	private JobSeekerService JobSeekerService;

	  @Operation(summary = "Create a new Job Seeker profile")
	    @ApiResponses(value = {
	            @ApiResponse(responseCode = "200", description = "Job Profile created",
	                    content = @Content(schema = @Schema(implementation = CompanyProfileDto.class))),
	            @ApiResponse(responseCode = "500", description = "Internal server error")
	    })
	  @PostMapping(value = "/createProfile", consumes = {"multipart/form-data"})
	  public ResponseEntity<JobSeekerDto> createJobSeekerProfile(
	          @RequestParam Long id,
	          @RequestParam String name,
	          @RequestParam String email,
	          @RequestParam String whatsappnumber,
	          @RequestParam Qualification qualification,
	          @RequestParam String specialization,
	          @RequestParam int totalExperience,
	          @RequestParam Set<PrefferedLocation> PreferedJobLocation,
	          @RequestParam String addressLine,
	            @RequestParam String city,
	            @RequestParam String state,
	            @RequestParam String pinCode,
	            @RequestParam String alternateMobile,

	          @RequestParam
	          @Parameter(description = "Date in the format dd-MM-yyyy", 
	                     schema = @Schema(type = "string", format = "date", example = "13-06-2002"))
	          @DateTimeFormat(pattern = "dd-MM-yyyy") Date dateOfBirth,
	          
	          @RequestParam Set<Skills> skills,
	          @RequestParam("profileImage") MultipartFile profileImage,
	          @RequestParam("resume") MultipartFile resume
	  ) {

	        try {
	            // Ensure your CompanyProfileDto constructor matches the provided parameters
	        	Address jobseekerAddress =new Address(addressLine,city,state,pinCode,alternateMobile);
	            JobSeekerDto JobSeekerDto = new JobSeekerDto(id, name, email, whatsappnumber, qualification, specialization, totalExperience, PreferedJobLocation, jobseekerAddress, dateOfBirth, skills, profileImage.getBytes(), resume.getBytes());
	            JobSeekerDto savedJobSeekerDto = JobSeekerService.createJobSeekerProfile(JobSeekerDto);
	            return new ResponseEntity<>(savedJobSeekerDto, HttpStatus.CREATED);
	        } catch (IOException e) {
	            // Optional: Add logging here to track the error
	            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
	        }
	    }
	@Operation(summary = "Get the JobSeeker by Id")
	@GetMapping("/getbyid")
	public ResponseEntity<JobSeekerDto> getById( @RequestParam Long id) {
		JobSeekerDto userDto = this.JobSeekerService.getUserById(id);
		return new ResponseEntity<JobSeekerDto>(userDto, HttpStatus.OK);
	}

	
	  @Operation(summary = "Update Job Seeker profile")
	    @ApiResponses(value = {
	            @ApiResponse(responseCode = "200", description = "Job Profile Updated",
	                    content = @Content(schema = @Schema(implementation = CompanyProfileDto.class))),
	            @ApiResponse(responseCode = "500", description = "Internal server error")
	    })
	  @PutMapping(value = "/updateProfile", consumes = {"multipart/form-data"})
	  public ResponseEntity<JobSeekerDto> updateProfile(
	          @RequestParam Long id,
	          @RequestParam String name,
	          @RequestParam String email,
	          @RequestParam String whatsappnumber,
	          @RequestParam Qualification qualification,
	          @RequestParam String specialization,
	          @RequestParam int totalExperience,
	          @RequestParam Set<PrefferedLocation> PreferedJobLocation,
	          @RequestParam String addressLine,
	            @RequestParam String city,
	            @RequestParam String state,
	            @RequestParam String pinCode,
	            @RequestParam String alternateMobile,

	          @RequestParam
	          @Parameter(description = "Date in the format dd-MM-yyyy", 
	                     schema = @Schema(type = "string", format = "date", example = "13-06-2002"))
	          @DateTimeFormat(pattern = "dd-MM-yyyy") Date dateOfBirth,
	          
	          @RequestParam Set<Skills> skills,
	          @RequestParam("profileImage") MultipartFile profileImage,
	          @RequestParam("resume") MultipartFile resume
	  ) {

	        try {
	            // Ensure your CompanyProfileDto constructor matches the provided parameters
	        	Address jobseekerAddress =new Address(addressLine,city,state,pinCode,alternateMobile);
	            JobSeekerDto JobSeekerDto = new JobSeekerDto(id, name, email, whatsappnumber, qualification, specialization, totalExperience, PreferedJobLocation, jobseekerAddress, dateOfBirth, skills, profileImage.getBytes(), resume.getBytes());
	            
	            JobSeekerDto updatedUser = JobSeekerService.updateUser(JobSeekerDto.getId(), JobSeekerDto);
	       
	            return new ResponseEntity<>(updatedUser, HttpStatus.OK);
	        } catch (IOException e) {
	            // Optional: Add logging here to track the error
	            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
	        }
	    }
	
	@Operation(summary = "Apply Job")
	@PutMapping("/applyjob ")
	public ResponseEntity<String> applyJob( @RequestParam Long jobseekerid, @RequestParam String CompanyJobId ) {
		
		String status= JobSeekerService.applyForJob(jobseekerid, CompanyJobId);
		return new ResponseEntity<>(status, HttpStatus.OK);
	}


	@Operation(summary = "Recomanded Jobs")
	@GetMapping("/RecommendedJobs")
	public ResponseEntity<List<CompanyJobDto>> getRecommendedJobs(@RequestParam Long jobseekerId) {
		List<CompanyJobDto> list= JobSeekerService.getRecommendedJobs(jobseekerId);
		
		return new ResponseEntity<>(list, HttpStatus.OK);
	}
	
	@Operation(summary = "View Status")
	@GetMapping("/viewStatus")
	public ResponseEntity<JobStatus> getStatus(@RequestParam Long jobseekerId,@RequestParam String companyjobid) {
		JobStatus status= JobSeekerService.viewJobStatus(companyjobid,  jobseekerId);
		
		return new ResponseEntity<>(status, HttpStatus.OK);
	}
	

}
