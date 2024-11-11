package com.jobs.bitlabs.controller;

import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.Operation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import com.jobs.bitlabs.dto.CompanyProfileDto;  
import com.jobs.bitlabs.service.CompanyProfileService;
import java.io.IOException;
import java.util.Optional;

@RestController
@RequestMapping("bitlabs.com")
public class CompanyProfileController {

    private final CompanyProfileService companyProfileService;

    @Autowired
    public CompanyProfileController(CompanyProfileService companyProfileService) {
        this.companyProfileService = companyProfileService;
    }

    @Operation(summary = "Create a new Company Profile")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "201", description = "Company Profile created",
                    content = @Content(schema = @Schema(implementation = CompanyProfileDto.class))),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @PostMapping(value = "/createProfile",consumes = {"multipart/form-data"})
    public ResponseEntity<CompanyProfileDto> createCompanyProfile(
            @RequestParam String companyId,
            @RequestParam String recruiterName,
            @RequestParam String companyName,
            @RequestParam String companyAddress, 
            @RequestParam Long companyNumber,
            @RequestParam("logo") MultipartFile logo) {

        try {
            // Ensure your CompanyProfileDto constructor matches the provided parameters
            CompanyProfileDto companyProfileDto = new CompanyProfileDto(companyId, logo.getBytes(), companyName, recruiterName, companyAddress, companyNumber);
            CompanyProfileDto savedProfile = companyProfileService.saveCompanyProfile(companyProfileDto);
            return new ResponseEntity<>(savedProfile, HttpStatus.CREATED);
        } catch (IOException e) {
            // Optional: Add logging here to track the error
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @Operation(summary = "Get a Company Profile by ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Found the Company Profile",
                    content = @Content(schema = @Schema(implementation = CompanyProfileDto.class))),
            @ApiResponse(responseCode = "404", description = "Company Profile not found")
    })
    @GetMapping("/getCompanyProfileById")
    public ResponseEntity<CompanyProfileDto> getCompanyProfile(@RequestParam String companyId) {
        Optional<CompanyProfileDto> companyProfileDto = companyProfileService.getCompanyProfileById(companyId);
        return companyProfileDto.map(ResponseEntity::ok).orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    @Operation(summary = "Delete a Company Profile by ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "204", description = "Company Profile deleted"),
            @ApiResponse(responseCode = "404", description = "Company Profile not found")
    })
    @DeleteMapping("deleteCompanyProfileById")
    public ResponseEntity<Void> deleteCompanyProfile(@RequestParam String companyId) {
        companyProfileService.deleteCompanyProfile(companyId);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
