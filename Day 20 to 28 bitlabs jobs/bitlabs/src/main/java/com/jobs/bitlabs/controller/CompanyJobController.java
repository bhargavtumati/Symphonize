package com.jobs.bitlabs.controller;

import java.io.IOException;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.entity.JobSeeker;
import com.jobs.bitlabs.enums.JobStatus;
import com.jobs.bitlabs.enums.PefferedLocation;
import com.jobs.bitlabs.enums.Qualification;
import com.jobs.bitlabs.enums.Skills;
import com.jobs.bitlabs.service.CompanyJobService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;



@RestController
@RequestMapping("bitlabs.com/companyJob")
public class CompanyJobController {
	
	@Autowired
	private CompanyJobService companyjobservice;

	
	
	
	@PostMapping("postJob")
	public  ResponseEntity<CompanyJobDto> createjob(
			  @RequestParam  String JobId,
			  @RequestParam  String JobTitle,
			  @RequestParam  String JobDescription,
			  @RequestParam
		      @Parameter(description = "Date in the format dd-MM-yyyy", 
		                     schema = @Schema(type = "string", format = "date", example = "13-06-2002"))
		      @DateTimeFormat(pattern = "dd-MM-yyyy") Date jobposteddate,
		      @RequestParam  String CompanyId,
			  @RequestParam  Qualification Qualification,
			  @RequestParam  Long ExperienceMin,
			  @RequestParam  Long ExperienceMax,
			  @RequestParam  Set<Skills> Skills,
	          @RequestParam  Long SalaryMin,
			  @RequestParam  Long SalaryMax,
			  @RequestParam  Set<PefferedLocation> PreferedJobLocation,
			  @RequestParam  String JobType,
			  @RequestParam  Boolean Status
			
			
			) {
		
		return  new ResponseEntity<>(companyjobservice.postJob(new CompanyJobDto( JobId,  JobTitle,  JobDescription,  jobposteddate,  CompanyId,
				 Qualification, ExperienceMin, ExperienceMax,  Skills, SalaryMin,
				 SalaryMax, PreferedJobLocation,  JobType,  Status)), HttpStatus.OK);
		
	
	}
	
	
	@PutMapping("updateJob")
	public  ResponseEntity<CompanyJobDto> updatejob(
			  @RequestParam  String JobId,
			  @RequestParam  String JobTitle,
			  @RequestParam  String JobDescription,
			  @RequestParam
		      @Parameter(description = "Date in the format dd-MM-yyyy", 
		                     schema = @Schema(type = "string", format = "date", example = "13-06-2002"))
		      @DateTimeFormat(pattern = "dd-MM-yyyy") Date jobposteddate,
		      @RequestParam  String CompanyId,
			  @RequestParam  Qualification Qualification,
			  @RequestParam  Long ExperienceMin,
			  @RequestParam  Long ExperienceMax,
			  @RequestParam  Set<Skills> Skills,
	          @RequestParam  Long SalaryMin,
			  @RequestParam  Long SalaryMax,
			  @RequestParam  Set<PefferedLocation> PreferedJobLocation,
			  @RequestParam  String JobType,
			  @RequestParam  Boolean Status
			
			
			) {
		
		return  new ResponseEntity<>(companyjobservice.updateJob(new CompanyJobDto( JobId,  JobTitle,  JobDescription,  jobposteddate,  CompanyId,
				 Qualification, ExperienceMin, ExperienceMax,  Skills, SalaryMin,
				 SalaryMax, PreferedJobLocation,  JobType,  Status)), HttpStatus.OK);
		
	
	}
	@Operation(summary = "Get a Company Job by ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Found the Company Job",
                    content = @Content(schema = @Schema(implementation = CompanyProfileDto.class))),
            @ApiResponse(responseCode = "404", description = "Company Job not found")
    })
    @GetMapping("/getByID")
    public ResponseEntity<CompanyJobDto> getCompanyJobById(@RequestParam String companyjobId) {
        Optional<CompanyJobDto> companyJobDto = companyjobservice.getCompanyJobById(companyjobId);
        return companyJobDto.map(ResponseEntity::ok).orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
	
	@GetMapping("getAllJobs")
	public ResponseEntity<List<CompanyJobDto>> getAlljobs() {
		return new ResponseEntity<>(companyjobservice.getAllJobs(), HttpStatus.OK);
	}
	
	@DeleteMapping("deleteJob")
	public ResponseEntity<String> deleteJobById(@RequestParam String Jobid) {
		 companyjobservice.deleteByJobId(Jobid);
		 return new ResponseEntity<>("deleted", HttpStatus.OK);
	}
	
	@GetMapping("getCountOfApplicants")
	public ResponseEntity<Integer> getAllApplicants(){
		int applicants = companyjobservice.getApplicantsCount() ;
		 return new ResponseEntity<>(applicants, HttpStatus.OK);
		
	}
	

	@GetMapping("getCountOfActiveJobs")
	public ResponseEntity<Integer> getCountOfActiveJobs(){
		int activejobs = companyjobservice.getCountOfActiveJobs() ;
		 return new ResponseEntity<>(activejobs, HttpStatus.OK);
		
	}
	
	@Operation(summary = "Change Status of Applicant")
	@GetMapping("/changeStatus")
	public ResponseEntity<String> getStatus(@RequestParam Long jobseekerId,@RequestParam String companyjobid,@RequestParam JobStatus changedstatus ) {
		String status= companyjobservice.changeJobSeekerJobStatus(companyjobid,  jobseekerId, changedstatus);
		
		return new ResponseEntity<>(status, HttpStatus.OK);
	}
	
	
	@Operation(summary = "Filter Data by Experience")
	@GetMapping("/filterdata")
	public ResponseEntity<List<JobSeeker>> filterData(@RequestParam Long Experience,@RequestParam String companyjobid ) throws IOException{
		List<JobSeeker> shortlist = companyjobservice.FilterData(Experience,  companyjobid);
		
		return new ResponseEntity<>(shortlist, HttpStatus.OK);
	}
	
	
	

}
