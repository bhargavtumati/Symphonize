package com.jobs.bitlabs;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

import com.jobs.bitlabs.dto.CompanyProfileDto;
import com.jobs.bitlabs.entity.CompanyProfile;
import com.jobs.bitlabs.exception.CustomException;
import com.jobs.bitlabs.repo.CompanyProfileRepository;
import com.jobs.bitlabs.service.CompanyProfileServiceImpl;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

class CompanyProfileServiceImplTest {

    @Mock
    private CompanyProfileRepository companyProfileRepository;

    @InjectMocks
    private CompanyProfileServiceImpl companyProfileService;

    private CompanyProfileDto companyProfileDto;
    private CompanyProfile companyProfile;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this); // Initialize mock objects

        // Sample data for the test
        companyProfileDto = new CompanyProfileDto("123", new byte[0], "ABC Corp", "John Doe", null, 1234567890L);
        companyProfile = new CompanyProfile();
        companyProfile.setCompanyId("123");
        companyProfile.setCompanyName("ABC Corp");
        companyProfile.setRecruiterName("John Doe");
        companyProfile.setCompanyNumber(1234567890L);
    }

    @Test
    void saveCompanyProfile_ShouldSaveSuccessfully_WhenValid() {
        // Arrange: Mock repository behavior
        when(companyProfileRepository.existsById(companyProfileDto.getCompanyId())).thenReturn(false); // Mocking repository method

        when(companyProfileRepository.save(any(CompanyProfile.class))).thenReturn(companyProfile); // Save mock

        // Act: Call the method to test
        CompanyProfileDto result = companyProfileService.saveCompanyProfile(companyProfileDto);

        // Assert: Verify the expected result
        assertNotNull(result);
        assertEquals(companyProfileDto.getCompanyId(), result.getCompanyId());
        verify(companyProfileRepository, times(1)).save(any(CompanyProfile.class)); // Verifying save method was called
    }

    @Test
    void saveCompanyProfile_ShouldThrowCustomException_WhenCompanyIdContainsSpecialCharacters() {
        // Arrange: Modify the input to have special characters in Company ID
        CompanyProfileDto invalidCompanyProfileDto = new CompanyProfileDto("123@!", new byte[0], "ABC Corp", "John Doe", null, 1234567890L);

        // Act & Assert: Verify that the exception is thrown
        CustomException thrown = assertThrows(CustomException.class, () -> {
            companyProfileService.saveCompanyProfile(invalidCompanyProfileDto);
        });
        assertEquals("Company ID contains special characters: 123@!", thrown.getMessage());
    }

    @Test
    void saveCompanyProfile_ShouldThrowCustomException_WhenCompanyIdAlreadyExists() {
        // Arrange: Mock repository to return that companyId already exists
        when(companyProfileRepository.existsById(companyProfileDto.getCompanyId())).thenReturn(true);

        // Act & Assert: Verify that the exception is thrown
        CustomException thrown = assertThrows(CustomException.class, () -> {
            companyProfileService.saveCompanyProfile(companyProfileDto);
        });
        assertEquals("Company ID already exists: 123", thrown.getMessage());
    }
}
