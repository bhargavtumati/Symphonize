package com.jobs.bitlabs;

import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.repo.CompanyProfileRepo;
import com.jobs.bitlabs.service.CompanyprofileServiceImpl;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import java.util.Date;

@ExtendWith(MockitoExtension.class)
public class CompanyProfileServiceTest {

    @Mock
    private CompanyProfileRepo companyProfileRepository;

    @InjectMocks
    private CompanyprofileServiceImpl companyProfileService; // Use the concrete implementation

    @Test
    void testCreateCompanyProfile() {
        // Create a mock CompanyProfile
        CompanyProfile mockProfile = new CompanyProfile();
        mockProfile.setCompanyId("uniquestring123");
        mockProfile.setCompanyName("Test Company");
        mockProfile.setCompanyMail("test@company.com");
        mockProfile.setRecuriterName("Test Recruiter");
        mockProfile.setCompanyMobileNumber(1234567890L);
        mockProfile.setCompanyAddress("3rd Floor, Sai Odyssey NH9 Service Road, Guru Nanak Colony, Vijayawada, Andhra Pradesh 520008");
        mockProfile.setRegisteredDate(new Date());

        // Define the behavior of the mock repository
        when(companyProfileRepository.save(any(CompanyProfile.class))).thenReturn(mockProfile);

        // Call the service method
        CompanyProfile createdProfile = companyProfileService.createCompanyProfile(mockProfile);

        // Verify the result
        assertThat(createdProfile).isNotNull();
        assertThat(createdProfile.getCompanyId()).isEqualTo("uniquestring123");
        assertThat(createdProfile.getCompanyName()).isEqualTo("Test Company");
        assertThat(createdProfile.getCompanyMail()).isEqualTo("test@company.com");
        assertThat(createdProfile.getRecruiterName()).isEqualTo("Test Recruiter");
        assertThat(createdProfile.getCompanyMobileNumber()).isEqualTo(1234567890L);
        assertThat(createdProfile.getCompanyAddress()).isEqualTo("3rd Floor, Sai Odyssey NH9 Service Road, Guru Nanak Colony, Vijayawada, Andhra Pradesh 520008");
        assertThat(createdProfile.getRegisteredDate()).isNotNull();
    }
}
