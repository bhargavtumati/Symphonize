package com.jobs.bitlabs.controller;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.dto.CompanyprofileDtoMapper;
import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.repo.CompanyProfileRepo;
import com.jobs.bitlabs.service.CompanyProfileService;
import com.jobs.bitlabs.service.FileServices;



import io.swagger.v3.oas.annotations.parameters.RequestBody;

import jakarta.persistence.EntityNotFoundException;

@RestController
@RequestMapping("bitlabs.com/companyProfile")
public class CompanyProfileController {

    @Autowired
    private CompanyProfileService companyProfileService;
    
    @Autowired
    private FileServices fileservices;
    
    @Autowired
    private CompanyProfileRepo companyProfileRepo;

    @Value("${upload.dir}")
    private String uploadDir;

    /* @Operation(summary = "Create a new Company Profile")
   @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Profile created successfully", 
                     content = { @Content(mediaType = "application/json", 
                     schema = @Schema(implementation = CompanyProfileDto.class)) }),
        @ApiResponse(responseCode = "500", description = "Internal server error", 
                     content = @Content) 
    })*/
    @PostMapping(value = "/createProfile")
    public ResponseEntity<CompanyProfileDto> createCompanyProfile( @RequestBody CompanyProfileDto companyProfileDto)  {
        // Handle the upload and save logic
    
        CompanyProfileDto createdProfile = companyProfileService.createCompanyProfile( companyProfileDto);
        return ResponseEntity.ok(createdProfile);
    }
    
    

	@PostMapping("/profile/{postId}")
	public ResponseEntity<CompanyProfileDto> uploadPostImage(@RequestParam("image") MultipartFile image,
			@PathVariable String CompanyProfileId) throws IOException {

		Optional<CompanyProfile> optionalcompanyprofile = companyProfileRepo.findById(CompanyProfileId);
				//getById(companyprofiledto.getCompanyId());
		
	

		
		if (optionalcompanyprofile.isPresent()) {
			
			CompanyProfile companyprofile = optionalcompanyprofile.get();
			String fileName = this.fileservices.uploadImage(uploadDir, image);
			companyprofile.setProfileImage(fileName);
			
			CompanyProfile savedcompanyprofile = companyProfileRepo.save(companyprofile);
			CompanyProfileDto savedcompanydto = CompanyprofileDtoMapper.mapToCompanyProfileDto(savedcompanyprofile);
			return ResponseEntity.ok(savedcompanydto);
		}
		else {
			throw new EntityNotFoundException("Post Not Found");
		}
	}
	
   // @Operation(summary = "Get all Company Profiles")
    @GetMapping("getAllCompanyProfiles")
    public List<CompanyProfileDto> getAllCompanyProfiles() {
        return companyProfileService.getAllCompanyProfiles();
    }

   // @Operation(summary = "Delete a Company Profile")
   // @ApiResponses(value = {
   //     @ApiResponse(responseCode = "200", description = "Profile deleted successfully"),
   //     @ApiResponse(responseCode = "404", description = "Profile not found")
  //  })
    @DeleteMapping("/deleteCompanyProfile/{companyId}")
    public ResponseEntity<String> deleteCompanyProfile(@PathVariable("companyId") String companyId) {
        return ResponseEntity.ok(companyProfileService.deleteCompanyProfile(companyId));
    }
}
