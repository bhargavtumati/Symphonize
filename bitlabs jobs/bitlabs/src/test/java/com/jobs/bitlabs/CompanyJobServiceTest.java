package com.jobs.bitlabs;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import static org.mockito.ArgumentMatchers.any;

import com.jobs.bitlabs.dto.CompanyJobDto;
import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.entity.CompanyJob;
import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.entity.JobSeeker;
import com.jobs.bitlabs.repo.CompanyJobRepo;
import com.jobs.bitlabs.repo.CompanyProfileRepo;
import com.jobs.bitlabs.service.CompanyJobServiceImpl;
import com.jobs.bitlabs.service.CompanyProfileServiceImpl;
import com.jobs.bitlabs.enums.Qualification;
import com.jobs.bitlabs.enums.JobStatus;
import com.jobs.bitlabs.enums.PrefferedLocation;
import com.jobs.bitlabs.enums.Skills;

public class CompanyJobServiceTest {

    @Mock
    private CompanyJobRepo companyjobrepo;

    @Mock
    private CompanyProfileRepo companyprofilerepo;

    @InjectMocks
    private CompanyJobServiceImpl companyjobserviceimpl;

    @InjectMocks
    private CompanyProfileServiceImpl companyprofileserviceimpl;

    private CompanyJobDto companyjobdto;
    private CompanyJob companyjob;
    private CompanyProfileDto companyProfileDto;
    private CompanyProfile companyProfile;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);

        // Initialize CompanyProfileDto and CompanyProfile
       companyProfileDto = new CompanyProfileDto("SYMPHONIZE", new byte[0], "ABC Corp", "John Doe", null, 1234567890L);
        companyProfile = new CompanyProfile();
        companyProfile.setCompanyId("SYMPHONIZE");
        companyProfile.setCompanyName("ABC Corp");
        companyProfile.setRecruiterName("John Doe");
        companyProfile.setCompanyNumber(1234567890L);

        // Initialize CompanyJobDto and CompanyJob
        Set<Skills> skillsSet = new HashSet<>();
        skillsSet.add(Skills.JAVA);

        Set<PrefferedLocation> preferredLocation = new HashSet<>();
        preferredLocation.add(PrefferedLocation.Bangalore);

        Map<JobSeeker, JobStatus> maplist = new HashMap<>();

        companyjobdto = new CompanyJobDto(
            "GAD24",
            "JAVA DEVELOPER",
            "WE ARE LOOKING FOR A JAVA DEVELOPER WITH STRONG FOUNDATIONS",
            new Date(),
            "SYMPHONIZE",
            Qualification.BTECH,
            2L,
            3L,
            skillsSet,
            3L,
            6L,
            preferredLocation,
            "WFO and Full-Time",
            false
        );

        companyjob = new CompanyJob(
            "GAD24",
            "JAVA DEVELOPER",
            "WE ARE LOOKING FOR A JAVA DEVELOPER WITH STRONG FOUNDATIONS",
            new Date(),
            "SYMPHONIZE",
            Qualification.BTECH,
            2L,
            3L,
            skillsSet,
            3L,
            6L,
            preferredLocation,
            "WFO and Full-Time",
            false,
            maplist
        );
    }

   
    @Test
    void saveCompanyJob_ShouldSaveSuccessfully_WhenValid() {
        // Mock behavior for checking if the company exists
        when(companyprofilerepo.existsById(companyProfileDto.getCompanyId())).thenReturn(true);

        // Mock behavior for saving CompanyJob
        when(companyjobrepo.existsById(companyjobdto.getJobId())).thenReturn(false);
        when(companyjobrepo.save(any(CompanyJob.class))).thenReturn(companyjob);

        // Call the method under test
        CompanyJobDto savedJob = companyjobserviceimpl.postJob(companyjobdto);

        // Assertions
        assertNotNull(savedJob);
        assertEquals(companyjobdto.getJobId(), savedJob.getJobId());

        // Verify interactions
        verify(companyprofilerepo, times(1)).existsById(companyProfileDto.getCompanyId());
        verify(companyjobrepo, times(1)).save(any(CompanyJob.class));
    }

}
