package com.jobs.bitlabs.service;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.exception.CustomException;
import com.jobs.bitlabs.repo.CompanyJobRepo;
import com.jobs.bitlabs.repo.CompanyProfileRepo;
import com.jobs.bitlabs.repo.JobSeekerRepo;
import com.jobs.bitlabs.dto.CompanyJobdtoMapper;
import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.entity.JobSeeker;
import com.jobs.bitlabs.enums.JobStatus;


import java.util.regex.Pattern;
import java.util.stream.Collectors;


@Service
public class CompanyJobServiceImpl implements CompanyJobService {

	private CompanyProfileRepo companyprofilerepo;
	
	private CompanyJobRepo companyjobrepo;
	
	private JobSeekerRepo jobseekerrepo;
	

	public CompanyJobServiceImpl(CompanyProfileRepo companyprofilerepo, CompanyJobRepo companyjobrepo, JobSeekerRepo jobseekerrepo ) {
		super();
		this.companyprofilerepo =  companyprofilerepo;
		this.companyjobrepo = companyjobrepo;
		this.jobseekerrepo = jobseekerrepo;
	}

	private static final Pattern SPECIAL_CHAR_PATTERN = Pattern.compile("[^a-zA-Z0-9 ]");

	public CompanyJobDto postJob(CompanyJobDto companyjobdto) {
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyjobdto.getJobId()).find()) {
			throw new CustomException("Job ID contains special characters: " + companyjobdto.getJobId()); 
			}
		if (companyjobrepo.existsById(companyjobdto.getJobId())) { 
			throw new CustomException("Job ID already exists: " + companyjobdto.getJobId()); 
			} 
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyjobdto.getJobTitle()).find()) {
			throw new CustomException("Job Title contains special characters: " + companyjobdto.getJobTitle()); 
			}
		if (companyjobdto.getJobDescription().equals(null)) {
			throw new CustomException("Job Description is null: " + companyjobdto.getJobDescription()); 
			}
		if (!companyprofilerepo.existsById(companyjobdto.getCompanyId())) {
			throw new CustomException("Company not yet registered: please register " + companyjobdto.getCompanyId()); 
			} 
		
		CompanyJob companyjob = CompanyJobdtoMapper.mapToCompanyJob(companyjobdto);
		CompanyJob savedcompanyjob = companyjobrepo.save(companyjob);
		return CompanyJobdtoMapper.mapToCompanyJobDto(savedcompanyjob); 
		}
	
      public CompanyJobDto updateJob(CompanyJobDto companyjobdto) {
		
		
		if (!companyjobrepo.existsById(companyjobdto.getJobId())) { 
			throw new CustomException("Job ID doesnot exit: " + companyjobdto.getJobId()); 
			} 
		
		if (SPECIAL_CHAR_PATTERN.matcher(companyjobdto.getJobTitle()).find()) {
			throw new CustomException("Job Title contains special characters: " + companyjobdto.getJobTitle()); 
			}
		if (companyjobdto.getJobDescription().equals(null)) {
			throw new CustomException("Job Description is null: " + companyjobdto.getJobDescription()); 
			}
		if (!companyprofilerepo.existsById(companyjobdto.getCompanyId())) {
			throw new CustomException("Company not yet registered: please register " + companyjobdto.getCompanyId()); 
			} 
		
		CompanyJob companyjob = CompanyJobdtoMapper.mapToCompanyJob(companyjobdto);
		CompanyJob savedcompanyjob = companyjobrepo.save(companyjob);
		return CompanyJobdtoMapper.mapToCompanyJobDto(savedcompanyjob); 
		}
	
     
    public Optional<CompanyJobDto> getCompanyJobById(String companyJobId) {
    	    	CompanyJob companyjob = this.companyjobrepo.findById(companyJobId)
    	    			.orElseThrow(() -> new CustomException("company not found with id: " + companyJobId));
    	        
    	    	return Optional.of(CompanyJobdtoMapper.mapToCompanyJobDto(companyjob));

    	    }
      
	public List<CompanyJobDto> getAllJobs() {
	    List<CompanyJob> companyjobs = companyjobrepo.findAll();
	    return companyjobs.stream().map(companyjob -> CompanyJobdtoMapper.mapToCompanyJobDto(companyjob))
	                      .collect(Collectors.toList());
	}

	
	public void deleteByJobId(String JobId) {
		companyjobrepo.deleteById(JobId);
		}
	
	
	
	public int getApplicantsCount() {
		int ApplicantsCount=0;
		
		List<CompanyJob> companyJobs = companyjobrepo.findAll();
		
		for (CompanyJob companyJob : companyJobs) {
	        if (companyJob.getStatus()) {  // Assuming getStatus() returns a boolean for active status
	        	ApplicantsCount+=companyJob.getApplicantStatus().size();
	        }
	    }
		
		
		return ApplicantsCount;
		}
	
	
	public int getCountOfActiveJobs() {
	    int ActiveJobscount = 0;  // Initialize the count variable

	    // Fetch all company jobs
	    List<CompanyJob> companyJobs = companyjobrepo.findAll();

	    // Loop through each CompanyJob and check if it's active
	    for (CompanyJob companyJob : companyJobs) {
	        if (companyJob.getStatus()) {  // Assuming getStatus() returns a boolean for active status
	        	ActiveJobscount++;
	        }
	    }

	    return ActiveJobscount;
	}
	
	public String changeJobSeekerJobStatus(String companyjobid, Long id, JobStatus changedstatus) {
		
		CompanyJob companyjob = this.companyjobrepo.findById(companyjobid)
				.orElseThrow(() -> new CustomException("companyjob not found with id: " + companyjobid));
		
		JobSeeker jobseeker = this.jobseekerrepo.findById(id)
				.orElseThrow(() -> new CustomException("jobseeker not found with id: " + id));
		
		Map<CompanyJob,JobStatus> jobsmap = jobseeker.getAppliedJobStatus();
		
		for (Map.Entry<CompanyJob, JobStatus> entry : jobsmap.entrySet()) {
		    CompanyJob companyJob = entry.getKey();
		   // String status = entry.getValue();

		    if (companyJob.getJobId().equals(companyjobid)) {
		    	entry.setValue(changedstatus);
		    	jobseekerrepo.save(jobseeker);
		    }
		}
		
        Map<JobSeeker,JobStatus> companyjobmap = companyjob.getApplicantStatus();
		
		for (Map.Entry<JobSeeker, JobStatus> entry : companyjobmap.entrySet()) {
		   jobseeker= entry.getKey();
		   // String status = entry.getValue();

		    if (jobseeker.getId().equals(id)) {
		    	entry.setValue(changedstatus);
		    	companyjobrepo.save(companyjob);
		    }
		}
		return "changed status";
		
				
		
	}
	
	public List<JobSeeker> FilterData(Long Experience, String companyjobid) throws IOException{
		
		List<JobSeeker> jobseekers  =new ArrayList<>() ;
		
		CompanyJob companyjob = this.companyjobrepo.findById(companyjobid)
				.orElseThrow(() -> new CustomException("companyjob not found with id: " + companyjobid));
		
        Map<JobSeeker,JobStatus> applicantsmap = companyjob.getApplicantStatus();
		
		for (Map.Entry<JobSeeker, JobStatus> entry : applicantsmap.entrySet()) {
			JobSeeker jobseeker = entry.getKey();
		   // String status = entry.getValue();

		    if (jobseeker.getTotalExperience() >= Experience) {
		    	
		    	jobseekers.add(jobseeker);
		    }
		}
		String filePath = "C:/Users/SESPL/Downloads/company_jobs.csv";
		exportShortListedToCSV(jobseekers, filePath);
		return jobseekers;
		
		
	}
	
	public static void exportShortListedToCSV(List<JobSeeker> jobSeekers, String filePath) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            // Write header
            writer.println("JobId,JobTitle,JobDescription");

            // Write data rows
            for (JobSeeker user : jobSeekers) {
                writer.printf("%s,%s,%s%n",
                   user.getName(),
                   user.getEmail(),
                   user.getQualification()
                
                );
            }

            System.out.println("CSV file created successfully at " + filePath);
        } catch (IOException e) {
            System.err.println("Error writing CSV file: " + e.getMessage());
        }
    }

	
	
}